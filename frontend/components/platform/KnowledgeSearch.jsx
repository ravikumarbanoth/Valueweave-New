// Phase 4 — search across the static knowledge layer AND the researched projection.
//
// EXTENDED, NOT REPLACED. The existing client-side search over
// lib/static-knowledge is untouched: same input, same cards, same behaviour when
// the projection is absent. A second result group is added beneath it.
//
// The two groups stay visually separate because they are different kinds of thing.
// The static layer is editorial (56 hand-written records); the projection is
// researched, sourced and confidence-scored (647 entities). Merging them into one
// ranked list would hide which is which.
//
// Postgres ilike, not the Python SearchEngine's four-mode ladder. The engine's
// EXACT/ALIAS/PREFIX/FUZZY ranking is not reproduced here and the UI does not claim
// it is — see docs/SEARCH_GUIDE.md. Substring matching is honest about being
// substring matching.
"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Search } from "lucide-react";
import { getAllKnowledgeItems } from "@/lib/static-knowledge";
import ConfidenceBadge from "@/components/knowledge/ConfidenceBadge";
import ProvenanceLine from "@/components/knowledge/ProvenanceLine";
import { searchKnowledge, hrefFor, TYPE_BY_URL } from "@/lib/knowledge";

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
];

export default function KnowledgeSearch() {
  const [query, setQuery] = useState("");
  const items = useMemo(() => getAllKnowledgeItems(), []);
  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items.slice(0, 8);
    return items.filter((item) => item.searchText.includes(q)).slice(0, 12);
  }, [items, query]);

  // Researched entities. Debounced, and silently empty when the projection is not
  // deployed — exactly the contract lib/knowledge.js promises.
  const [entities, setEntities] = useState([]);
  // Step 3, Priority 7 — filter the researched results by entity type. Applied
  // server-side in the query rather than by filtering a fetched page, so a filter
  // widens the reachable set instead of narrowing the same twelve rows.
  const [typeFilter, setTypeFilter] = useState("");
  useEffect(() => {
    const q = query.trim();
    if (q.length < 2) {
      setEntities([]);
      return undefined;
    }
    let cancelled = false;
    const timer = setTimeout(async () => {
      const rows = await searchKnowledge(q, { limit: 12, entityType: typeFilter || undefined });
      if (!cancelled) setEntities(rows);
    }, 250);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [query, typeFilter]);

  return (
    <section className="card-base p-5 sm:p-7">
      <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4 mb-5">
        <div>
          <span className="chip bg-teal-100 text-teal-700 border border-teal-200 mb-3">CLIENT-SIDE SEARCH</span>
          <h3 className="font-display font-extrabold text-2xl text-ink">Search the Knowledge Layer</h3>
          <p className="text-sm text-muted mt-2 max-w-2xl leading-relaxed">
            Searches the editorial knowledge layer and, where deployed, the researched
            knowledge base of 647 sourced entities. Rule-based substring matching — no AI.
          </p>
        </div>
        <div className="relative w-full lg:w-80">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search Medak, PMEGP, turmeric, welding..."
            className="input-field !pl-10"
          />
        </div>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {results.map((item) => (
          <Link key={`${item.type}-${item.slug}`} href={item.href} className="rounded-2xl bg-stone-50 border border-stone-150 p-4 hover:border-amber-300 hover:bg-amber-50 transition-colors group">
            <span className="chip bg-white text-stone-500 border border-stone-200 text-[10px] mb-3">{item.typeLabel}</span>
            <h4 className="font-display font-bold text-sm text-ink group-hover:text-amber-700 transition-colors">{item.name}</h4>
            <p className="text-xs text-muted mt-2 line-clamp-3 leading-relaxed">
              {item.summary || item.description || item.purpose || item.overview}
            </p>
          </Link>
        ))}
      </div>

      {/* ── Researched entities, kept visually separate from the editorial layer ── */}
      {entities.length > 0 && (
        <div data-testid="search-researched" className="mt-6 pt-5 border-t border-stone-150">
          <div className="flex items-baseline justify-between gap-3 mb-3">
            <h4 className="font-display font-extrabold text-base text-ink">
              Researched knowledge base
            </h4>
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
