#!/usr/bin/env python3
"""
Run the shipped frontend JavaScript from a Python test.

WHY THE TESTS SHELL OUT TO NODE
-------------------------------
The matcher is JavaScript. A Python reimplementation of it would be a second
matcher that passes its own tests while the one users hit is broken — which is
the exact failure this repository has already paid for once, in the search
outage where a ranking engine nobody called sat next to an `ilike` everybody
did. These tests run the real modules.

WHY THIS FILE EXISTS RATHER THAN A COPY PER SUITE
-------------------------------------------------
Each suite used to stage the two or three lib files it needed by name. That
worked until a lib file imported a new one: `search-vocabulary.js` picked up
`./search/multilingual.js`, the staging list did not, and thirteen tests failed
with ERR_MODULE_NOT_FOUND — a defect in the harness reported as a defect in the
code under test.

So the whole of `frontend/lib` is mirrored, not a hand-listed subset. Adding an
import to a lib module can no longer break a suite that does not mention it.

    from tests.js_harness import JsHarness

    h = JsHarness()                       # mirrors frontend/lib into a tmpdir
    h.dataset("entities.json", rows)      # anything the script needs to read
    out = h.run('''
        const { rankEntities } = await import("$LIB/knowledge-search.js");
        console.log(JSON.stringify(rankEntities(...)));
    ''')                                  # parsed JSON on stdout
"""

import csv
import json
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FE = ROOT / "frontend"
LIB = FE / "lib"
ENTITIES_CSV = ROOT / "knowledge_graph" / "entities" / "entities.csv"
RELATIONSHIPS_CSV = ROOT / "knowledge_graph" / "relationships" / "relationships.csv"

NODE = shutil.which("node")
NODE_REASON = ("node is required — the code under test is JavaScript, and "
               "testing a Python copy of it would prove nothing")


def entities():
    """The real graph, as the frontend receives it (confidence is a number)."""
    with open(ENTITIES_CSV, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        row["confidence_score"] = int(row["confidence_score"] or 0)
    return rows


def relationships():
    with open(RELATIONSHIPS_CSV, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class JsHarness:
    """A temporary mirror of frontend/lib that plain `node` can import.

    The `@/lib/x` alias is Next's, resolved by the bundler, and bare node knows
    nothing about it. Every occurrence is rewritten to a relative path as the
    tree is copied — including inside subdirectories, where the alias has to
    climb back out.
    """

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.lib = self.dir / "lib"
        self._mirror()

    def _mirror(self):
        for src in LIB.rglob("*.js"):
            rel = src.relative_to(LIB)
            dst = self.lib / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            # `@/lib/foo` from lib/search/x.js has to become `../foo.js`.
            depth = len(rel.parts) - 1
            prefix = "./" if depth == 0 else "../" * depth
            text = src.read_text(encoding="utf-8")
            text = text.replace("@/lib/", prefix).replace('@/components/', prefix)
            dst.write_text(text, encoding="utf-8")

    def dataset(self, name, rows):
        """Write JSON the script can read back. Returns the absolute path."""
        path = self.dir / name
        path.write_text(json.dumps(rows), encoding="utf-8")
        return path

    def run(self, body, timeout=90):
        """Execute an ESM snippet and parse its stdout as JSON.

        `$LIB` and `$DIR` expand to the mirrored lib and the scratch directory,
        so a caller never has to know where the temporary copy landed.
        """
        script = self.dir / "run.mjs"
        source = textwrap.dedent(body).replace("$LIB", str(self.lib)).replace("$DIR", str(self.dir))
        script.write_text('import fs from "node:fs";\n' + source, encoding="utf-8")
        result = subprocess.run([NODE, str(script)], capture_output=True,
                                text=True, timeout=timeout)
        if result.returncode != 0:
            raise AssertionError(f"node failed:\n{result.stdout}\n{result.stderr}")
        return json.loads(result.stdout)

    def cleanup(self):
        self._tmp.cleanup()
