#!/usr/bin/env bash
# Full post-deployment verification. Slower and stricter than health_check.sh:
# run it once after a deployment, not on a schedule.
#
# Every check knows what "correct but empty" looks like. On this platform an empty
# panel is often the right answer — 43 of 45 businesses have no skill edge, no
# scheme has a district edge — and a verifier that cannot tell a documented data
# gap from a broken deployment is worse than none.
#
# Exit: 0 verified · 1 verified with known gaps · 2 failed
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
cd "$VW_ROOT"
need_cmd psql python3
need_env DATABASE_URL

FAILURES=0
check() {  # check <label> <actual> <expected>
  if [[ "$2" == "$3" ]]; then ok "$1: $2"; else
    printf '    %s✗ %s: got %s, expected %s%s\n' "$C_RED" "$1" "${2:-nothing}" "$3" "$C_RESET" >&2
    FAILURES=$((FAILURES + 1))
  fi
}

step "1 · Schema"
check "tables total" "$(psql_scalar "select count(*) from pg_tables where schemaname in ('public','knowledge','user_intelligence');")" "51"
check "knowledge tables" "$(psql_scalar "select count(*) from pg_tables where schemaname='knowledge';")" "10"
check "user_intelligence tables" "$(psql_scalar "select count(*) from pg_tables where schemaname='user_intelligence';")" "5"
check "tables without RLS" "$(psql_scalar "select count(*) from pg_tables where schemaname in ('public','knowledge','user_intelligence') and rowsecurity=false;")" "0"

step "2 · Migration 011 repair"
check "vocabulary table in knowledge" "$(psql_scalar "select to_regclass('knowledge.kg_vocabulary_map') is not null;")" "t"
check "no unbuildable foreign key" "$(psql_scalar "select count(*) from pg_constraint where conrelid='knowledge.kg_vocabulary_map'::regclass and contype='f';")" "0"

step "3 · Crosswalk loaded"
check "crosswalk rows" "$(psql_scalar "select count(*) from knowledge.kg_vocabulary_map;")" "202"
check "districts" "$(psql_scalar "select count(*) from knowledge.kg_vocabulary_map where term_kind='district';")" "33"
check "skills" "$(psql_scalar "select count(*) from knowledge.kg_vocabulary_map where term_kind='skill';")" "147"
check "resolution coherent" "$(psql_scalar "select count(*) from knowledge.kg_vocabulary_map where (match_method='NO_COUNTERPART') <> (global_entity_id is null);")" "0"

step "4 · Knowledge synced"
for pair in "kg_entities 647" "kg_relationships 865" "kg_districts 61" "kg_skills 45" \
            "kg_schemes 40" "kg_businesses 85" "kg_industries 24" "kg_agriculture 45"; do
  set -- $pair
  check "$1" "$(psql_scalar "select count(*) from knowledge.$1 where sync_deleted_at is null;")" "$2"
done

step "5 · Dashboard data available"
recs=$(psql_scalar "select count(*) from user_intelligence.user_recommendations;")
users=$(psql_scalar "select count(distinct user_id) from user_intelligence.user_activity_summary;")
if [[ "${users:-0}" == "0" ]]; then
  warn "no user intelligence computed — /dashboard will show NOT_COMPUTED for every user.
         Correct only if run_user_intelligence.sh has not been run yet."
else
  ok "intelligence: $users user(s), $recs recommendation(s)"
  check "dangling recommendations" "$(psql_scalar "
    select count(*) from user_intelligence.user_recommendations ur
     where ur.item_id like 'vw:%' and not exists (
       select 1 from knowledge.kg_entities e where e.global_entity_id = ur.item_id);")" "0"
fi

step "6 · Search returns results"
hits=$(psql_scalar "select count(*) from knowledge.kg_entities where sync_deleted_at is null and canonical_name ilike '%weld%';")
[[ "${hits:-0}" -gt 0 ]] 2>/dev/null && ok "search for 'weld': $hits result(s)" \
  || { printf '    %s✗ search returned nothing for a term known to exist%s\n' "$C_RED" "$C_RESET" >&2
       FAILURES=$((FAILURES + 1)); }

step "7 · Recommendations reachable — the connected-graph check"
# One representative traversal per detail page type. These are the joins the UI
# performs; if they return nothing, pages render but say nothing.
biz_skill=$(psql_scalar "select count(*) from knowledge.kg_relationships where relationship_type='REQUIRES_SKILL' and sync_deleted_at is null;")
ok "REQUIRES_SKILL edges: ${biz_skill:-0}"
scheme_district=$(psql_scalar "select count(*) from knowledge.kg_relationships r join knowledge.kg_entities a on a.global_entity_id=r.from_entity join knowledge.kg_entities b on b.global_entity_id=r.to_entity where a.entity_type='GovernmentScheme' and b.entity_type='District';")
if [[ "${scheme_district:-0}" == "0" ]]; then
  warn "0 scheme->district edges — RS2-VIA_DISTRICT cannot fire. KNOWN GAP, not a deployment failure (Phase 2 R1 recovers 305)."
else
  ok "scheme->district edges: $scheme_district"
fi

step "8 · Routes"
if [[ -n "${PRODUCTION_URL:-}" ]] && command -v curl >/dev/null 2>&1; then
  for path in / /knowledge /signin; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 "${PRODUCTION_URL%/}$path" || echo 000)
    [[ "$code" == "200" ]] && ok "$path -> 200" \
      || { printf '    %s✗ %s -> %s%s\n' "$C_RED" "$path" "$code" "$C_RESET" >&2; FAILURES=$((FAILURES+1)); }
  done
else
  warn "PRODUCTION_URL not set — route checks skipped"
fi

printf '\n'
if ((FAILURES)); then
  printf '%sVerification FAILED: %d check(s).%s\n' "$C_RED" "$FAILURES" "$C_RESET" >&2
  exit 2
fi
if ((VW_WARNINGS)); then
  printf '%sVerified with %d known gap(s). See POST_DEPLOYMENT_VALIDATION.md §11.%s\n' \
    "$C_YELLOW" "$VW_WARNINGS" "$C_RESET"
  exit 1
fi
printf '%sDeployment verified.%s\n' "$C_GREEN" "$C_RESET"
