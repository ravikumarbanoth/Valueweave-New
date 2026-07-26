// Confidence on a knowledge row. 0–100, banded, with the caveat attached.
//
// The tooltip is the point. A number on its own invites a user to read it as
// "how likely this is true", which it is not: it scores how strong the SOURCE is.
// Every package row in the knowledge base is VST-NEEDS_REVIEW, so nothing here has
// been checked by a person.
import { confidenceBand } from "@/lib/intelligence";

export default function ConfidenceBadge({ confidence, className = "" }) {
  const n = Number(confidence) || 0;
  const band = confidenceBand(n);

  // Editorial content (idea library, research articles) genuinely has no
  // confidence score. Showing "0" would read as "we are certain it is wrong".
  if (!n) {
    return (
      <span
        title="This item comes from editorial content, which carries no source-confidence score."
        className={`chip border ${band.tone} text-[10px] ${className}`}
      >
        editorial
      </span>
    );
  }

  return (
    <span
      title={`Confidence ${n}/100 — ${band.label}. This scores how strong the source is, not whether the fact is correct. No row in this knowledge base has been reviewed by a person.`}
      className={`chip border ${band.tone} text-[10px] tabular-nums ${className}`}
    >
      {n}/100
    </span>
  );
}
