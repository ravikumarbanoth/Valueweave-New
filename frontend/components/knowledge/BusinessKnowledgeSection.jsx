// Phase 6 — researched knowledge for one business idea.
//
// Spans four packages through the knowledge graph:
//   Package004/008  comparable researched businesses (BusinessOpportunity, MSME)
//   Package007      schemes that support them        (SUPPORTED_BY_SCHEME)
//   Package006      skills they require             (REQUIRES_SKILL)
//   Package001      districts they employ in        (GENERATES_EMPLOYMENT)
//
// LINKS, NEVER MERGES.
// An idea-library entry is editorial: written to inspire, carrying no source and no
// confidence score. A Package004/008 row is researched: sourced, provenance-carried,
// confidence-scored. They are different kinds of claim about the world. Presenting
// them as one list would launder the first into the credibility of the second, so
// every card says which it is and the section header says it too.
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import KnowledgeCard from "./KnowledgeCard";
import KnowledgeCardGrid from "./KnowledgeCardGrid";
import TrustPanel from "./TrustPanel";
import { getNeighbours, resolveTerms, hrefFor } from "@/lib/knowledge";

export default function BusinessKnowledgeSection({ sectorLabel, skills = [], districts = [] }) {
  const [state, setState] = useState({ loading: true });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      // The sector crosswalk resolves 11 of 22 idea sectors (Step 0). When it
      // misses, that is reported rather than hidden: half the library has no
      // researched industry to hang off yet.
      const [sectorHit, skillHits, districtHits] = await Promise.all([
        resolveTerms("sector", sectorLabel ? [sectorLabel] : []),
        resolveTerms("skill", skills),
        resolveTerms("district", districts),
      ]);

      const industry = sectorHit.resolved[0] || null;

      // Businesses in this industry, reached through PART_OF.
      const members = industry
        ? await getNeighbours(industry.global_entity_id, {
            relationshipType: "PART_OF",
            direction: "in",
            limit: 40,
          })
        : [];
      const businesses = members
        .filter(({ entity }) => ["MSME", "BusinessOpportunity"].includes(entity.entity_type))
        .slice(0, 6);

      // Schemes reachable from those businesses.
      const schemeLists = await Promise.all(
        businesses.map(({ entity }) =>
          getNeighbours(entity.global_entity_id, {
            relationshipType: "SUPPORTED_BY_SCHEME",
            direction: "out",
            limit: 8,
          })
        )
      );
      const seen = new Set();
      const schemes = [];
      schemeLists.flat().forEach(({ entity, edge }) => {
        if (seen.has(entity.global_entity_id)) return;
        seen.add(entity.global_entity_id);
        schemes.push({ entity, edge });
      });

      if (!cancelled) {
        setState({
          loading: false,
          industry,
          businesses,
          schemes: schemes.slice(0, 6),
          skillHits,
          districtHits,
        });
      }
    })().catch(() => {
      if (!cancelled) setState({ loading: false, failed: true });
    });
    return () => {
      cancelled = true;
    };
  }, [sectorLabel, JSON.stringify(skills), JSON.stringify(districts)]);

  if (state.loading) {
    return (
      <section className="card-base p-5 mb-5" data-testid="business-knowledge-loading">
        <p className="text-xs text-muted">Loading…</p>
      </section>
    );
  }

  if (state.failed) {
    return (
      <section className="card-base p-5 mb-5" data-testid="business-knowledge-failed">
        <p className="text-xs text-muted">Couldn&apos;t load this just now. Try refreshing the page.</p>
      </section>
    );
  }

  const { industry, businesses = [], schemes = [], skillHits, districtHits } = state;
  const nothing = businesses.length === 0 && schemes.length === 0;

  return (
    <section data-testid="business-knowledge" className="card-base p-5 sm:p-7 mb-5">
      <span className="chip bg-teal-100 text-teal-700 border border-teal-200 mb-3">
        REAL EXAMPLES
      </span>
      <h2 className="font-display font-extrabold text-xl text-ink">
        Businesses like this that already exist
      </h2>
      <p className="text-sm text-muted mt-2 mb-4 max-w-2xl leading-relaxed">
        The idea above was written by our team to get you thinking. Below are{" "}
        <strong className="text-ink">real businesses</strong> in the same sector that we
        have researched, the government schemes that support them, and where they
        operate. Two different things, kept separate on purpose.
      </p>

      {nothing ? (
        <KnowledgeCardGrid
          status="NO_DATA_SOURCE"
          testId="business-knowledge"
          note={
            industry
              ? `We have not connected any businesses to ${industry.canonical_name} yet.`
              : `We have not matched "${sectorLabel}" to an industry we have researched yet. The idea above still stands — we just cannot show you comparable businesses for it.`
          }
        />
      ) : (
        <>
          <TrustPanel hasUnverified className="mb-5" />

          {businesses.length > 0 && (
            <div className="mb-5">
              <h3 className="label-display">
                Businesses in {industry?.canonical_name}
                <span className="text-stone-400 font-normal tabular-nums ml-1.5">
                  {businesses.length}
                </span>
              </h3>
              <KnowledgeCardGrid columns="sm:grid-cols-2">
                {businesses.map(({ entity }) => (
                  <KnowledgeCard
                    key={entity.global_entity_id}
                    testId="business-comparable"
                    title={entity.canonical_name}
                    type={entity.entity_type === "MSME" ? "small business" : "business idea"}
                    confidence={entity.confidence_score}
                    provenance={{ package: entity.source_package, rowId: entity.package_local_id }}
                    href={hrefFor(entity)}
                  />
                ))}
              </KnowledgeCardGrid>
            </div>
          )}

          {schemes.length > 0 && (
            <div className="mb-5">
              <h3 className="label-display">
                Schemes supporting them
                <span className="text-stone-400 font-normal tabular-nums ml-1.5">
                  {schemes.length}
                </span>
              </h3>
              <KnowledgeCardGrid columns="sm:grid-cols-2">
                {schemes.map(({ entity, edge }) => (
                  <KnowledgeCard
                    key={entity.global_entity_id}
                    testId="business-scheme"
                    title={entity.canonical_name}
                    type="government scheme"
                    confidence={entity.confidence_score}
                    reason="Supports businesses like this one"
                    provenance={{
                      package: edge?.provenance_package,
                      dataset: edge?.provenance_dataset,
                      rowId: edge?.provenance_row_id,
                    }}
                    href={hrefFor(entity)}
                  />
                ))}
              </KnowledgeCardGrid>
            </div>
          )}
        </>
      )}

      {/* ── Step 4: the resolved half ────────────────────────────────────────
          This component already resolved every idea's skills and districts
          through the crosswalk, and then rendered only the ones that FAILED.
          The successes — real graph entities with detail pages — were computed
          and thrown away, so an idea listing "Welding, Food Processing" showed
          the reader nothing they could click.

          Both directions are now shown, and the contrast is the useful part: a
          user can see at a glance how much of this idea the knowledge base
          actually covers. */}
      {(skillHits?.resolved?.length > 0 || districtHits?.resolved?.length > 0) && (
        <div className="mt-4 pt-4 border-t border-stone-150" data-testid="idea-resolved">
          <h3 className="label-display">Explore these</h3>
          <div className="flex flex-wrap gap-1.5">
            {[
              ...(skillHits?.resolved || []).map((r) => ["skill", r]),
              ...(districtHits?.resolved || []).map((r) => ["district", r]),
            ]
              .slice(0, 14)
              .map(([kind, r]) => (
                <Link
                  key={`${kind}-${r.global_entity_id}`}
                  href={hrefFor({
                    global_entity_id: r.global_entity_id,
                    entity_type: r.entity_type,
                  })}
                  data-testid="idea-resolved-link"
                  title={`"${r.term}" matched ${r.canonical_name} by ${String(
                    r.match_method || ""
                  ).toLowerCase()}`}
                  className="chip bg-teal-50 text-teal-700 border border-teal-200 hover:border-teal-400 transition-colors text-[11px]"
                >
                  {r.canonical_name || r.term}
                </Link>
              ))}
          </div>
          <p className="text-[10px] text-stone-400 mt-2 leading-relaxed">
            Each one has its own page with the full details and everything connected
            to it.
          </p>
        </div>
      )}

      {/* Skill and district resolution, reported either way. An unresolved skill is
          a real skill the knowledge base has not collected — worth saying. */}
      {(skillHits?.unresolved?.length > 0 || districtHits?.unresolved?.length > 0) && (
        <div className="mt-4 pt-4 border-t border-stone-150">
          <h3 className="label-display">We have not covered these yet</h3>
          <div className="flex flex-wrap gap-1.5">
            {[...(skillHits?.unresolved || []), ...(districtHits?.unresolved || [])]
              .slice(0, 12)
              .map((u) => (
                <span
                  key={u.term}
                  title={u.reason}
                  className="chip bg-stone-100 text-stone-500 border border-stone-200 text-[11px]"
                >
                  {u.term}
                </span>
              ))}
          </div>
          <p className="text-[10px] text-stone-400 mt-2 leading-relaxed">
            These are real skills and places — we have just not gathered information on
            them yet. It is a gap on our side, not a comment on them.
          </p>
        </div>
      )}
    </section>
  );
}
