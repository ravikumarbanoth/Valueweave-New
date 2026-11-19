#!/usr/bin/env python3
"""
Cloudflare compatibility, Phase 2A: research articles without a filesystem,
article rendering without code evaluation, and the Next.js 15 behaviour that
was pinned explicitly.

Two things stopped research articles working on Cloudflare Workers:

  1. lib/mdx.js read content/research/*.mdx with `fs` at request time; Workers
     have no project filesystem. Now a build-time registry
     (scripts/build-research-registry.mjs) carries the same files.
  2. compileMDX evaluates generated code with `new Function`; Workers forbid
     it ("Code generation from strings disallowed"). Now lib/mdx-render.js
     renders the same MDX with no evaluation.

These tests hold that neither change altered what a reader sees: the registry
is the files, the visibility rule is unchanged, and the new renderer produces
byte-identical HTML to compileMDX for every article.
"""
import json
import re
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

from tests.js_harness import NODE, JsHarness

ROOT = Path(__file__).resolve().parent.parent
FE = ROOT / "frontend"
CONTENT = FE / "content" / "research"
GENERATOR = FE / "scripts" / "build-research-registry.mjs"
ESBUILD = FE / "node_modules" / ".bin" / "esbuild"


def read(path):
    return Path(path).read_text(encoding="utf-8")


def code(path):
    src = re.sub(r"/\*.*?\*/", "", read(path), flags=re.DOTALL)
    return "\n".join(line.split("//", 1)[0] for line in src.splitlines())


def generate(out, content=None):
    cmd = [NODE, str(GENERATOR), "--out", str(out)]
    if content:
        cmd += ["--content", str(content)]
    subprocess.run(cmd, check=True, capture_output=True, cwd=FE)


