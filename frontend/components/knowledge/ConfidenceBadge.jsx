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
        title="Written by our editorial team rather than gathered from an official source, so it has no source rating."
        className={`chip border ${band.tone} text-[10px] ${className}`}
      >
        editorial
      </span>
    );
  }

  return (
    <span
      title={`Source rating ${n}/100 — ${band.label}. This tells you how reliable the source is, not whether every detail is still current. Please confirm anything important on the official website.`}
      className={`chip border ${band.tone} text-[10px] tabular-nums ${className}`}
    >
      {n}/100
    </span>
  );
}
