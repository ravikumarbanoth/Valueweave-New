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

# THE EXPECTED ROW COUNT IS READ, NOT WRITTEN DOWN
# ------------------------------------------------
# It was `EXPECTED_ROWS=1812` and `expected 647`, hard-coded. That was correct
# on the day it was written and wrong the first time the collection pipeline
# promoted anything: the first real end-to-end run added one scheme, the graph
# went to 648, and this script reported a warning for a knowledge base that had
# grown exactly as intended.
#
# A ratchet that fires on success is a ratchet people learn to ignore, and then
# it cannot report the row that went missing. So the number now comes from the
# graph the sync is about to project. What is still checked — and is the thing
# actually worth checking — is that the target ends up holding what Git holds.
EXPECTED_ROWS=$(python3 -c "
import json, pathlib
summary = json.loads(pathlib.Path('knowledge_graph/graph_summary.json').read_text())
print(summary['entity_count'] + summary['relationship_count'])
" 2>/dev/null || echo 0)
EXPECTED_ENTITIES=$(python3 -c "
import json, pathlib
print(json.loads(pathlib.Path('knowledge_graph/graph_summary.json').read_text())['entity_count'])
" 2>/dev/null || echo 0)

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

# VW_SYNC_TARGET selects the transport, and the two need different credentials.
# Declared here rather than just before the apply because this guard has to know
# which one to demand: requiring SUPABASE_* for a run that never contacts
# PostgREST would refuse a perfectly valid sync.
#
#   postgres  writes over the PostgreSQL wire protocol with DATABASE_URL, and is
#             unaffected by the Dashboard's "Exposed schemas" setting. Default.
#   supabase  writes through PostgREST with the service role key, and is refused
#             with PGRST106 unless `knowledge` is on that list.
#
# See knowledge_sync/adapters.py for why the default changed.
SYNC_TARGET="${VW_SYNC_TARGET:-postgres}"

case "$SYNC_TARGET" in
  postgres) need_env DATABASE_URL ;;
  supabase) need_env SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY ;;
  *) fail "VW_SYNC_TARGET must be 'postgres' or 'supabase', got '$SYNC_TARGET'" ;;
esac

# Say where this is about to write, before anything reads or writes.
#
# The default transport changed from PostgREST to Postgres, and "the default
# changed" is not something anyone should have to take on trust when the thing
# being changed is which database gets 1,812 rows. Printed before the table
# checks so that if those checks look at the wrong database, the log already
# says which one.
#
# The adapter prints its own line when it is constructed. That one is the proof:
# this is intent, that is fact. If the two ever disagree, believe the adapter.
step "Transport"
info "target:   $SYNC_TARGET"
case "$SYNC_TARGET" in
  postgres)
    info "database: $(mask_dsn "${DATABASE_URL:-}")"
    info "note:     writes over the PostgreSQL protocol — the API's Exposed"
    info "          schemas setting does not apply to this path"
    ;;
  supabase)
    info "endpoint: $(mask_url "${SUPABASE_URL:-}")"
    info "note:     writes through PostgREST — requires 'knowledge' under"
    info "          Project Settings -> API -> Exposed schemas"
    ;;
esac

# Do the tables exist? Nothing checked, and the failure without this is a raw
# PostgREST error surfacing through the SDK — technically accurate and useless
# for working out that the migrations were never run.
#
# Uses psql and DATABASE_URL — not PostgREST — so it reports on the same database
# the default transport writes to.
#
# Still skipped rather than failed when psql is unavailable: with
# VW_SYNC_TARGET=supabase the sync needs no Postgres connection at all, and
# demanding one here would refuse a legitimate run. When the target IS postgres,
# DATABASE_URL is already guaranteed present by the guard above, so the only way
# to reach the skip is a runner without psql — which is called out loudly below
# rather than passed over in silence.
if [[ -n "${DATABASE_URL:-}" ]] && command -v psql >/dev/null 2>&1; then
  step "Checking the target tables exist"

  # Connectivity FIRST, and as its own question.
  #
  # psql_scalar swallows stderr, so an unreachable database and an absent table
  # both come back as the empty string. A CI run reported all eight tables
  # missing from a database that had just served knowledge.kg_entities over
  # PostgREST — the tables were there and psql simply could not connect. The
  # message sent the reader to redeploy a schema that was already correct.
  if ! probe_err=$(psql_probe); then
    fail "cannot connect to DATABASE_URL. Whatever else is true, this is NOT a
    missing schema — nothing here was able to look.

    psql said:
      ${probe_err:-(no output)}

    Target: $(mask_dsn "${DATABASE_URL:-}")
