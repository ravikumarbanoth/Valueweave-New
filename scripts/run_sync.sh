#!/usr/bin/env bash
# Project the knowledge graph into Supabase.
#
# Always plans first, and refuses to apply when the plan reports errors or an
# unexpected number of warnings. Four V6-OWNERSHIP warnings are declared and
# governed by ADR-005; a fifth means something changed that a person should read.
#
#   ./scripts/run_sync.sh                 plan, then apply
#   ./scripts/run_sync.sh --plan-only     plan, change nothing
#   ./scripts/run_sync.sh --full          ignore the manifest, rewrite every row
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
cd "$VW_ROOT"
need_cmd python3

PLAN_ONLY=0; FULL=""
for a in "$@"; do
  case "$a" in
    --plan-only) PLAN_ONLY=1 ;;
    --full) FULL="--full" ;;
    *) fail "unknown argument: $a" ;;
  esac
done

EXPECTED_WARNINGS=4
EXPECTED_ROWS=1812

step "Checking generated DDL against the specs"
python3 knowledge_sync/generate_migration.py --check | sed 's/^/    /' \
  || fail "the committed migration no longer matches TABLE_SPECS — regenerate it"

step "Planning (no credentials needed, writes nothing)"
python3 -m knowledge_sync plan > /tmp/vw_sync_plan.log 2>&1 || {
  cat /tmp/vw_sync_plan.log; fail "plan failed"; }
grep -E "extract |validate |insert=" /tmp/vw_sync_plan.log | sed 's/^/    /'

errors=$(grep -oE "validate   [0-9]+ error" /tmp/vw_sync_plan.log | grep -oE "[0-9]+" || echo 0)
warns=$(grep -oE "[0-9]+ warning" /tmp/vw_sync_plan.log | grep -oE "[0-9]+" | head -1 || echo 0)

[[ "${errors:-0}" == "0" ]] || fail "$errors validation error(s). Fix the package, not the sync."
if [[ "${warns:-0}" == "$EXPECTED_WARNINGS" ]]; then
  ok "$EXPECTED_WARNINGS governed warnings (ADR-005) — expected"
else
  fail "expected $EXPECTED_WARNINGS warnings, got ${warns:-0}.
    An unexpected warning means an undeclared cross-package overlap. Read
    the plan above before applying."
fi

# A large delete count is almost never retired facts — it is a renamed dataset or
# a changed key column. Stopping here has caught more mistakes than any other check.
deletes=$(grep -oE "delete=[0-9]+" /tmp/vw_sync_plan.log | grep -oE "[0-9]+" \
          | awk '{s+=$1} END {print s+0}')
if [[ "$deletes" -gt 50 ]]; then
  warn "$deletes row(s) would be soft-deleted. Usually a renamed dataset, not retired facts."
  confirm "Continue with $deletes deletions?"
fi

if ((PLAN_ONLY)); then summary "Sync plan"; exit 0; fi

need_env SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY

# Do the tables exist? Nothing checked, and the failure without this is a raw
# PostgREST error surfacing through the SDK — technically accurate and useless
# for working out that the migrations were never run.
#
# Skipped rather than failed when DATABASE_URL is absent: the sync itself writes
# over the REST API and does not need a Postgres connection, so requiring one
# here would break a legitimate way to run this script.
if [[ -n "${DATABASE_URL:-}" ]] && command -v psql >/dev/null 2>&1; then
  step "Checking the target tables exist"
  missing=""
  for tbl in kg_entities kg_relationships kg_districts kg_skills \
             kg_schemes kg_businesses kg_industries kg_agriculture; do
    present=$(psql_scalar "select to_regclass('knowledge.$tbl') is not null;")
    [[ "$present" == "t" ]] || missing="$missing $tbl"
  done
  if [[ -n "$missing" ]]; then
    fail "the knowledge schema is missing these tables:$missing
    The migrations have not been applied to this database. Run
    ./scripts/first_deploy.sh — it applies them in order, expects 009 to fail,
    and repairs it with 011. Nothing here can create them."
  fi
  ok "all 8 target tables present"
else
  info "no DATABASE_URL or psql — skipping the table check; a missing table will
    surface as a PostgREST error during apply"
fi

step "Applying${FULL:+ (full rebuild)}"
run python3 -m knowledge_sync --target supabase sync $FULL | tail -6 | sed 's/^/    /'

step "Proving idempotency — the check that matters"
if [[ "$DRY_RUN" == "1" ]]; then
  info "[dry-run] would re-run sync and require 0 inserted, 0 updated"
  summary "Sync (dry run)"; exit 0
fi
python3 -m knowledge_sync --target supabase sync > /tmp/vw_sync_second.log 2>&1
second=$(grep -oE "[0-9]+ inserted, [0-9]+ updated" /tmp/vw_sync_second.log | tail -1)
info "second run: ${second:-unknown}"
if [[ "$second" == "0 inserted, 0 updated" ]]; then
  ok "sync is idempotent"
else
  fail "the second run reported '$second' on unchanged input.
    A value round-trips differently through Postgres than through the content
    hash. Diagnose before putting the sync on a schedule."
fi

step "Verifying row counts"
actual=$(psql_scalar "select count(*) from knowledge.kg_entities;")
info "knowledge.kg_entities: ${actual:-unreadable} (expected 647)"
[[ "${actual:-0}" == "647" ]] && ok "entity count correct" \
  || warn "entity count is ${actual:-unreadable}, expected 647"

summary "Knowledge sync"
