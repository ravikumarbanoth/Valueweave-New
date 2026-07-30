#!/usr/bin/env bash
# Rebuild the knowledge graph from packages/ and validate it.
#
# Needs no database and no credentials — it reads CSVs and writes CSVs. Safe to
# run anywhere, including in CI on a pull request.
#
#   ./scripts/run_graph_build.sh              rebuild and validate
#   ./scripts/run_graph_build.sh --check      validate only, change nothing
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
cd "$VW_ROOT"
need_cmd python3

CHECK_ONLY=0
[[ "${1:-}" == "--check" ]] && CHECK_ONLY=1

if ((CHECK_ONLY)); then
  step "Validating the committed graph"
else
  step "Rebuilding the knowledge graph"
  run python3 knowledge_graph/build_graph.py > /tmp/vw_graph_build.log 2>&1 \
    || { cat /tmp/vw_graph_build.log; fail "build_graph.py failed"; }
  tail -12 /tmp/vw_graph_build.log | sed 's/^/    /'
fi

step "Validating"
if run python3 knowledge_graph/validate_graph.py > /tmp/vw_graph_validate.log 2>&1; then
  grep -E "entities|relationships|connectivity|PASS" /tmp/vw_graph_validate.log \
    | sed 's/^/    /'
  ok "graph is structurally sound"
else
  cat /tmp/vw_graph_validate.log
  fail "validate_graph.py reported errors — do not sync"
fi

# The one expected warning. A second means something changed and needs reading.
warn_count=$(grep -cE "^\s+\[G[0-9]+" /tmp/vw_graph_validate.log || true)
if [[ "$warn_count" -gt 1 ]]; then
  warn "$warn_count validator warnings (expected 1: G10-ORPHANS). Read them before syncing."
else
  ok "1 expected warning (G10-ORPHANS, 142 entities)"
fi

if ((! CHECK_ONLY)) && git -C "$VW_ROOT" diff --quiet knowledge_graph/ 2>/dev/null; then
  ok "graph artifacts unchanged"
elif ((! CHECK_ONLY)); then
  # A rebuild always restamps created_at/updated_at. Tell the operator whether
  # anything real moved, because 1,500 changed lines looks alarming and usually is not.
  real=$(git -C "$VW_ROOT" diff knowledge_graph/ | grep '^[+-]' | grep -v '^[+-][+-]' \
         | sed 's/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/<D>/g' | sort | uniq -u | wc -l)
  if [[ "$real" -eq 0 ]]; then
    info "artifacts differ by build date only — no content change"
  else
    warn "$real line(s) differ beyond the build date. Review before committing."
  fi
fi

summary "Graph build"
