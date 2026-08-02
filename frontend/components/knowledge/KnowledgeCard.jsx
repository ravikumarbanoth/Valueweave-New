// One knowledge entity or recommendation, with its provenance and confidence.
//
// Deliberately styled with the tokens the app already uses (card-base, chip,
// text-ink, text-muted) so it sits inside existing pages without redesigning them.
//
// STEP 4 — THE FIFTH ELEMENT
// --------------------------
// The brief requires every recommendation to show five things: reason,
// confidence, supporting knowledge, related entities, and source package. Four
// were here. `supporting_entities` — the graph entities the rule actually
// traversed to reach this conclusion — was read only to pull a package name out
// of the first one, and the entities themselves were dropped.
//
// They are now rendered as links. That is the difference between "we recommend
// this because you know welding" and a recommendation you can walk backwards
// through: the skill, the business it unlocked, the district it employs in, each
// one a page.
//
// A nested <a> inside an <a> is invalid HTML and React will warn, so when a card
// is itself a link the related row sits OUTSIDE it, in a shared wrapper. Same
// visual card, two elements.
import Link from "next/link";

import ConfidenceBadge from "./ConfidenceBadge";
import ProvenanceLine from "./ProvenanceLine";

export default function KnowledgeCard({
  title,
  type,
  reason,
  confidence,
  matchScore,
  href,
  provenance,
  related = [],
  footer,
  testId,
}) {
  const links = (related || []).filter((r) => r && r.href && r.label);

  const body = (
    <>
      <div className="flex items-start justify-between gap-2 mb-2">
        {type && <span className="chip bg-white text-stone-500 border border-stone-200 text-[10px]">{type}</span>}
        <div className="flex items-center gap-1.5 shrink-0">
          {matchScore !== undefined && matchScore !== null && (
            <span
              title="How closely this fits the skills and district on your profile. This is about you — it is not a rating of how reliable the information is."
              className="chip bg-teal-50 text-teal-700 border border-teal-200 text-[10px] tabular-nums"
            >
              {Math.round(Number(matchScore))}% match
            </span>
          )}
          <ConfidenceBadge confidence={confidence} />
        </div>
      </div>

      <h4 className="font-display font-bold text-sm text-ink leading-snug">{title}</h4>

      {/* The reason is why this is on screen at all. Never truncated away. */}
      {reason && <p className="text-xs text-muted mt-2 leading-relaxed">{reason}</p>}

      {footer}

      {provenance && (
        <ProvenanceLine
          package={provenance.package}
          dataset={provenance.dataset}
          rowId={provenance.rowId}
          className="mt-2.5"
        />
      )}
    </>
  );

  const relatedRow = links.length > 0 && (
    <div
      data-testid={testId ? `${testId}-related` : "knowledge-card-related"}
      className="mt-2.5 pt-2.5 border-t border-stone-200/70"
    >
      <p className="text-[10px] uppercase tracking-wider text-stone-400 font-display font-bold mb-1.5">
        Supporting knowledge
      </p>
      <div className="flex flex-wrap gap-1.5">
        {links.slice(0, 6).map((r) => (
          <Link
            key={`${r.href}-${r.label}`}
            href={r.href}
            data-testid="knowledge-card-related-link"
            title={r.detail || undefined}
            className="chip bg-white text-stone-600 border border-stone-200 hover:border-amber-300 hover:text-amber-700 transition-colors text-[10px]"
          >
            {r.label}
          </Link>
        ))}
      </div>
    </div>
  );

  const shell = "rounded-2xl bg-stone-50 border border-stone-150 p-4 h-full transition-colors";

  if (!href) {
    return (
      <div data-testid={testId} className={shell}>
        {body}
        {relatedRow}
      </div>
    );
  }

  // The card links, the chips link, and neither is nested inside the other.
  if (relatedRow) {
    return (
      <div data-testid={testId} className={shell}>
        <Link href={href} className="block group">
          {body}
        </Link>
        {relatedRow}
      </div>
    );
  }

  return (
    <Link
      data-testid={testId}
      href={href}
      className={`${shell} block hover:border-amber-300 hover:bg-amber-50 group`}
    >
      {body}
    </Link>
  );
}
