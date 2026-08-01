#!/usr/bin/env python3
"""
Generate sql/deploy_knowledge.sql from the migration files.

WHY GENERATED AND NOT HAND-WRITTEN
----------------------------------
The consolidated script must contain the same SQL as the migrations, forever. A
hand-transcribed copy is a second source of truth that drifts the first time
somebody edits a migration and forgets this file — and the drift is invisible
until a deployment produces a schema the sync does not recognise.

So the migrations stay authoritative and this assembles them. Re-run after any
migration change; `tests/test_knowledge_pipeline.py` fails if the checked-in
output is stale.

WHAT IT CHANGES, AND WHY EACH CHANGE IS SAFE
--------------------------------------------
1.  A preflight block that aborts if `public.profiles` is missing, or if it
    exists without an `is_admin` column. That table is the application's own; if
    it is absent the operator is pointed at a database that is not the one they
    think it is, and creating a stand-in would corrupt a real deployment later.

    The column check is not theoretical — it was found by running this script.
    `public.is_valueweave_admin()` reads `p.is_admin`, PostgreSQL validates a
    `language sql` body at CREATE time, and the column is added not by the base
    schema but by frontend/migrations/001_research_articles.sql. On a database
    where that migration never ran, PHASE 1 fails with `column p.is_admin does
    not exist` forty lines into the script. Checking up front turns an obscure
    failure into an instruction. Both checks run before anything is created, and
    neither writes to `profiles`: adding the column is the operator's call.

2.  `public.is_valueweave_admin()` is lifted out of
    202606200002_entrepreneurship_knowledge_graph.sql and placed FIRST.
    001_knowledge_schema.sql's final statement — the policy on
    knowledge.sync_runs — calls it, and 001 is not transactional, so without it
    you get 9 tables, 34 indexes, 8 of 9 policies and an unprotected sync_runs.
    The function is `create or replace`, so re-declaring it is a no-op when the
    real migration has already run.

3.  The inner `begin;`/`commit;` in 011 is removed and the WHOLE script is
    wrapped in one transaction instead. Nested transaction control inside a
    larger batch either errors or silently commits early depending on the
    client. One outer transaction is stronger than 011's own: the entire
    deployment is now all-or-nothing.

    Every statement involved is transactional in PostgreSQL — create schema,
    create table, create index, alter table, create policy, grant, alter
    default privileges. Verified by running the generated file against a real
    PostgreSQL 16.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sql" / "deploy_knowledge.sql"

CMS = ROOT / "supabase/migrations/202606200002_entrepreneurship_knowledge_graph.sql"
PHASES = [
    ("2", "Knowledge schema — 9 tables, 34 indexes, 9 read policies",
     "knowledge_sync/migrations/001_knowledge_schema.sql"),
    ("3", "Vocabulary crosswalk repair — the table 009 could not create",
     "frontend/migrations/011_repair_vocabulary_crosswalk.sql"),
    ("4", "User intelligence — 5 tables, RLS scoped to auth.uid()",
     "user_intelligence/migrations/001_user_intelligence.sql"),
]


def admin_function():
    """The `create or replace function public.is_valueweave_admin()` block."""
    src = CMS.read_text(encoding="utf-8")
    start = src.index("create or replace function public.is_valueweave_admin()")
    end = src.index("$$;", start) + len("$$;")
    return src[start:end]


def admin_function_body():
    """The same block as a plain `create function`, for the create-if-absent path.

    `or replace` is dropped because the caller has already established that the
    function does not exist. Keeping it would make the guard decorative and
    reintroduce the risk of rewriting a predicate that sixteen live policies
    evaluate.

    The body's own `$$` quoting is left alone: it sits inside `$fn$ … $fn$`
    inside `do $phase1$ … $phase1$`, and PostgreSQL matches dollar-quote tags
    exactly, so three distinct tags nest without interfering.
    """
    fn = admin_function()
    assert fn.startswith("create or replace function"), fn[:40]
    assert "$fn$" not in fn and "$phase1$" not in fn, "dollar-quote tag collision"
    return "create function" + fn[len("create or replace function"):]


def indent(text, prefix):
    return "\n".join(prefix + l if l.strip() else l for l in text.splitlines())


def strip_transaction_control(sql, path):
    """Remove standalone `begin;` / `commit;` — the outer wrapper replaces them.

    Line-anchored so a `begin` inside a `do $$ … $$` block is untouched: those
    are PL/pgSQL block delimiters, not transaction control, and removing one
    would produce a syntax error rather than a subtle bug.
    """
    out, removed = [], 0
    for line in sql.splitlines():
        if line.strip().lower() in ("begin;", "commit;"):
            removed += 1
            out.append(f"-- [consolidated] removed `{line.strip()}` "
                       f"— the whole script runs in one transaction")
            continue
        out.append(line)
    if removed and "011_" not in path:
        print(f"  note: stripped {removed} transaction statement(s) from {path}",
              file=sys.stderr)
    return "\n".join(out)


def banner(num, title, source=None):
    line = "═" * 74
    src = f"\n--  source: {source}" if source else ""
    return (f"\n\n-- {line}\n"
            f"-- PHASE {num} · {title}{src}\n"
            f"-- {line}\n")


def build():
    parts = [f"""-- ValueWeave — consolidated knowledge deployment
