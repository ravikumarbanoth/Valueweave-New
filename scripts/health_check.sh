#!/usr/bin/env bash
# Continuous health check. Safe to run every 5 minutes from cron or a monitor.
#
# THE ONE THING THIS EXISTS FOR
# -----------------------------
# The platform's worst failure is silent. If the `knowledge` schema is not exposed,
# every query fails, safe() in lib/knowledge.js returns [], and the app serves 200s
# with empty panels. No error rate moves. Uptime monitoring reports healthy.
#
# So this checks through the ANON key, not the service role — a health check that
# cannot fail the way production fails is worse than none.
#
# One correction to an earlier version of this comment, because it changes the
# order of a deployment: the service role does NOT bypass the exposed-schemas
# setting. That setting is PostgREST's `db-schemas` allowlist, and PostgREST
# validates the requested schema against it before it authenticates anything —
# an unlisted schema returns PGRST106 whichever key is presented. It is a server
# configuration, not a permission, so there is no key that can route around it.
#
# The practical consequence: `knowledge` must be exposed BEFORE the sync runs,
# not after. The sync writes through PostgREST too (SupabaseTarget calls
# client.schema(...) — see knowledge_sync/adapters.py), so an unexposed schema
# fails the import, not merely the browser.
#
# What the service role does bypass is RLS, which is why a service-role read
# would still be the wrong check here: it would sail past the read policies that
# a real visitor has to satisfy.
#
# EXIT CODES, AND WHY THE DEFAULT CHANGED
# ---------------------------------------
# This used to exit 1 on any warning. That is the right contract for a monitor,
# which wants to know the moment anything degrades, and the wrong one for a
# deployment gate, which is what the GitHub workflow uses it as.
#
# The consequence was a green deployment reported as a failed run: 1,812 records
# synced, 202 crosswalk rows loaded, four checks OK, zero critical — and exit 1,
# because PRODUCTION_URL was unset and user_intelligence had not been computed
# yet. Neither of those means the deployment is broken. A CI job that goes red
# when nothing is wrong teaches everyone to ignore it, and then it cannot report
# the failure that matters.
#
# So the default is now: only CRITICAL fails. Warnings are printed exactly as
# before, counted in the summary, and carried in the JSON — they are just no
# longer fatal.
#
#   0  no critical findings (warnings may be present and are reported)
#   1  warnings, and only with --strict
#   2  at least one critical finding — always, in either mode
#
#   ./scripts/health_check.sh                human-readable, warnings tolerated
#   ./scripts/health_check.sh --strict       warnings fail too (monitors, gates)
#   ./scripts/health_check.sh --json         one object, for a monitor
#   ./scripts/health_check.sh --json --strict
#
# `VW_HEALTH_STRICT=1` does the same as --strict, for callers that set
# environment rather than arguments.
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
cd "$VW_ROOT"

JSON=0
STRICT="${VW_HEALTH_STRICT:-0}"

# A loop, not `[[ $1 == --json ]]`. The old form read only the first argument,
# so `--json --strict` would have honoured the first and dropped the second
# without saying so. An unknown flag is an error for the same reason: a typo
# like `--stict` must not quietly leave strict mode off.
while (($#)); do
  case "$1" in
    --json)   JSON=1 ;;
    --strict) STRICT=1 ;;
    -h|--help)
      sed -n '2,/^source /p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//;$d'
      exit 0 ;;
    *) printf 'health_check.sh: unknown option %s\n' "$1" >&2; exit 64 ;;
  esac
  shift
done

CRITICAL=0
declare -a FINDINGS=()

# severity|check|detail. Detail is collapsed to one line: findings are parsed
# line-by-line in --json mode, and a multi-line message would split into two
# malformed records.
record() {
  local detail
  detail="$(printf '%s' "$3" | tr '\n' ' ' | tr -s ' ')"
  FINDINGS+=("$1|$2|$detail")
}

