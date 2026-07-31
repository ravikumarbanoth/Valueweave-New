// Knowledge search — Platform v3.0, Step 4.
//
// WHAT CHANGED, AND WHY IT MATTERED
// ---------------------------------
// This component used to search two things at once. The primary result grid —
// the one that filled before you typed anything and sat at the top — came from
// lib/static-knowledge.js: 56 hand-written JSON records with no source, no
// confidence and no provenance. The researched projection, 647 sourced entities
// across Packages 001–008, appeared underneath as a secondary group and only
// after two characters were typed.
//
// So the platform's weakest data answered first and its strongest answered
// second. Every one of the seven static types — districts, industries,
// manufacturing, products, training, skills, schemes — has a researched
// counterpart now, so the static group is gone and the projection is the search.
//
// The static detail routes at /knowledge/<plural>/<slug> still resolve. Nothing
// links to them from here any more, but breaking 56 live URLs to make a point
// about data quality would be a worse trade than leaving them reachable.
//
// STILL NOT THE PYTHON SEARCH ENGINE.
// Postgres ilike, not the EXACT/ALIAS/PREFIX/FUZZY ladder in search/index.py —
// see docs/SEARCH_GUIDE.md. Substring matching is honest about being substring
// matching, and the copy below says so.
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Search } from "lucide-react";
import ConfidenceBadge from "@/components/knowledge/ConfidenceBadge";
import ProvenanceLine from "@/components/knowledge/ProvenanceLine";
import KnowledgeEmptyState from "@/components/knowledge/KnowledgeEmptyState";
import { searchKnowledge, hrefFor } from "@/lib/knowledge";

//: The filter axis. Entity types, not packages: a user searching for "welding"
//: wants to narrow to skills, not to Package006.
const SEARCH_FILTERS = [
  { value: "", label: "All" },
  { value: "BusinessOpportunity", label: "Businesses" },
  { value: "Skill", label: "Skills" },
  { value: "GovernmentScheme", label: "Schemes" },
  { value: "District", label: "Districts" },
  { value: "Industry", label: "Industries" },
  { value: "Crop", label: "Agriculture" },
  { value: "MSME", label: "MSMEs" },
  { value: "Machinery", label: "Machinery" },
  { value: "TrainingProvider", label: "Training" },
];

export default function KnowledgeSearch() {
  const [query, setQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [entities, setEntities] = useState([]);
  // "idle" before the first search, so an empty grid never reads as "no results"
  // when the truth is "you have not searched yet".
  const [state, setState] = useState("idle");

  useEffect(() => {
    const q = query.trim();
    if (q.length < 2) {
      setEntities([]);
      setState("idle");
      return undefined;
    }
    let cancelled = false;
    setState("searching");
    const timer = setTimeout(async () => {
      // Never throws — returns [] when the projection is not deployed.
      const rows = await searchKnowledge(q, { limit: 24, entityType: typeFilter || undefined });
      if (cancelled) return;
      setEntities(rows);
      setState(rows.length > 0 ? "results" : "empty");
    }, 250);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [query, typeFilter]);

  return (
    <section className="card-base p-5 sm:p-7" data-testid="knowledge-search">
      <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4 mb-5">
        <div>
          <span className="chip bg-teal-100 text-teal-700 border border-teal-200 mb-3">
            RESEARCHED KNOWLEDGE
          </span>
          <h3 className="font-display font-extrabold text-2xl text-ink">Search the Knowledge Base</h3>
          <p className="text-sm text-muted mt-2 max-w-2xl leading-relaxed">
            Searches 647 sourced entities across Packages 001–008. Every result carries
            the package it came from and a confidence score. Rule-based substring
            matching — no AI, and no ranking beyond source confidence.
          </p>
        </div>
        <div className="relative w-full lg:w-80">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search Medak, PMEGP, turmeric, welding..."
            aria-label="Search the researched knowledge base"
            data-testid="knowledge-search-input"
            className="input-field !pl-10"
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-1.5 mb-5" data-testid="knowledge-search-filters">
        {SEARCH_FILTERS.map((f) => (
          <button
            key={f.value || "all"}
            type="button"
            onClick={() => setTypeFilter(f.value)}
            aria-pressed={typeFilter === f.value}
            className={`chip border transition-colors ${
              typeFilter === f.value
                ? "bg-ink text-white border-ink"
                : "bg-white text-stone-600 border-stone-200 hover:border-stone-300"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {state === "idle" && (
        <p className="text-sm text-muted text-center py-8" data-testid="knowledge-search-idle">
          Type at least two characters to search the researched knowledge base.{" "}
          <Link href="/knowledge" className="underline hover:text-ink">
            Or browse by category →
          </Link>
        </p>
      )}

      {state === "searching" && (
        <p className="text-sm text-muted text-center py-8">Searching…</p>
      )}

      {state === "empty" && (
        <KnowledgeEmptyState
          reason="NO_MATCH"
          entityLabel={
            typeFilter
              ? (SEARCH_FILTERS.find((f) => f.value === typeFilter)?.label || "records").toLowerCase()
              : "records"
          }
          query={query.trim()}
        />
      )}

      {state === "results" && (
        <div data-testid="search-researched">
          <div className="flex items-baseline justify-between gap-3 mb-3">
            <h4 className="font-display font-extrabold text-base text-ink">Results</h4>
            <span className="text-xs text-stone-400 tabular-nums">
              {entities.length} {entities.length === 1 ? "entity" : "entities"}
            </span>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {entities.map((e) => (
              <Link
                key={e.global_entity_id}
                href={hrefFor(e)}
                data-testid="search-entity"
                className="rounded-2xl bg-white border border-stone-150 p-4 hover:border-amber-300 hover:bg-amber-50 transition-colors block"
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <span className="chip bg-stone-50 text-stone-500 border border-stone-200 text-[10px]">
                    {e.entity_type}
                  </span>
                  <ConfidenceBadge confidence={e.confidence_score} />
                </div>
                <h5 className="font-display font-bold text-sm text-ink leading-snug">
                  {e.canonical_name}
                </h5>
                <ProvenanceLine
                  package={e.source_package}
                  rowId={e.package_local_id}
                  className="mt-2"
                />
              </Link>
            ))}
          </div>
          <p className="text-[10px] text-stone-400 mt-3 leading-relaxed">
            Sourced rows with provenance and a confidence score. None has been reviewed
            by a person — confidence describes source strength, not correctness.
          </p>
        </div>
      )}
    </section>
  );
}