# ═══════════════════════════════════════ 1. the registry is the files
@unittest.skipIf(NODE is None, "node is required — the generator is JavaScript")
class RegistryMatchesFilesTest(unittest.TestCase):
    """Every .mdx file, frontmatter and body exactly as gray-matter reads it."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix=".registry-", dir=FE)
        out = Path(cls.tmp.name) / "registry.mjs"
        generate(out)
        script = Path(cls.tmp.name) / "compare.mjs"
        script.write_text(textwrap.dedent(f"""
            import fs from "node:fs";
            import path from "node:path";
            import {{ createRequire }} from "node:module";
            const require = createRequire({json.dumps(str(FE / "package.json"))});
            const matter = require("gray-matter");
            const registry = (await import({json.dumps(out.as_uri())})).default;
            const dir = {json.dumps(str(CONTENT))};
            const files = fs.readdirSync(dir).filter((f) => f.endsWith(".mdx")).sort();
            const direct = files.map((f) => {{
              const {{ data, content }} = matter(fs.readFileSync(path.join(dir, f), "utf-8"));
              return {{ slug: f.replace(/\\.mdx$/, ""), data, content }};
            }});
            const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
            console.log(JSON.stringify({{
              files: files.length,
              slugs: registry.map((e) => e.slug),
              expected: direct.map((e) => e.slug),
              dataEqual: direct.every((d, i) => same(d.data, registry[i].data)),
              contentEqual: direct.every((d, i) => d.content === registry[i].content),
            }}));
        """), encoding="utf-8")
        cls.out = json.loads(subprocess.run([NODE, str(script)], capture_output=True, text=True,
                                            check=True, cwd=FE).stdout)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_article_file_is_in_the_registry(self):
        self.assertGreaterEqual(self.out["files"], 3)
        self.assertEqual(self.out["slugs"], self.out["expected"])

    def test_frontmatter_is_unchanged(self):
        self.assertTrue(self.out["dataEqual"])

    def test_body_is_unchanged(self):
        self.assertTrue(self.out["contentEqual"])


# ═══════════════════════════════════════ 2. the visibility rule is unchanged
@unittest.skipIf(NODE is None, "node is required — the loader is JavaScript")
class VisibilityTest(unittest.TestCase):
    """Published shows; `published: false` hides unless drafts are asked for."""

    @classmethod
    def setUpClass(cls):
        fixtures = Path(tempfile.mkdtemp(prefix=".registry-fixtures-", dir=FE))
        try:
            (fixtures / "live-guide.mdx").write_text(
                '---\ntitle: "Live guide"\ncategory: "energy"\npublishedAt: "2026-05-01T00:00:00.000Z"\n---\n\nBody **one**.\n',
                encoding="utf-8")
            (fixtures / "draft-guide.mdx").write_text(
                '---\ntitle: "Draft guide"\npublished: false\npublishedAt: "2026-06-01T00:00:00.000Z"\n---\n\nBody two.\n',
                encoding="utf-8")
            # An unquoted YAML date: gray-matter reads a Date, and it must stay one.
            (fixtures / "dated-guide.mdx").write_text(
                '---\ntitle: "Dated guide"\npublishedAt: 2026-04-01\n---\n\nBody three.\n', encoding="utf-8")
            # A file name the slug rule rejects is unreachable, as before.
            (fixtures / "Bad Name.mdx").write_text('---\ntitle: "Bad"\n---\n\nx\n', encoding="utf-8")
            cls.h = JsHarness()
            generate(cls.h.lib / "generated" / "research-registry.js", fixtures)
        finally:
            shutil.rmtree(fixtures, ignore_errors=True)
        cls.out = cls.h.run('''
            const m = await import("$LIB/mdx.js");
            const dated = m.getArticleBySlug("dated-guide");
            console.log(JSON.stringify({
              slugs: m.getAllArticleSlugs(),
              withDrafts: m.getAllArticleSlugs({ includeDrafts: true }),
              all: m.getAllArticles().map((a) => a.slug),
              draftHidden: m.getArticleBySlug("draft-guide") === null,
              draftWithFlag: m.getArticleBySlug("draft-guide", { includeDrafts: true })?.published,
              live: m.getArticleBySlug("live-guide"),
              datedIsDate: dated?.publishedAt instanceof Date,
              traversal: m.getArticleBySlug("../etc/passwd"),
              missing: m.getArticleBySlug("no-such-article"),
            }));
        ''')

    @classmethod
    def tearDownClass(cls):
        cls.h.cleanup()

    def test_drafts_are_hidden_by_default(self):
        self.assertNotIn("draft-guide", self.out["slugs"])
        self.assertTrue(self.out["draftHidden"])
        self.assertNotIn("draft-guide", self.out["all"])

    def test_drafts_are_available_when_asked_for(self):
        self.assertIn("draft-guide", self.out["withDrafts"])
        self.assertIs(self.out["draftWithFlag"], False)

    def test_published_article_fields_are_mapped_as_before(self):
        live = self.out["live"]
        self.assertEqual(live["title"], "Live guide")
        self.assertEqual(live["category"], "energy")
        self.assertTrue(live["published"])
        self.assertEqual(live["publishedAt"], "2026-05-01T00:00:00.000Z")
        self.assertIn("Body **one**.", live["content"])
        self.assertEqual(live["readingTime"], 1)

    def test_a_yaml_date_stays_a_date(self):
        self.assertTrue(self.out["datedIsDate"])

    def test_invalid_and_unknown_slugs_return_nothing(self):
        self.assertIsNone(self.out["traversal"])
        self.assertIsNone(self.out["missing"])
        # Same as the filesystem version: a file name the slug rule rejects is
        # never a published article. (With includeDrafts the old code listed
        # every file name, valid or not; the registry keeps that quirk rather
        # than silently changing admin behaviour.)
        self.assertNotIn("Bad Name", self.out["slugs"])
        self.assertIn("Bad Name", self.out["withDrafts"])

    def test_the_loader_no_longer_touches_the_filesystem(self):
        src = code(FE / "lib" / "mdx.js")
        for forbidden in ('from "fs"', 'from "path"', "readFileSync", "readdirSync", "process.cwd"):
            self.assertNotIn(forbidden, src, forbidden)
        self.assertIn('from "@/lib/generated/research-registry.js"', src)


# ═══════════════════════════════════════ 3. rendering without evaluation
@unittest.skipIf(NODE is None or not ESBUILD.exists(),
                 "node and frontend devDependencies (esbuild via wrangler) are required")
class RenderParityTest(unittest.TestCase):
    """renderMdx must produce exactly what compileMDX produces, for real content."""

    @classmethod
    def setUpClass(cls):
        tmp = Path(tempfile.mkdtemp(prefix=".mdx-parity-", dir=FE))
        try:
            entry = tmp / "entry.jsx"
            entry.write_text(textwrap.dedent(f"""
                import fs from "node:fs";
                import path from "node:path";
                import matter from "gray-matter";
                import {{ renderToStaticMarkup }} from "react-dom/server";
                import {{ compileMDX }} from "next-mdx-remote/rsc";
                import remarkGfm from "remark-gfm";
                import {{ renderMdx }} from {json.dumps(str(FE / "lib" / "mdx-render.js"))};
                import {{ mdxComponents }} from {json.dumps(str(FE / "components" / "research" / "MDXContent.jsx"))};
                const dir = {json.dumps(str(CONTENT))};
                const cases = fs.readdirSync(dir).filter((f) => f.endsWith(".mdx"))
                  .map((f) => [f, matter(fs.readFileSync(path.join(dir, f), "utf8")).content]);
                cases.push(
                  ["one-line callout", "Intro.\\n\\n<Callout type=\\"tip\\">Short tip</Callout>\\n\\nAfter."],
                  ["markdown inside callout", "<Callout type=\\"warning\\">\\n\\n**Bold** [link](https://x.y)\\n\\n- one\\n- two\\n\\n</Callout>"],
                  ["gfm", "| A | B |\\n|---|---|\\n| 1 | ~~2~~ |\\n\\nwww.example.com"],
                  ["admin-style markdown", "## Overview\\n\\nSome *text*.\\n\\n1. First\\n2. Second\\n\\n> quote\\n\\n---\\n\\n```js\\nconst a = 1;\\n```"],
                  ["explicit lowercase JSX", "Text with <a href=\\"/x\\">raw</a> and [md](/y)."],
                  ["inline JSX in a sentence", "A sentence with <Callout type=\\"info\\">inline</Callout> inside."],
                  // next-mdx-remote strips JavaScript by default (blockJS); so must renderMdx.
                  ["inline expression", "Two plus two is {{2 + 2}}.\\n\\n<Callout type=\\"info\\">Still here</Callout>"],
                  ["expression-only paragraph", "Before.\\n\\n{{someVariable}}\\n\\nAfter."],
                  ["comment expression", "Visible {{/* hidden */}} text."],
                  ["attribute expression", "<Callout type={{\\"warning\\"}}>Typed by expression</Callout>"],
                  ["spread attribute", "<Callout {{...props}}>Spread</Callout>"],
                  ["import and export", "import X from \\"y\\"\\nexport const a = 1\\n\\n## Still renders\\n\\nBody."],
                  ["expression in list and table", "- one {{1}}\\n- two\\n\\n| a | b |\\n|---|---|\\n| {{x}} | y |"],
                );
                const out = [];
                for (const [name, src] of cases) {{
                  const {{ content }} = await compileMDX({{ source: src, components: mdxComponents,
                    options: {{ mdxOptions: {{ remarkPlugins: [remarkGfm] }} }} }});
                  out.push({{ name, same: renderToStaticMarkup(content) === renderToStaticMarkup(renderMdx(src, mdxComponents)) }});
                }}
                const throws = (fn) => {{ try {{ fn(); return false; }} catch {{ return true; }} }};
                console.log(JSON.stringify({{
                  out,
                  strayBraceThrows: throws(() => renderMdx("Price is {{about 5 lakh", mdxComponents)),
                  unknownComponentThrows: throws(() => renderMdx("<Nope>x</Nope>", mdxComponents)),
                }}));
            """), encoding="utf-8")
            bundle = tmp / "bundle.mjs"
            subprocess.run(
                [str(ESBUILD), str(entry), "--bundle", "--platform=node", "--format=esm",
                 "--jsx=automatic", "--loader:.js=jsx", "--log-level=error", f"--outfile={bundle}",
                 "--banner:js=import{createRequire}from'module';const require=createRequire(import.meta.url);"],
                check=True, cwd=FE, env={"PATH": str(Path(NODE).parent), "NODE_PATH": str(FE / "node_modules")})
            cls.result = json.loads(subprocess.run([NODE, str(bundle)], capture_output=True, text=True,
                                                   check=True, cwd=FE).stdout)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_every_article_renders_byte_identically(self):
        articles = [o for o in self.result["out"] if o["name"].endswith(".mdx")]
        self.assertGreaterEqual(len(articles), 3)
        for o in articles:
            self.assertTrue(o["same"], o["name"])

    def test_edge_cases_render_byte_identically(self):
        for o in self.result["out"]:
            self.assertTrue(o["same"], o["name"])

    def test_invalid_mdx_and_unknown_components_reach_the_next_tier(self):
        # Exactly the inputs compileMDX also fails on (at compile, or for an
        # unknown component while rendering), so renderBody behaves as before.
        self.assertTrue(self.result["strayBraceThrows"])
        self.assertTrue(self.result["unknownComponentThrows"])

    def test_javascript_is_stripped_like_production_not_evaluated(self):
        names = {o["name"]: o["same"] for o in self.result["out"]}
        for case in ("inline expression", "expression-only paragraph", "comment expression",
                     "attribute expression", "spread attribute", "import and export",
                     "expression in list and table"):
            self.assertTrue(names[case], case)


class RendererSourceTest(unittest.TestCase):

    def test_the_renderer_never_evaluates_strings(self):
        src = code(FE / "lib" / "mdx-render.js")
        for forbidden in ("new Function", "eval(", "compileMDX", "@mdx-js/mdx"):
            self.assertNotIn(forbidden, src, forbidden)

    def test_the_article_page_tries_the_safe_renderer_first(self):
        src = code(FE / "app" / "research" / "[slug]" / "page.js")
        body = src[src.index("async function renderBody"):]
        self.assertLess(body.index("renderMdx("), body.index("compileMDX("))
        self.assertLess(body.index("compileMDX("), body.index("marked.parse("))


# ═══════════════════════════════════════ 4. Next.js 15 behaviour, pinned
class NextFifteenBehaviourTest(unittest.TestCase):

    def test_versions(self):
        pkg = json.loads(read(FE / "package.json"))
        deps = pkg["dependencies"]
        self.assertEqual(deps["next"], "15.5.29")
        self.assertEqual(deps["react"], "19.3.1")
        self.assertEqual(deps["react-dom"], "19.3.1")

    def test_registry_is_built_by_next_itself_for_any_build_command(self):
        # Not by an npm script: Vercel's build command can be overridden in its
        # project settings, and OpenNext runs the build itself. next.config.js
        # is loaded by every one of them.
        cfg = read(FE / "next.config.js")
        self.assertIn("PHASE_PRODUCTION_BUILD", cfg)
        self.assertIn("PHASE_DEVELOPMENT_SERVER", cfg)
        self.assertIn("build-research-registry.mjs", cfg)
        self.assertIn("module.exports = (phase) =>", cfg)
        self.assertIn("lib/generated", read(FE / ".gitignore"))
        self.assertIn("renameSync", read(GENERATOR))  # atomic: parallel build workers

    def test_client_router_cache_keeps_next_14_values(self):
        cfg = read(FE / "next.config.js")
        self.assertIn("staleTimes: { dynamic: 30, static: 300 }", cfg)

    def test_route_handlers_are_dynamic_explicitly(self):
        for route in ("app/api/search/suggest/route.js", "app/auth/callback/route.js"):
            self.assertIn('export const dynamic = "force-dynamic";', read(FE / route), route)

    def test_server_supabase_client_awaits_cookies_and_every_caller_awaits_it(self):
        self.assertIn("export async function createClient()", read(FE / "lib" / "supabase-server.js"))
        self.assertIn("await cookies()", read(FE / "lib" / "supabase-server.js"))
        for path in list((FE / "app").rglob("*.js")) + list((FE / "components").rglob("*.jsx")) + list((FE / "lib").glob("*.js")):
            src = read(path)
            if 'from "@/lib/supabase-server"' not in src:
                continue
            bare = re.findall(r"(?<!await )\bcreateClient\(\)", src)
            self.assertEqual(bare, [], str(path.relative_to(FE)))

    def test_route_params_are_awaited(self):
        offenders = []
        for path in (FE / "app").rglob("page.js"):
            src = code(path)
            if re.search(r"export (default )?(async )?function \w+\(\{\s*(params|searchParams)", src):
                offenders.append(str(path.relative_to(FE)))
        self.assertEqual(offenders, [])


# ═══════════════════════════════════════ 5. Cloudflare config stays free and local
class CloudflareConfigTest(unittest.TestCase):

    def test_no_billable_bindings(self):
        wrangler = code(FE / "wrangler.jsonc")
        for binding in ("r2_buckets", "kv_namespaces", "d1_databases", "durable_objects",
                        "queues", "images", "routes", "custom_domain", "ai\"", "vectorize"):
            self.assertNotIn(binding, wrangler, binding)
        self.assertIn('"nodejs_compat"', wrangler)
        self.assertIn('".open-next/assets"', wrangler)

    def test_open_next_uses_no_cache_service(self):
        src = code(FE / "open-next.config.ts")
        self.assertIn("defineCloudflareConfig()", src)
        self.assertNotIn("r2", src.lower())
        self.assertNotIn("kv", src.lower())

    def test_there_is_no_deploy_script(self):
        scripts = json.loads(read(FE / "package.json"))["scripts"]
        self.assertFalse([k for k, v in scripts.items() if "deploy" in k or "deploy" in v])


if __name__ == "__main__":
    unittest.main()
