#!/usr/bin/env bash
# Shared helpers for the ValueWeave deployment scripts.
#
# Sourced, never executed. Every script that uses it inherits:
#   * strict mode          — a typo fails the script instead of skipping a step
#   * consistent output    — step / ok / warn / fail, so logs are greppable
#   * credential guards    — checked once, up front, with the reason named
#   * DRY_RUN              — print what would run, touch nothing
#
# WHY BASH
# --------
# These wrap psql and two Python CLIs. A Python wrapper around a Python CLI adds an
# import path and an argument-forwarding layer to gain nothing, and an operator
# recovering a deployment at 2am can read shell.

set -Eeuo pipefail

VW_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export VW_ROOT

DRY_RUN="${DRY_RUN:-0}"

if [[ -t 1 ]]; then
  C_RESET=$'\033[0m'; C_DIM=$'\033[2m'; C_RED=$'\033[31m'
  C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'; C_BOLD=$'\033[1m'
else
  C_RESET=""; C_DIM=""; C_RED=""; C_GREEN=""; C_YELLOW=""; C_BOLD=""
fi

VW_WARNINGS=0

step() { printf '\n%s==> %s%s\n' "$C_BOLD" "$*" "$C_RESET"; }
ok()   { printf '    %s✓%s %s\n' "$C_GREEN" "$C_RESET" "$*"; }
info() { printf '    %s%s%s\n' "$C_DIM" "$*" "$C_RESET"; }
warn() { VW_WARNINGS=$((VW_WARNINGS + 1))
         printf '    %s! %s%s\n' "$C_YELLOW" "$*" "$C_RESET" >&2; }
fail() { printf '    %s✗ %s%s\n' "$C_RED" "$*" "$C_RESET" >&2; exit 1; }

# Run a command, or describe it under DRY_RUN.
run() {
  if [[ "$DRY_RUN" == "1" ]]; then
    printf '    %s[dry-run]%s %s\n' "$C_DIM" "$C_RESET" "$*"
    return 0
  fi
  "$@"
}

need_env() {
  local missing=()
  for var in "$@"; do
    [[ -n "${!var:-}" ]] || missing+=("$var")
  done
  if ((${#missing[@]})); then
    fail "missing required environment: ${missing[*]}
    Source a gitignored env file rather than exporting inline — the service role
    key must not reach shell history. See PRODUCTION_DEPLOYMENT_GUIDE.md §3."
  fi
}

need_cmd() {
  for c in "$@"; do
    command -v "$c" >/dev/null 2>&1 || fail "required command not found: $c"
  done
}

# A connection string, safe to print.
#
# Parsed with urllib rather than cut/sed: a Postgres password may legally contain
# `@`, `:` and `/`, so a naive split on those puts part of the credential in the
# log — which is the exact opposite of what a masking helper is for.
#
# Shows scheme, host, port and database in full, because the whole point is to
# let someone confirm which database is about to be written to. The password is
# replaced outright; the username keeps its prefix and loses the rest, since on
# Supabase poolers it carries the project ref (postgres.<ref>).
mask_dsn() {
  python3 - "$1" <<'PYEOF'
import sys
from urllib.parse import urlsplit, parse_qs

raw = (sys.argv[1] if len(sys.argv) > 1 else "").strip()
if not raw:
    print("(not set)"); raise SystemExit

try:
    u = urlsplit(raw)
except Exception:
    print("(unparseable — check the DATABASE_URL secret)"); raise SystemExit

# Host may be absent from the authority and supplied as a query parameter
# instead: `postgresql://user@/db?host=/var/run/postgresql` is a valid libpq URI
# and is what a unix-socket connection looks like. Rejecting it as unparseable
# would report a fault in a working configuration.
host = u.hostname or (parse_qs(u.query).get("host", [""])[0]) or "(local socket)"

# .port raises on a non-numeric port, which happens when an unencoded ":" in the
# password confuses the authority split. Degrade to "no port shown" rather than
# declaring the whole DSN unreadable — and never fall back to printing the raw
# string, which is where the password lives.
try:
    port = f":{u.port}" if u.port else ""
except ValueError:
    port = ""

user = u.username or ""
if user:
    head = user.split(".", 1)[0]
    user = head + (".****" if "." in user else "")
cred = f"{user}:****@" if (u.username or u.password or "@" in u.netloc) else ""

db = (u.path or "").lstrip("/") or "(default)"
scheme = u.scheme or "postgresql"
print(f"{scheme}://{cred}{host}{port}/{db}")
PYEOF
}

# Same idea for a project URL: keep the shape, hide the project ref.
mask_url() {
  printf '%s' "${1:-(not set)}" | sed -E 's#(https://)[^./]+#\1****#'
}

# One scalar out of Postgres, whitespace trimmed. Empty string on error, so a
# caller decides what a failed query means rather than the script dying inside a
# health check whose whole job is to report failure.
psql_scalar() {
  psql "$DATABASE_URL" -qtAX -c "$1" 2>/dev/null | tr -d '[:space:]' || true
}

psql_file() {
  local f="$1"
  [[ -f "$f" ]] || fail "migration not found: $f"
  run psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -q -f "$f"
}

# Confirm a destructive action unless VW_ASSUME_YES=1.
confirm() {
  local prompt="$1"
  if [[ "${VW_ASSUME_YES:-0}" == "1" ]]; then
    info "auto-confirmed: $prompt"
    return 0
  fi
  if [[ ! -t 0 ]]; then
    fail "$prompt
    Refusing in a non-interactive shell. Set VW_ASSUME_YES=1 to proceed."
  fi
  read -r -p "    ${prompt} [y/N] " reply
  [[ "$reply" == "y" || "$reply" == "Y" ]] || fail "aborted by operator"
}

summary() {
  local label="$1"
  printf '\n'
  if ((VW_WARNINGS)); then
    printf '%s%s complete with %d warning(s).%s\n' \
      "$C_YELLOW" "$label" "$VW_WARNINGS" "$C_RESET"
  else
    printf '%s%s complete.%s\n' "$C_GREEN" "$label" "$C_RESET"
  fi
}
