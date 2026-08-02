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

# libpq also accepts a keyword string: "host=... port=... password=...".
# Valid, and not a URI, so urlsplit would report a fault in a working value.
if "=" in raw.split()[0] and "://" not in raw:
    kv = dict(p.split("=", 1) for p in raw.split() if "=" in p)
    host = kv.get("host", "(unset)"); port = kv.get("port", "")
    print(f"keyword form: host={host}"
          + (f" port={port}" if port else "")
          + f" dbname={kv.get('dbname', '(default)')} "
            f"user={kv.get('user', '(default)')} password={'****' if 'password' in kv else '(none)'}")
    raise SystemExit

try:
    u = urlsplit(raw)
    host = u.hostname or (parse_qs(u.query).get("host", [""])[0]) or "(local socket)"
except ValueError as exc:
    # The common real cause, and worth naming rather than shrugging at: '[' and
    # ']' in the authority are parsed as an IPv6 literal, so a password
    # containing them — very often an unreplaced "[YOUR-PASSWORD]" from the
    # Supabase connection-string dialog — makes the whole URI invalid. libpq
    # rejects it for the same reason, so this is a real fault, not a display
    # problem. The exception text names only the host, never the password.
    hint = ""
    if "[" in raw or "]" in raw:
        hint = (" — the value contains '[' or ']'. If that is a literal "
                "[YOUR-PASSWORD] placeholder, replace it with the real password; "
                "if the password genuinely contains brackets, percent-encode them "
                "(%5B and %5D)")
    print(f"(not a valid connection URI: {exc}{hint})")
    raise SystemExit
except Exception:
    print("(unparseable — check the DATABASE_URL secret)"); raise SystemExit

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
print(f"{u.scheme or 'postgresql'}://{cred}{host}{port}/{db}")
PYEOF
}

# Strip anything credential-shaped out of arbitrary text — a libpq error, say —
# before it reaches a public build log.
redact() {
  sed -E -e 's#(://[^:/@]*):[^@]*@#\1:****@#g' -e 's#password=[^ ]*#password=****#g'
}

# Can we actually reach the database? Returns 0 and prints nothing on success;
# returns 1 and prints the redacted reason otherwise.
#
# Exists because psql_scalar swallows stderr, which makes "the connection
# failed" and "the query returned false" indistinguishable. That ambiguity sent
# a CI run into reporting all eight tables missing from a database that
# demonstrably had them — the tables had just been read successfully through
# PostgREST seconds earlier.
psql_probe() {
  local err
  if ! err=$(psql "$DATABASE_URL" -qtAX -c "select 1" 2>&1 >/dev/null); then
    printf '%s' "$err" | head -3 | redact
    return 1
  fi
  return 0
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
