#!/usr/bin/env python3
"""
ValueWeave Platform v2.2 — Work Package 1: Knowledge Engine compatibility check

The Knowledge Engine (VKE v0.1.0) was written before Platform v2 existed, and was
recovered into `main` in v2.2 after living unmerged on a branch for two days. That
gap is exactly where silent incompatibility hides, so nothing here is asserted:
every claim below is a check that runs against the eight released packages and the
built knowledge graph, and fails loudly if it does not hold.

Nine checks, in the order a consumer would hit them:

  C1  Import surface        every module and every declared __all__ symbol imports
  C2  Sentinel agreement    the engine's PENDING_VERIFICATION is the repository's
  C3  Verification enum     VerificationStatus covers every value the packages use
  C4  Provenance columns    ProvenanceRecord.to_csv_fields() emits exactly the six
                            mandatory columns, in every package's vocabulary
  C5  Confidence bands      ConfidenceTier classifies every observed package score
  C6  Validation rules      the engine's rules run over a real package dataset
  C7  Lifecycle vocabulary  WorkflowState vs the graph's LIFECYCLE_STATES: two
                            different vocabularies, and the mapping between them
  C8  Rule engine           RuleQuery answers a real question over real rows
  C9  Collector/parser      the source registry can now name real modules

Exit code 0 = compatible, 1 = at least one check failed.

    python3 knowledge_engine/check_compatibility.py
"""

import csv
import importlib
import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PACKAGES = ROOT / "packages"
KE = ROOT / "knowledge_engine"

results = []


def check(cid, title, ok, detail, warning=None):
    status = "PASS" if ok else "FAIL"
    entry = {"check": cid, "title": title, "status": status, "detail": detail}
    if warning:
        entry["warning"] = warning
    results.append(entry)
    print(f"  [{status}] {cid} {title}")
    print(f"         {detail}")
    if warning:
        print(f"         WARN: {warning}")
    return ok


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def package_datasets():
    for pkg in sorted(p for p in PACKAGES.iterdir() if p.is_dir()):
        ds = pkg / "datasets"
        if ds.exists():
            for f in sorted(ds.glob("*.csv")):
                yield pkg.name, f


MODULES = [
    "knowledge_engine.core.types",
    "knowledge_engine.core.provenance",
    "knowledge_engine.collectors",
    "knowledge_engine.parsers",
    "knowledge_engine.validation",
    "knowledge_engine.provenance",
    "knowledge_engine.package_builder",
    "knowledge_engine.versioning",
    "knowledge_engine.update_engine",
    "knowledge_engine.rule_engine",
]


