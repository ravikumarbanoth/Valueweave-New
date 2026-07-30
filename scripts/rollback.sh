#!/usr/bin/env bash
# Roll back a deployment, one level at a time.
#
# Five levels, least to most destructive. Levels 1-4 lose nothing that is not
# derived from Git; level 5 is the only one that touches user data, and it is
# deliberately not automated here.
#
#   ./scripts/rollback.sh sync [run_id]     undo one knowledge sync run
#   ./scripts/rollback.sh knowledge         drop and rebuild the projection
#   ./scripts/rollback.sh intelligence      drop and recompute user intelligence
#   ./scripts/rollback.sh list              show available rollback points
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
cd "$VW_ROOT"

LEVEL="${1:-}"

case "$LEVEL" in
  list)
    need_cmd python3
    step "Knowledge sync rollback points"
    python3 -m knowledge_sync snapshots | sed 's/^/    /'
    step "Recent runs"
    python3 -m knowledge_sync history --limit 10 | sed 's/^/    /'
    exit 0
    ;;

  sync)
    need_cmd python3
    need_env SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY
    RUN_ID="${2:-}"
    if [[ -z "$RUN_ID" ]]; then
      step "Available rollback points"
      python3 -m knowledge_sync snapshots | sed 's/^/    /'
      fail "pass a run_id: ./scripts/rollback.sh sync <run_id>"
    fi
    step "Dry run for $RUN_ID"
    python3 -m knowledge_sync rollback "$RUN_ID" --dry-run | sed 's/^/    /'
    confirm "Apply this rollback?"
    run python3 -m knowledge_sync rollback "$RUN_ID" | sed 's/^/    /'
    ok "run $RUN_ID reversed"
    info "Only the most recent run should normally be rolled back. Reversing an
    older one while newer runs stand produces a state matching no version of Git."
    ;;

  knowledge)
    need_cmd psql python3
    need_env DATABASE_URL SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY
    step "Level 3 — drop and rebuild the knowledge projection"
    info "Safe by construction: the schema holds nothing but a projection of Git."
    info "The crosswalk lives here too and will be reloaded."
    confirm "Drop schema knowledge and rebuild it?"
    run psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -c "drop schema if exists knowledge cascade;"
    psql_file "$VW_ROOT/knowledge_sync/migrations/001_knowledge_schema.sql"
    psql_file "$VW_ROOT/frontend/migrations/011_repair_vocabulary_crosswalk.sql"
    run "$VW_ROOT/scripts/load_crosswalk.sh"
    run python3 -m knowledge_sync sync --full --target supabase | tail -4 | sed 's/^/    /'
    ok "projection rebuilt"
    warn "Recompute user intelligence: recommendations reference entity ids, and a
         full rebuild can change them. ./scripts/run_user_intelligence.sh --from-db --apply --force"
    ;;

  intelligence)
    need_cmd psql
    need_env DATABASE_URL
    step "Level 4 — drop and recompute user intelligence"
    info "Loses only computed rows. Every one is reproducible from Git plus profiles."
    confirm "Drop schema user_intelligence and recreate it?"
    run psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -c "drop schema if exists user_intelligence cascade;"
    psql_file "$VW_ROOT/user_intelligence/migrations/001_user_intelligence.sql"
    ok "schema recreated, empty"
    info "Recompute: ./scripts/run_user_intelligence.sh --from-db --apply"
    ;;

  ""|-h|--help)
    cat <<'USAGE'
Rollback ladder — stop at the first level that works.

  1  frontend      Vercel -> Deployments -> previous -> Promote        (not scripted)
  2  sync          ./scripts/rollback.sh sync <run_id>                 loses that run
  3  knowledge     ./scripts/rollback.sh knowledge                     loses nothing
  4  intelligence  ./scripts/rollback.sh intelligence                  loses computed rows
  5  public schema Supabase point-in-time restore                      LOSES USER DATA

  ./scripts/rollback.sh list        show rollback points

Level 5 is not scripted on purpose. It is the only level that destroys data a
user created, and it needs a decision rather than a command.
USAGE
    exit 0
    ;;

  *) fail "unknown level: $LEVEL (try --help)" ;;
esac

summary "Rollback"
