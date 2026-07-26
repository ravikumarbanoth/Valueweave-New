// One knowledge entity or recommendation, with its provenance and confidence.
//
// Deliberately styled with the tokens the app already uses (card-base, chip,
// text-ink, text-muted) so it sits inside existing pages without redesigning them.
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
  footer,
  testId,
}) {
  const body = (
    <>
      <div className="flex items-start justify-between gap-2 mb-2">
        {type && <span className="chip bg-white text-stone-500 border border-stone-200 text-[10px]">{type}</span>}
        <div className="flex items-center gap-1.5 shrink-0">
          {matchScore !== undefined && matchScore !== null && (
            <span
              title="How well this matches your profile. Separate from source confidence."
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

  const shell =
    "rounded-2xl bg-stone-50 border border-stone-150 p-4 h-full transition-colors";

  if (!href) {
    return (
      <div data-testid={testId} className={shell}>
        {body}
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
