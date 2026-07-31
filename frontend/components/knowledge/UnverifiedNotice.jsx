// The disclosure that no knowledge row has human review.
//
// COMPUTED, NOT HARD-CODED. It renders only while unverified rows actually exist,
// so it disappears by itself the day stewardship makes it false. A hard-coded
// disclaimer would still be sitting here a year after it stopped being true, and a
// stale disclaimer is its own kind of dishonesty.
//
// Pass `verified`/`total`, or `hasUnverified` when only the boolean is known.
export default function UnverifiedNotice({ verified = 0, total = 0, hasUnverified = null, className = "" }) {
  const unverified = hasUnverified === null ? Math.max(0, total - verified) > 0 : hasUnverified;
  if (!unverified) return null;

  return (
    <p
      data-testid="unverified-notice"
      className={`text-xs text-stone-500 bg-stone-50 border border-stone-150 rounded-xl px-3 py-2 leading-relaxed ${className}`}
    >
      <span className="font-semibold text-stone-600">Please double-check before you act.</span>{" "}
      We gather this from official public sources, but our team has not yet checked
      every line by hand. If you are about to apply for a scheme or invest money,
      confirm the details on the official website first.
    </p>
  );
}
