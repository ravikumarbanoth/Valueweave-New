#!/usr/bin/env bash
# Load the vocabulary crosswalk into knowledge.kg_vocabulary_map.
#
# Deployment blocker B2: 202 rows sit in governance/vocabulary/*.csv and nothing
# loaded them. Without this, resolveTerms() returns nothing and every district and
# skill a user types silently fails to resolve.
#
# Idempotent: the table's unique constraint is (term_kind, source_vocab,
# normalised_term), and rows are inserted through a staging table with
# `on conflict do update`, so re-running refreshes rather than duplicating.
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
cd "$VW_ROOT"
need_cmd psql
need_env DATABASE_URL

VOCAB="$VW_ROOT/governance/vocabulary"
EXPECTED_TOTAL=202

step "Checking the target table"
have=$(psql_scalar "select to_regclass('knowledge.kg_vocabulary_map') is not null;")
[[ "$have" == "t" ]] || fail "knowledge.kg_vocabulary_map does not exist.
    Apply frontend/migrations/011_repair_vocabulary_crosswalk.sql first."
ok "knowledge.kg_vocabulary_map present"

step "Loading crosswalk CSVs"
total=0
for kind in district sector skill; do
  csv="$VOCAB/${kind}_crosswalk.csv"
  [[ -f "$csv" ]] || fail "missing $csv — run governance/vocabulary/build_crosswalk.py"
  rows=$(($(wc -l < "$csv") - 1))
  total=$((total + rows))

  if [[ "$DRY_RUN" == "1" ]]; then
    info "[dry-run] would load $rows row(s) from ${kind}_crosswalk.csv"
    continue
  fi

  # Staged, so a malformed CSV cannot leave the live table half-loaded.
  psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -q <<SQL
begin;
create temporary table _vw_stage (like knowledge.kg_vocabulary_map including defaults)
  on commit drop;
alter table _vw_stage drop column if exists id;
alter table _vw_stage drop column if exists synced_at;

\copy _vw_stage(term_kind, source_vocab, source_term, normalised_term, global_entity_id, entity_type, canonical_name, match_method, match_score, notes) from '$csv' with (format csv, header true, force_null (global_entity_id, entity_type, canonical_name, match_score))

insert into knowledge.kg_vocabulary_map
      (term_kind, source_vocab, source_term, normalised_term,
       global_entity_id, entity_type, canonical_name, match_method, match_score, notes)
select term_kind, source_vocab, source_term, normalised_term,
       nullif(global_entity_id, ''), nullif(entity_type, ''), nullif(canonical_name, ''),
       match_method, match_score, notes
  from _vw_stage
    on conflict (term_kind, source_vocab, normalised_term) do update
   set global_entity_id = excluded.global_entity_id,
       entity_type      = excluded.entity_type,
       canonical_name   = excluded.canonical_name,
       match_method     = excluded.match_method,
       match_score      = excluded.match_score,
       notes            = excluded.notes,
       synced_at        = now();
commit;
SQL
  ok "${kind}: $rows row(s)"
done

if [[ "$DRY_RUN" == "1" ]]; then summary "Crosswalk load (dry run)"; exit 0; fi

step "Verifying"
loaded=$(psql_scalar "select count(*) from knowledge.kg_vocabulary_map;")
info "rows in table: $loaded (expected $EXPECTED_TOTAL)"
# `group by term_kind`, NOT `group by 1`.
#
# The ordinal refers to the first SELECT ITEM, and the first select item here is
# the whole concatenation — which contains count(*). PostgreSQL rejects that with
# "aggregate functions are not allowed in GROUP BY", after the load has already
# committed, so the sync succeeded and the workflow failed anyway.
#
# The two-column form quoted in the migration and in deploy_knowledge.sql —
# `select term_kind, count(*) ... group by 1` — is correct, because there
# ordinal 1 IS term_kind. Collapsing those two columns into one formatted string
# for prettier CLI output silently changed what the ordinal pointed at. Naming
# the column cannot drift that way.
psql "$DATABASE_URL" -qtAX -c \
  "select '    ' || term_kind || ': ' || count(*)
     from knowledge.kg_vocabulary_map
    group by term_kind
    order by term_kind;"

[[ "$loaded" == "$EXPECTED_TOTAL" ]] \
  && ok "all $EXPECTED_TOTAL crosswalk rows present" \
  || warn "expected $EXPECTED_TOTAL rows, found $loaded — regenerate with build_crosswalk.py if the packages changed"

incoherent=$(psql_scalar "
  select count(*) from knowledge.kg_vocabulary_map
   where (match_method = 'NO_COUNTERPART') <> (global_entity_id is null);")
[[ "$incoherent" == "0" ]] \
  && ok "resolution coherence holds" \
  || fail "$incoherent row(s) violate the resolution invariant"

summary "Crosswalk load"
