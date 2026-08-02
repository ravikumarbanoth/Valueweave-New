// One intelligence score. Three statuses, three different sentences.
//
// The rule this component exists to enforce: a score of null is NOT zero.
//   APPLIED      show the number and its reason
//   NO_SIGNAL    we looked and found nothing — show 0 and say what is missing
//   UNAVAILABLE  we could not compute it — show "—" and NEVER a number
//
// Rendering UNAVAILABLE as 0 would tell a user they scored nothing when the truth
// is that we lack an input. That is the single most misleading thing this UI could
// do, so it is handled here once rather than at every call site.
import { STATUS, scoreLabel, scoreTone } from "@/lib/intelligence";

export default function ScoreCard({ label, score, status, confidence, reason, detail, testId }) {
  const value = scoreLabel(score, status);
  const tone = scoreTone(score, status);
  const unavailable = status === STATUS.UNAVAILABLE;

  return (
    <div data-testid={testId} className="rounded-2xl bg-white border border-stone-150 p-4">
      <div className="flex items-start justify-between gap-3 mb-2">
        <h3 className="font-display font-bold text-sm text-ink leading-snug">{label}</h3>
        <span
          className={`shrink-0 rounded-xl border px-2.5 py-1 font-display font-extrabold text-base tabular-nums ${tone}`}
          title={unavailable ? "Not enough information to compute this" : `${value} out of 100`}
        >
          {value}
          {!unavailable && <span className="text-[10px] font-semibold opacity-60">/100</span>}
        </span>
      </div>

      {reason && <p className="text-xs text-muted leading-relaxed">{reason}</p>}

      <div className="flex items-center gap-2 mt-2.5 flex-wrap">
        {status && status !== STATUS.APPLIED && (
          <span className="chip bg-stone-100 text-stone-500 border border-stone-200 text-[10px]">
            {status === STATUS.UNAVAILABLE ? "not enough data" : "nothing found yet"}
          </span>
        )}
        {confidence > 0 && (
          <span
            title="How reliable the weakest source behind this number is. We show the lowest one, not the average, so the score is never flattered."
            className="chip bg-stone-50 text-stone-500 border border-stone-200 text-[10px] tabular-nums"
          >
            source {confidence}/100
          </span>
        )}
      </div>

      {detail}
    </div>
  );
}