# ── 1 · direct database reachability (service role or direct URL) ──────────
ENTITIES=""; EDGES=""; VOCAB=""; UI_USERS=""; UI_RECS=""
if [[ -n "${DATABASE_URL:-}" ]] && command -v psql >/dev/null 2>&1; then
  ENTITIES=$(psql_scalar "select count(*) from knowledge.kg_entities;")
  EDGES=$(psql_scalar "select count(*) from knowledge.kg_relationships;")
  VOCAB=$(psql_scalar "select count(*) from knowledge.kg_vocabulary_map;")
  UI_USERS=$(psql_scalar "select count(distinct user_id) from user_intelligence.user_activity_summary;")
  UI_RECS=$(psql_scalar "select count(*) from user_intelligence.user_recommendations;")

  [[ -n "$ENTITIES" ]] || { record CRITICAL knowledge_schema "knowledge.kg_entities unreadable — schema missing or dropped"; CRITICAL=1; }
  [[ "${ENTITIES:-0}" -ge 647 ]] 2>/dev/null && record OK knowledge_synced "$ENTITIES entities" \
    || { [[ "${ENTITIES:-0}" == "0" ]] && { record CRITICAL knowledge_synced "0 entities — sync has never run"; CRITICAL=1; } \
         || record WARN knowledge_synced "${ENTITIES:-?} entities, expected 647 — partial sync"; }
  [[ "${EDGES:-0}" -ge 865 ]] 2>/dev/null && record OK graph_edges "$EDGES relationships" \
    || record WARN graph_edges "${EDGES:-?} relationships, expected 865"
  [[ "${VOCAB:-0}" == "202" ]] && record OK crosswalk_loaded "202 crosswalk rows" \
    || { [[ "${VOCAB:-0}" == "0" ]] && record CRITICAL crosswalk_loaded "0 rows — nothing will resolve" && CRITICAL=1 \
         || record WARN crosswalk_loaded "${VOCAB:-?} rows, expected 202"; }
  [[ "${UI_USERS:-0}" -gt 0 ]] 2>/dev/null && record OK intelligence_populated "$UI_USERS user(s), $UI_RECS recommendation(s)" \
    || record WARN intelligence_populated "0 users — run scripts/run_user_intelligence.sh --apply"

  # Recommendations pointing at entities the projection no longer holds. Expected
  # zero; anything else means intelligence was computed against an older graph.
  DANGLING=$(psql_scalar "
    select count(*) from user_intelligence.user_recommendations ur
     where ur.item_id like 'vw:%'
       and not exists (select 1 from knowledge.kg_entities e
                        where e.global_entity_id = ur.item_id);")
  [[ "${DANGLING:-0}" == "0" ]] && record OK recommendation_integrity "no dangling recommendations" \
    || record WARN recommendation_integrity "${DANGLING} recommendation(s) point at missing entities — recompute after a full sync"
else
  record WARN database "DATABASE_URL or psql unavailable — database checks skipped"
fi

# ── 2 · schema exposure, through the anon key: the silent failure ──────────
if [[ -n "${NEXT_PUBLIC_SUPABASE_URL:-}" && -n "${NEXT_PUBLIC_SUPABASE_ANON_KEY:-}" ]] \
   && command -v curl >/dev/null 2>&1; then
  # Normalised the same way as the workflow's exposure preflight, and for the
  # same reason: a trailing slash or a /rest/v1 already in the secret produces
  # "//rest/v1/kg_entities", which PostgREST answers 404 + PGRST125 "Invalid
  # request URL". That is indistinguishable from "not exposed" in the case
  # below, so this check would report CRITICAL and send someone to the Exposed
  # schemas setting to fix a typo in an environment variable.
  base="$(printf '%s' "$NEXT_PUBLIC_SUPABASE_URL" | tr -d '\r\n' \
          | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
  base="${base%"${base##*[!/]}"}"
  case "$base" in */rest/v1) base="${base%/rest/v1}" ;; esac
  base="${base%"${base##*[!/]}"}"

  code=$(curl -s -o /tmp/vw_expose.json -w '%{http_code}' \
    -H "apikey: $NEXT_PUBLIC_SUPABASE_ANON_KEY" \
    -H "Authorization: Bearer $NEXT_PUBLIC_SUPABASE_ANON_KEY" \
    -H "Accept-Profile: knowledge" \
    "$base/rest/v1/kg_entities?select=global_entity_id&limit=1" || echo 000)
  if grep -q PGRST125 /tmp/vw_expose.json 2>/dev/null; then
    record CRITICAL schema_exposed "malformed request URL (PGRST125).
             NEXT_PUBLIC_SUPABASE_URL should be exactly https://<ref>.supabase.co
             — no trailing slash, no /rest/v1 suffix."
    code=handled
  fi
  case "$code" in
    handled) : ;;
    200) record OK schema_exposed "knowledge schema reachable by the anon key" ;;
    404|406) record CRITICAL schema_exposed "anon key cannot see the knowledge schema (HTTP $code).
             Add 'knowledge, user_intelligence' to API -> Exposed schemas.
             THIS IS THE FAILURE THAT PRODUCES NO ERROR ANYWHERE ELSE."; CRITICAL=1 ;;
    000) record WARN schema_exposed "could not reach Supabase from here" ;;
    *)   record WARN schema_exposed "unexpected HTTP $code" ;;
  esac
