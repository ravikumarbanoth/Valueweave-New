// "Latest knowledge" — the newest rows in the projection (Step 3, Priority 1).
//
// Ordered by the sync's own timestamp, so it shows what actually landed in the
// database rather than when a researcher wrote it. Every item links to its detail
// page and names its source package.
import Link from "next/link";
import { hrefFor } from "@/lib/knowledge";
import SourceBadge from "./SourceBadge";
import ConfidenceBadge from "./ConfidenceBadge";

export default function LatestKnowledgeCard({ items = [] }) {
  if (items.length === 0) return null;
  return (
    <section data-testid="latest-knowledge" className="card-base p-5 mb-6">
      <div className="flex items-center justify-between gap-3 mb-3">
        <div>
          <h2 className="font-display font-bold text-ink">Recently added</h2>
          <p className="text-xs text-muted mt-0.5">The newest additions to our research</p>
        </div>
        <Link href="/knowledge" className="text-[12px] text-muted underline hover:text-ink whitespace-nowrap">
          Explore all →
        </Link>
      </div>
      <ul className="flex flex-col divide-y divide-stone-100">
        {items.slice(0, 6).map((e) => (
          <li key={e.global_entity_id}>
            <Link href={hrefFor(e)} data-testid="latest-knowledge-item"
                  className="flex items-center justify-between gap-3 py-2.5 hover:bg-stone-50 -mx-2 px-2 rounded-lg transition-colors">
              <span className="text-sm text-ink truncate">{e.canonical_name}</span>
              <span className="flex items-center gap-2 shrink-0">
                <SourceBadge sourcePackage={e.source_package} />
                <ConfidenceBadge confidence={e.confidence_score} />
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