$(diagnose_pg_failure "$probe_err" "${DATABASE_URL:-}")

    The tables may well exist; nothing here could look. Check the DATABASE_URL
    secret against Project Settings -> Database -> Connection string. The most
    common cause is an unreplaced [YOUR-PASSWORD] placeholder, or a password
    containing characters that must be percent-encoded.

    The sync would fail the same way: it connects with this same DSN."
  fi

  missing=""
  for tbl in kg_entities kg_relationships kg_districts kg_skills \
             kg_schemes kg_businesses kg_industries kg_agriculture; do
    present=$(psql_scalar "select to_regclass('knowledge.$tbl') is not null;")
    [[ "$present" == "t" ]] || missing="$missing $tbl"
  done
  if [[ -n "$missing" ]]; then
    fail "the knowledge schema is missing these tables:$missing

    The migrations have not been applied to this database. Two ways:

      locally   ./scripts/first_deploy.sh   (applies them in order, expects 009
                to fail, repairs it with 011, and stops at a manual gate)

      by hand   docs/MANUAL_DEPLOYMENT_PLAN.md — an audit query to run first,
                then the exact files in order

    Run sql/deploy_knowledge.sql in the Supabase SQL Editor — one paste, all
    15 tables, and safe to re-run."
  fi
  ok "all 8 target tables present"
elif [[ "$SYNC_TARGET" == "postgres" ]]; then
  # DATABASE_URL is guaranteed present here — the guard above demanded it — so
  # the only way to land in this branch is a runner without psql. Warn rather
  # than info: the check that would have caught "schema deployed but empty"
  # before writing anything just did not run.
  warn "psql is not installed — the table-existence check was SKIPPED.
    A missing table will now surface partway through apply as a psycopg
    UndefinedTable error instead of a clear message here."
else
  info "target is supabase and psql is unavailable — skipping the table check;
    a missing table will surface as a PostgREST error during apply"
fi

step "Applying${FULL:+ (full rebuild)} via --target $SYNC_TARGET"
run python3 -m knowledge_sync --target "$SYNC_TARGET" sync $FULL | tail -6 | sed 's/^/    /'

# The ninth table.
#
# knowledge.kg_vocabulary_map is NOT in TABLE_SPECS — the sync framework owns
# eight tables and the crosswalk is not one of them. It is built by
# governance/vocabulary/build_crosswalk.py and loaded by load_crosswalk.sh from
# three CSVs, through a staging table with `on conflict do update`.
#
# That loader was only ever invoked by first_deploy.sh, the greenfield path.
# Nothing in the CI path called it, so a sync would report complete with 647
# entities and 865 edges while the crosswalk sat at zero — and resolveTerms() is
# the only bridge from a term a user types to a graph entity, so every district
# and skill lookup silently resolved to nothing. health_check.sh calls that
# CRITICAL, correctly.
#
# Placed after the apply because the crosswalk references global_entity_id
# values that the entity load creates. Idempotent, so the re-run below is safe.
if command -v psql >/dev/null 2>&1; then
  step "Loading the vocabulary crosswalk"
  run "$VW_ROOT/scripts/load_crosswalk.sh" 2>&1 | sed 's/^/    /'
else
  warn "psql is not installed — the vocabulary crosswalk was NOT loaded.
    knowledge.kg_vocabulary_map stays empty, and every district and skill a
    user types will fail to resolve. Install postgresql-client on the runner."
fi

step "Proving idempotency — the check that matters"
if [[ "$DRY_RUN" == "1" ]]; then
  info "[dry-run] would re-run sync and require 0 inserted, 0 updated"
  summary "Sync (dry run)"; exit 0
fi
python3 -m knowledge_sync --target "$SYNC_TARGET" sync > /tmp/vw_sync_second.log 2>&1
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
info "knowledge.kg_entities: ${actual:-unreadable} (graph holds ${EXPECTED_ENTITIES})"
[[ "${actual:-0}" == "${EXPECTED_ENTITIES}" ]] \
  && ok "the target holds exactly what Git holds" \
  || warn "the target holds ${actual:-unreadable} entities and Git holds ${EXPECTED_ENTITIES} — \
a difference here means a row did not project, not that the graph changed size"

summary "Knowledge sync"