--
-- GENERATED FILE. Do not edit.
--   source: scripts/build_deployment_sql.py
--   regenerate: python3 scripts/build_deployment_sql.py
--
-- Paste the whole thing into the Supabase SQL Editor and run it once.
--
-- SAFE TO RE-RUN. Every object is `if not exists` or `create or replace`, every
-- policy is dropped before it is created, and the whole script is ONE
-- TRANSACTION — if any statement fails, nothing is applied and the database is
-- exactly as it was.
--
-- SAFE ON A NON-EMPTY DATABASE. It creates only objects in the `knowledge` and
-- `user_intelligence` schemas, plus one `create or replace` on an existing
-- application function. It touches no application table and deletes nothing.
--
-- WHAT IT DOES NOT DO. Exposing the schemas is a Supabase Dashboard action and
-- no SQL can perform it — Project Settings -> API -> Exposed schemas. Until
-- `knowledge` is listed there, PostgREST refuses every request naming it,
-- INCLUDING requests carrying the service-role key, because that is a server
-- config and not a permission check. The sync will keep failing without it.
--
-- Verify before and after with sql/verify_knowledge_schema.sql.

begin;
{banner("0", "Preflight — refuse to run against the wrong database")}
-- Two things must already be true. Both are checked before anything is created,
-- so a database that fails either is left completely untouched.
do $$
begin
  -- (a) This must be the ValueWeave application database.
  if to_regclass('public.profiles') is null then
    raise exception using
      message = 'public.profiles does not exist in this database.',
      hint    = 'This script extends an existing ValueWeave application schema. '
                'Either you are connected to the wrong project, or the base '
                'migrations have never been applied. Do not create a stand-in '
                'profiles table — apply frontend/supabase_schema.sql first.';
  end if;

  -- (b) PHASE 1 creates public.is_valueweave_admin(), whose body reads
  --     p.is_admin. PostgreSQL validates a `language sql` body at CREATE time,
  --     so a missing column fails there, not at first call. The column comes
  --     from frontend/migrations/001_research_articles.sql, which is a separate
  --     migration and may not have been applied.
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public'
      and table_name   = 'profiles'
      and column_name  = 'is_admin'
  ) then
    raise exception using
      message = 'public.profiles exists but has no is_admin column.',
      hint    = 'public.is_valueweave_admin() reads it, and one policy '
                '(knowledge.sync_runs admin read) depends on that function. '
                'Apply frontend/migrations/001_research_articles.sql, or add '
                'just the column: alter table public.profiles add column if '
                'not exists is_admin boolean not null default false;';
  end if;
end $$;
{banner("1", "Prerequisite — public.is_valueweave_admin()",
        "supabase/migrations/202606200002_entrepreneurship_knowledge_graph.sql")}
-- PHASE 2's final statement (the policy on knowledge.sync_runs) calls this.
--
-- CREATED ONLY IF ABSENT — deliberately not `create or replace`.
--
-- In the production database this function already exists and SIXTEEN policies
-- on the CMS tables (kg_district_profiles, kg_skills, kg_schemes, kg_resources,
-- kg_roadmaps, kg_industry_sectors, kg_collaborator_types) are written in terms
-- of it. `create or replace` would silently swap the body those policies
-- evaluate. The two versions are believed identical, but "believed identical"
-- is not a reason to rewrite the predicate guarding an existing access-control
-- rule, and this script has no way to diff them safely.
--
-- So: if it exists, leave it exactly as it is. If it does not, create it.
do $phase1$
begin
  if to_regprocedure('public.is_valueweave_admin()') is not null then
    raise notice '[phase 1] public.is_valueweave_admin() already exists — left untouched.';
  else
    execute $fn$
{indent(admin_function_body(), "      ")}
    $fn$;
    raise notice '[phase 1] created public.is_valueweave_admin().';
  end if;
end $phase1$;
"""]

    for num, title, rel in PHASES:
        sql = (ROOT / rel).read_text(encoding="utf-8")
        parts.append(banner(num, title, rel))
        parts.append(strip_transaction_control(sql, rel))

    parts.append(banner("5", "Commit"))
    parts.append("commit;\n")
    return "".join(parts)


if __name__ == "__main__":
    OUT.parent.mkdir(exist_ok=True)
    text = build()
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(text.splitlines())} lines)")
