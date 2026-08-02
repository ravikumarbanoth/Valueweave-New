// How strong the source behind a fact is.
//
// WHAT THIS SHOWED, AND WHY IT WAS THE WRONG NUMBER TO SHOW
// ---------------------------------------------------------
// It rendered `56/100` beside the name of a business opportunity. Every reader
// who has ever sat an exam reads 56/100 as a mark — a poor one — and the thing
// it appears next to is the thing it appears to be marking. It was not marking
// the opportunity. It was scoring how authoritative OUR SOURCE for that row is.
//
// The tooltip said so, and a tooltip does not exist on a phone.
//
// So the chip now leads with the band in words — "Official source", "Published
// source", "Local knowledge" — and the number moves into the tooltip beside the
// explanation it always needed. Nothing about the score itself changed: the same
// value, the same thresholds, still on `data-confidence` for tests and support.
//
// The zero case keeps its own label, because editorial content genuinely has no
// source score and showing "0" would read as "we are certain this is wrong".
import { confidenceBand } from "@/lib/intelligence";

export default function ConfidenceBadge({ confidence, className = "" }) {
  const n = Number(confidence) || 0;
  const band = confidenceBand(n);

  if (!n) {
    return (
      <span
        data-testid="confidence-badge"
        data-confidence="0"
        title="Written by our editorial team rather than gathered from an official source, so it has no source rating."
        className={`chip border ${band.tone} text-[10px] ${className}`}
      >
        {band.label}
      </span>
    );
  }

  return (
    <span
      data-testid="confidence-badge"
      data-confidence={n}
      title={`${band.label} — we rate it ${n}/100 for reliability. This scores how dependable the source is, not whether every detail is still current. Please confirm anything important on the official website.`}
      className={`chip border ${band.tone} text-[10px] ${className}`}
    >
      {band.label}
    </span>
  );
}