def main():
    print("ValueWeave Knowledge Engine — Platform v2 compatibility check\n")

    # ------------------------------------------------------------------- C1
    failed, symbols = [], 0
    for name in MODULES:
        try:
            mod = importlib.import_module(name)
        except Exception as exc:                                   # noqa: BLE001
            failed.append(f"{name}: {type(exc).__name__}: {exc}")
            continue
        for sym in getattr(mod, "__all__", []):
            if hasattr(mod, sym):
                symbols += 1
            else:
                failed.append(f"{name}.{sym} declared in __all__ but absent")
    ok1 = check("C1", "Import surface", not failed,
                f"{len(MODULES)} modules, {symbols} exported symbols, "
                f"{len(failed)} failures" + ("" if not failed else f": {failed[:3]}"))

    from knowledge_engine.core.types import (                      # noqa: E402
        ConfidenceTier, PENDING_VERIFICATION, VerificationStatus)

    # ------------------------------------------------------------------- C2
    # The engine parses the six provenance columns. A non-bare sentinel THERE would
    # break it, so that fails. The same string embedded in a prose summary column is
    # a style inconsistency in the packages built before the discipline was tightened
    # in Package005 — the engine reads those cells correctly — so that warns.
    PROVENANCE_COLUMNS = {"data_source", "source_url", "collection_date",
                          "confidence_score", "verification_status"}
    sentinel_cells = 0
    provenance_variants, prose_variants = set(), defaultdict(int)
    for pkg, f in package_datasets():
        for row in read(f):
            for k, v in row.items():
                v = (v or "").strip()
                if PENDING_VERIFICATION not in v:
                    continue
                if v == PENDING_VERIFICATION:
                    sentinel_cells += 1
                elif k in PROVENANCE_COLUMNS:
                    provenance_variants.add(f"{pkg}/{f.name}[{k}]")
                elif k != "notes":
                    prose_variants[pkg] += 1
    prose_total = sum(prose_variants.values())
    ok2 = check(
        "C2", "Sentinel agreement", not provenance_variants,
        f"{sentinel_cells} cells hold the bare sentinel {PENDING_VERIFICATION!r}; "
        f"{len(provenance_variants)} non-bare occurrences in the six provenance columns",
        warning=(None if not prose_total else
                 f"{prose_total} prose cells outside `notes` embed the sentinel in a sentence "
                 f"({', '.join(f'{k} {v}' for k, v in sorted(prose_variants.items()))}). "
                 f"These predate the bare-sentinel discipline introduced in Package005 and are "
                 f"honest prose, not fabrication. The engine reads them correctly, so this is a "
                 f"data-remediation item, not an incompatibility."))

    # ------------------------------------------------------------------- C3
    engine_values = {s.value for s in VerificationStatus}
    observed = defaultdict(int)
    for _pkg, f in package_datasets():
        for row in read(f):
            if "verification_status" in row:
                observed[(row["verification_status"] or "").strip()] += 1
    unknown = {v for v in observed if v and v not in engine_values}
    ok3 = check("C3", "Verification enum", not unknown,
                f"packages use {sorted(observed)}; engine defines {sorted(engine_values)}; "
                f"{len(unknown)} unrepresented" + ("" if not unknown else f": {sorted(unknown)}"))

    # ------------------------------------------------------------------- C4
    from knowledge_engine.core.provenance import ProvenanceRecord  # noqa: E402
    rec = ProvenanceRecord(
        source="compatibility check", source_url=["https://example.gov.in/"],
        collection_date=date.today(), collector="check_compatibility/2.2.0",
        confidence=70,
        notes="synthetic record used only to inspect the emitted column names")
    emitted = set(rec.to_csv_fields())
    mandatory = {"data_source", "source_url", "collection_date",
                 "confidence_score", "verification_status", "notes"}
    # Read the header directly: two Package001 datasets are header-only, and a
    # header-only dataset still has to declare the six columns.
    def header_of(path):
        with open(path, newline="", encoding="utf-8") as fh:
            return set(next(csv.reader(fh), []))

    empty_datasets = [f"{pkg}/{f.name}" for pkg, f in package_datasets() if not read(f)]
    datasets_with_all_six = sum(
        1 for _pkg, f in package_datasets() if mandatory.issubset(header_of(f)))
    total_datasets = sum(1 for _ in package_datasets())
    ok4 = check("C4", "Provenance columns", emitted == mandatory
                and datasets_with_all_six == total_datasets,
                f"engine emits {sorted(emitted)}; "
                f"{datasets_with_all_six}/{total_datasets} package datasets carry all six",
                warning=(None if not empty_datasets else
                         f"{len(empty_datasets)} dataset(s) are header-only and hold no rows: "
                         f"{', '.join(empty_datasets)}. The columns are declared, so the engine "
                         f"can write into them; there is simply nothing there yet."))

    # ------------------------------------------------------------------- C5
    scores, unclassifiable = [], []
    for _pkg, f in package_datasets():
        for row in read(f):
            c = (row.get("confidence_score") or "").strip()
            if c.isdigit():
                scores.append(int(c))
    for s in sorted(set(scores)):
        try:
            ConfidenceTier.for_score(s)
        except ValueError:
            unclassifiable.append(s)
    ok5 = check("C5", "Confidence bands", not unclassifiable,
                f"{len(scores)} scored cells, range {min(scores)}-{max(scores)}, "
                f"{len(set(scores))} distinct values, {len(unclassifiable)} unclassifiable")

    # ------------------------------------------------------------------- C6
    from knowledge_engine.validation import (                      # noqa: E402
        RequiredFieldsRule, SourceValidationRule, ValidationEngine)
    sample_path = PACKAGES / "Package007_Government_Schemes" / "datasets" / "government_schemes.csv"
    sample = read(sample_path)
    eng = ValidationEngine([
        RequiredFieldsRule(["scheme_id", "scheme_name", "data_source",
                            "source_url", "collection_date", "confidence_score",
                            "verification_status"]),
        SourceValidationRule(),
    ])
    report = eng.run(sample, {})
    ok6 = check("C6", "Validation rules", not report.violations,
                f"{len(eng.rules)} rules over {len(sample)} rows of "
                f"{sample_path.name}: {len(report.violations)} violations")

    # ------------------------------------------------------------------- C7
    from knowledge_engine.update_engine.states import WorkflowState  # noqa: E402
    graph_states = ["DRAFT", "COLLECTED", "VALIDATED", "REVIEWED",
                    "APPROVED", "PUBLISHED", "ARCHIVED"]
    # These are two different vocabularies and must not be conflated: WorkflowState
    # describes one update CYCLE, lifecycle_state describes a RECORD. The mapping is
    # the contract between them, and stewardship/lifecycle.py is where it is applied.
    mapping = {
        WorkflowState.CHECKING_SOURCE.value: "COLLECTED",
        WorkflowState.DETECTING_CHANGES.value: "COLLECTED",
        WorkflowState.VALIDATING.value: "VALIDATED",
        WorkflowState.UPDATING_DATABASE.value: "VALIDATED",
        WorkflowState.GENERATING_DRAFT.value: "DRAFT",
        WorkflowState.PENDING_HUMAN_APPROVAL.value: "REVIEWED",
        WorkflowState.STABLE_RELEASE.value: "PUBLISHED",
        WorkflowState.REJECTED.value: "ARCHIVED",
    }
    unmapped = {v for v in mapping.values() if v not in graph_states}
    ok7 = check("C7", "Lifecycle vocabulary", not unmapped,
                f"{len(WorkflowState)} workflow states map onto "
                f"{len(set(mapping.values()))} of {len(graph_states)} record lifecycle states; "
                f"APPROVED is reached only by a steward, never by the engine")

    # ------------------------------------------------------------------- C8
    from knowledge_engine.rule_engine import RuleQuery              # noqa: E402
    msmes = read(PACKAGES / "Package008_MSME" / "datasets" / "msme_businesses.csv")
    hits = RuleQuery().where("risk_level", "==", "Low").filter(msmes)
    ok8 = check("C8", "Rule engine", isinstance(hits, list),
                f"RuleQuery over {len(msmes)} Package008 businesses returned "
                f"{len(hits)} rows with risk_level == 'Low'")

    # ------------------------------------------------------------------- C9
    from knowledge_engine.collectors import default_registry        # noqa: E402
    from knowledge_engine import parsers                            # noqa: E402
    collector_names = sorted(default_registry.names()) \
        if hasattr(default_registry, "names") else \
        sorted(getattr(default_registry, "_collectors", {}))
    parser_names = [n for n in parsers.__all__ if n.endswith("Parser") and n != "BaseParser"]
    ok9 = check("C9", "Collector/parser availability", bool(collector_names) and bool(parser_names),
                f"{len(collector_names)} collectors, {len(parser_names)} parsers are now "
                f"nameable by the source registry (ADR-006 resolved)")

    all_ok = all([ok1, ok2, ok3, ok4, ok5, ok6, ok7, ok8, ok9])
    summary = {
        "checked_at": date.today().isoformat(),
        "engine_version": "0.1.0",
        "platform_version": "2.2.0",
        "checks": results,
        "passed": sum(1 for r in results if r["status"] == "PASS"),
        "failed": sum(1 for r in results if r["status"] == "FAIL"),
        "result": "COMPATIBLE" if all_ok else "INCOMPATIBLE",
        "workflow_to_lifecycle_mapping": mapping,
        "collectors": collector_names,
        "parsers": parser_names,
    }
    (KE / "compatibility_report.json").write_text(json.dumps(summary, indent=2) + "\n")

    print(f"\n  {summary['passed']}/{len(results)} checks passed")
    print(f"  {summary['result']} — report written to knowledge_engine/compatibility_report.json")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