else
  record WARN schema_exposed "NEXT_PUBLIC_SUPABASE_* not set — exposure check skipped.
           This is the check most worth running; set them."
fi

# ── 3 · the site itself ────────────────────────────────────────────────────
if [[ -n "${PRODUCTION_URL:-}" ]] && command -v curl >/dev/null 2>&1; then
  for path in "/" "/knowledge"; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "${PRODUCTION_URL%/}$path" || echo 000)
    [[ "$code" == "200" ]] && record OK "route${path//\//_}" "$path -> 200" \
      || { record CRITICAL "route${path//\//_}" "$path -> HTTP $code"; CRITICAL=1; }
  done
else
  record WARN site "PRODUCTION_URL not set — route checks skipped"
fi

# ── report ─────────────────────────────────────────────────────────────────
warns=0; oks=0; crits=0
for f in "${FINDINGS[@]}"; do
  case "${f%%|*}" in OK) oks=$((oks+1));; WARN) warns=$((warns+1));; CRITICAL) crits=$((crits+1));; esac
done

if ((JSON)); then
  # Emitted by python3, not by shell string juggling: a monitor parses this, and
  # hand-rolled JSON that is subtly invalid fails at the worst moment.
  printf '%s\n' "${FINDINGS[@]}" | python3 -c '
import json, sys, datetime
findings = []
for line in sys.stdin:
    line = line.rstrip("\n")
    if not line:
        continue
    sev, name, detail = line.split("|", 2)
    findings.append({"severity": sev, "check": name,
                     "detail": " ".join(detail.split())})
crit = sum(f["severity"] == "CRITICAL" for f in findings)
warn = sum(f["severity"] == "WARN" for f in findings)
num = lambda v: int(v) if str(v).isdigit() else None
print(json.dumps({
    "status": "critical" if crit else ("degraded" if warn else "healthy"),
    "checked_at": datetime.datetime.now(datetime.timezone.utc)
                   .strftime("%Y-%m-%dT%H:%M:%SZ"),
    "entities": num(sys.argv[1]), "edges": num(sys.argv[2]),
    "crosswalk": num(sys.argv[3]), "intelligence_users": num(sys.argv[4]),
    "recommendations": num(sys.argv[5]),
    "ok": sum(f["severity"] == "OK" for f in findings),
    "warnings": warn, "critical": crit,
    # `status` is unchanged — a monitor still sees "degraded" on warnings.
    # What changed is the process exit code, so the two are reported
    # separately rather than the caller inferring one from the other.
    "strict": sys.argv[6] == "1",
    "exit_code": 2 if crit else (1 if (warn and sys.argv[6] == "1") else 0),
    "findings": findings,
}, indent=2))
' "${ENTITIES:-}" "${EDGES:-}" "${VOCAB:-}" "${UI_USERS:-}" "${UI_RECS:-}" "$STRICT"
else
  step "ValueWeave health check"
  for f in "${FINDINGS[@]}"; do
    IFS='|' read -r sev name detail <<< "$f"
    case "$sev" in
      OK) ok "$name: $detail" ;;
      WARN) warn "$name: $detail" ;;
      CRITICAL) printf '    %s✗ %s: %s%s\n' "$C_RED" "$name" "$detail" "$C_RESET" >&2 ;;
    esac
  done
  printf '\n  %d ok · %d warning(s) · %d critical\n' "$oks" "$warns" "$crits"
  # Not when something critical fired: the run DID fail, and saying warnings
  # are tolerated next to a red cross reads as though nothing went wrong.
  if ((warns)) && ! ((STRICT)) && ! ((crits)); then
    printf '  warnings do not fail this run — pass --strict to make them fatal\n'
  fi
fi

# Critical always fails, in either mode. Warnings fail only under --strict.
if ((crits)); then
  exit 2
fi
if ((warns)) && ((STRICT)); then
  exit 1
fi
exit 0
