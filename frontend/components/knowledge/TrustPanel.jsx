// Where this information comes from, and what to do before you act on it.
//
// WHAT THIS REPLACED
// ------------------
// Two components said the same thing in two registers, and both were about our
// shortcomings rather than the reader's decision:
//
//   EntityHeader, on an amber alert panel:
//     "This record has not yet been reviewed by a person. It was collected
//      from a public source and machine-validated. Treat it as a starting
//      point."
//
//   UnverifiedNotice, on six surfaces:
//     "Please double-check before you act. We gather this from official
//      public sources, but our team has not yet checked every line by hand."
//
// Every word was true. The effect was not. A student reading "not reviewed by
// a person" on a government scheme does not conclude "I should confirm the
// deadline on the portal" — they conclude "this site does not know what it is
// talking about", and they leave. The disclosure was written by people worried
// about being wrong, for people who were not worried at all until they read it.
//
// WHY THIS IS NOT JUST SOFTER WORDING
// -----------------------------------
// The old notice was a statement about US: our review queue is behind. The new
// one is a statement about the INFORMATION: here is where it came from, here is
// who maintains it, and here is the one thing worth doing before you spend money
// or file an application. That advice is correct whether or not a human has read
// the row — scheme deadlines and eligibility rules change faster than any site
// can track — so it is useful rather than defensive.
//
// STILL COMPUTED, NEVER STALE
// ---------------------------
// The old component vanished entirely once `verified === total`, so it could not
// outlive its own truth. That property is kept, but it now governs the SECOND
// sentence rather than whether the panel exists: an unchecked entry asks you to
// confirm with the authority, a checked one says we confirmed it and still asks
// you to confirm anything time-sensitive. Neither sentence can become a lie, and
// `data-review-state` exposes which one is showing for support and for tests.
//
// The panel does not disappear when verification lands, because "where did this
// come from" is not a disclaimer — it is the platform's first promise, and the
// day everything is verified is the day it is most worth making.

/** The two states, kept out of the component so tests can name them. */
export const REVIEW_STATE = {
  RESEARCHED: "RESEARCHED", // gathered and machine-checked, not yet read by our team
  CHECKED: "CHECKED",       // a person on the research team has confirmed it
};

export default function TrustPanel({
  verified = 0,
  total = 0,
  hasUnverified = null,
  officialUrl,
  className = "",
}) {
  const pending =
    hasUnverified === null ? Math.max(0, total - verified) > 0 : hasUnverified;
  const state = pending ? REVIEW_STATE.RESEARCHED : REVIEW_STATE.CHECKED;

  return (
    <section
      data-testid="trust-panel"
      data-review-state={state}
      // Teal, not amber. The colour was doing as much of the work as the words:
      // the old panel was amber-50 on amber-200, which is the palette this app
      // uses for "attention", and it sat on pages about someone's career.
      //
      // tailwind.config.js overrides teal 50/100/500/600/700 with the brand
      // values and `extend` merges the rest of the scale in, so 200-400 and
      // 800-900 are still Tailwind's defaults and would clash with the brand
      // shades. Sticking to the five declared steps is deliberate.
      className={`rounded-xl border border-teal-100 bg-teal-50 px-4 py-3 ${className}`}
    >
      <p className="font-display font-bold text-[13px] text-teal-700">
        Where this information comes from
      </p>
      <p className="text-xs text-stone-600 leading-relaxed mt-1.5">
        We compile this from official public sources — government portals, published
        notifications and institution websites — and the ValueWeave research team
        keeps improving it.
      </p>
      <p className="text-xs text-stone-600 leading-relaxed mt-1.5">
        {pending
          ? "Before you apply for a scheme or invest money, always check the latest details with the official authority. Dates and eligibility rules change often."
          : "Our research team has confirmed this against the official source. Dates and eligibility rules still change, so check anything time-sensitive before you act."}
      </p>
      {officialUrl && String(officialUrl).startsWith("http") && (
        <a
          href={officialUrl}
          target="_blank"
          rel="noopener noreferrer"
          data-testid="trust-panel-official"
          className="inline-block text-xs font-display font-bold text-teal-700 underline underline-offset-2 mt-2 hover:text-teal-600"
        >
          Open the official website ↗
        </a>
      )}
    </section>
  );
}
