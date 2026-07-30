#!/usr/bin/env bash
# Compute per-user intelligence and write it to the user_intelligence schema.
#
# Deployment blocker B3, now closed: `user_intelligence write` is the writer that
# did not exist. Idempotent by result hash, so re-running over every user costs one
# read per unchanged user and writes nothing.
#
#   ./scripts/run_user_intelligence.sh                        fixture, memory target
#   ./scripts/run_user_intelligence.sh --users users.json     batch, memory target
#   ./scripts/run_user_intelligence.sh --users users.json --apply    write to Supabase
#   ./scripts/run_user_intelligence.sh --from-db --apply      read profiles, then write
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
cd "$VW_ROOT"
need_cmd python3

USERS=""; APPLY=0; FROM_DB=0; FORCE=""
while (($#)); do
  case "$1" in
    --users) USERS="${2:?--users needs a path}"; shift 2 ;;
    --apply) APPLY=1; shift ;;
    --from-db) FROM_DB=1; shift ;;
    --force) FORCE="--force"; shift ;;
    *) fail "unknown argument: $1" ;;
  esac
done

TARGET="memory"
if ((APPLY)); then
  need_env SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY
  TARGET="supabase"
else
  info "no --apply: computing against the in-memory target, writing nothing"
fi

if ((FROM_DB)); then
  need_cmd psql; need_env DATABASE_URL
  USERS="$(mktemp -t vw_users_XXXX.json)"
  step "Reading profiles from the database"
  # Only the columns the engine reads. A SELECT * here would pull personal data
  # into a temp file for no reason.
  psql "$DATABASE_URL" -qtAX -o "$USERS" -c "
    select coalesce(json_agg(u), '[]'::json) from (
      select json_build_object(
        'profile', json_build_object(
          'id', p.id, 'city', p.city, 'skills', p.skills,
          'interests', p.interests, 'looking_for', p.looking_for,
          'bio', p.bio, 'profile_complete', p.profile_complete)
      ) as u
      from public.profiles p
      where p.profile_complete = true
    ) t;" || fail "could not read profiles"
  count=$(python3 -c "import json,sys;print(len(json.load(open('$USERS'))))" 2>/dev/null || echo 0)
  ok "$count profile(s) with profile_complete = true"
  [[ "$count" != "0" ]] || { info "nothing to compute"; summary "User intelligence"; exit 0; }
fi

step "Computing and writing (target: $TARGET)"
args=(write --target "$TARGET" $FORCE)
[[ -n "$USERS" ]] && args+=(--users-json "$USERS")
run python3 -m user_intelligence "${args[@]}" || fail "write failed — see the errors above"

if ((APPLY)) && [[ "$DRY_RUN" != "1" ]] && command -v psql >/dev/null && [[ -n "${DATABASE_URL:-}" ]]; then
  step "Verifying"
  users=$(psql_scalar "select count(distinct user_id) from user_intelligence.user_activity_summary;")
  recs=$(psql_scalar "select count(*) from user_intelligence.user_recommendations;")
  info "users with intelligence: ${users:-unreadable}"
  info "recommendation rows:     ${recs:-unreadable}"
  [[ "${users:-0}" != "0" ]] && ok "intelligence populated" \
    || warn "no rows written — check that profiles exist and are complete"
fi

[[ -n "$USERS" && "$USERS" == /tmp/vw_users_* ]] && rm -f "$USERS"
summary "User intelligence"
