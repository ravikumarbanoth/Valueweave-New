#!/usr/bin/env bash
# One-shot first deployment: schema through verification.
#
# Orchestrates the other scripts in the order PRODUCTION_DEPLOYMENT_GUIDE.md
# establishes. Every step is idempotent, so a run that fails part-way can be
# re-run once the cause is fixed rather than needing a teardown.
#
# It does NOT: create the Supabase project, configure Google OAuth, expose the
# schemas, or deploy the frontend. Three of those are dashboard actions and one
# belongs to Vercel; a script that pretended to do them would report success for
# work it never did.
#
#   ./scripts/first_deploy.sh              full run
#   DRY_RUN=1 ./scripts/first_deploy.sh    print every step, change nothing
#   ./scripts/first_deploy.sh --skip-seed  omit the 500 synthetic opportunities
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
cd "$VW_ROOT"
need_cmd psql python3
need_env DATABASE_URL

SKIP_SEED=0
for a in "$@"; do
  case "$a" in
    --skip-seed) SKIP_SEED=1 ;;
    *) fail "unknown argument: $a" ;;
  esac
done

started=$(date +%s)

step "0 · Preflight"
python3 tests/run_all.py --quiet > /tmp/vw_tests.log 2>&1 \
  && ok "$(grep -oE 'TOTAL +[0-9]+' /tmp/vw_tests.log | tr -s ' ') tests pass" \
  || { tail -20 /tmp/vw_tests.log; fail "test suite failed — the clone or toolchain is wrong"; }
info "commit: $(git rev-parse --short HEAD 2>/dev/null || echo unknown)"

step "1 · Base schema"
psql_file "$VW_ROOT/frontend/supabase_schema.sql"
for m in 001_research_articles 002_collaboration_marketplace; do
  psql_file "$VW_ROOT/frontend/migrations/${m}.sql"
done

if ((SKIP_SEED)); then
  info "skipping 003_seed_opportunities.sql — no synthetic rows"
else
  psql_file "$VW_ROOT/frontend/migrations/003_seed_opportunities.sql"
  warn "500 synthetic opportunities inserted. They carry no provenance and are the
         main content of /dashboard. Label them, or re-run with --skip-seed:
         update public.opportunities set description =
           '[Illustrative example — not a verified opportunity] ' || description
          where created_by = 'system_seed';"
fi

for m in 004_admin_analytics 005_growth_intelligence 006_visitor_analytics \
         007_engagement_retention; do
  psql_file "$VW_ROOT/frontend/migrations/${m}.sql"
done

step "2 · Migration 009 — expected to fail, then repaired by 011"
# 009 references public.kg_entity_registry, which no migration creates. It is run
# anyway so history is honest: the database records the attempt, and 011 repairs
# whatever state it leaves. Failure here is expected and not fatal.
if psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -q \
     -f "$VW_ROOT/frontend/migrations/009_vocabulary_crosswalk.sql" 2>/dev/null; then
  ok "009 applied (pre-existing kg_entity_registry)"
else
  info "009 failed as expected — missing public.kg_entity_registry. 011 repairs this."
fi

psql_file "$VW_ROOT/frontend/migrations/010_missing_application_features.sql"
psql_file "$VW_ROOT/frontend/migrations/011_repair_vocabulary_crosswalk.sql"
ok "011 applied — knowledge.kg_vocabulary_map exists without the unbuildable FK"

step "3 · Platform settings and CMS tables"
psql_file "$VW_ROOT/supabase/migrations/202606200001_geo_video_devops.sql"
psql_file "$VW_ROOT/supabase/migrations/202606200002_entrepreneurship_knowledge_graph.sql"

step "4 · Derived schemas"
# One definition of "deploy the knowledge layer", shared with the Supabase SQL
# Editor path. This used to apply the two migrations directly, which meant the
# greenfield script and sql/deploy_knowledge.sql could disagree about what a
# deployed knowledge layer is — and the SQL Editor path is the one an operator
# actually uses against production.
#
# deploy_knowledge.sql is generated from those same migrations, adds the
# preflight and the correct ordering, and is idempotent, so re-applying 011 here
# after step 2 already ran it is a no-op.
psql_file "$VW_ROOT/sql/deploy_knowledge.sql"
tables=$(psql_scalar "select count(*) from pg_tables where schemaname in ('public','knowledge','user_intelligence');")
ok "${tables:-?} tables across 3 schemas"

step "5 · ⚠️  MANUAL — expose the schemas"
cat <<'MANUAL'
    Supabase Dashboard -> Project Settings -> API -> Exposed schemas
    Add:  knowledge, user_intelligence

    Skipping this produces NO ERROR ANYWHERE. Every query fails, safe() returns
    [], and the application looks exactly as it did before deployment.
MANUAL
confirm "Have you added both schemas and saved?"

step "6 · Vocabulary crosswalk"
run "$VW_ROOT/scripts/load_crosswalk.sh"

step "7 · Knowledge sync"
run "$VW_ROOT/scripts/run_sync.sh"

step "8 · User intelligence"
if psql_scalar "select count(*) from public.profiles;" | grep -qvE '^0?$'; then
  run "$VW_ROOT/scripts/run_user_intelligence.sh" --from-db --apply
else
  info "no profiles yet — run scripts/run_user_intelligence.sh --from-db --apply after the first sign-ups"
fi

step "9 · Verification"
set +e
"$VW_ROOT/scripts/verify_deployment.sh"
verify_status=$?
set -e

elapsed=$(( $(date +%s) - started ))
printf '\n%s─────────────────────────────────────────────%s\n' "$C_DIM" "$C_RESET"
printf '  First deployment finished in %dm %ds\n' $((elapsed / 60)) $((elapsed % 60))
case "$verify_status" in
  0) printf '  %sVerified.%s\n' "$C_GREEN" "$C_RESET" ;;
  1) printf '  %sVerified with known data gaps%s — see POST_DEPLOYMENT_VALIDATION.md §11.\n' "$C_YELLOW" "$C_RESET" ;;
  *) printf '  %sVerification failed.%s Fix, then re-run — every step is idempotent.\n' "$C_RED" "$C_RESET" ;;
esac
printf '\n  Still to do by hand:\n'
printf '    · bootstrap the first admin (update public.profiles set is_admin = true …)\n'
printf '    · configure Google OAuth redirect URIs\n'
printf '    · deploy the frontend\n\n'
exit "$verify_status"
