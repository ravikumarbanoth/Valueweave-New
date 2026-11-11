// Where the homepage network ends: in the footer, on ValueWeave's own mark.
//
// The last homepage section's rails curve in to SEAM_X at its bottom edge —
// the top edge of the footer — and arrive here, at a hub straddling that edge.
// From the hub, faint lines fan out into the footer and the two rails carry
// on down its sides, fading out, so the network finishes in the brand rather
// than stopping dead above the last section.
//
// Rendered by FooterClient on "/" only; every other page's footer is
// unchanged. Pure markup — no hooks, no state.
import { RAIL_LEFT, RAIL_RIGHT, SEAM_X } from "./geometry";

// Where the fan of lines from the hub reaches the bottom of the footer.
const RAYS = [14, 32, 68, 86];

export default function NetworkFooterHub() {
  return (
    <div aria-hidden="true" data-testid="footer-network-hub" className="absolute inset-0 -z-10 pointer-events-none overflow-x-clip">
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
        <defs>
          <linearGradient id="vw-fade" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="rgb(245 158 11)" stopOpacity="0.4" />
            <stop offset="1" stopColor="rgb(245 158 11)" stopOpacity="0" />
          </linearGradient>
        </defs>
        {[RAIL_LEFT, RAIL_RIGHT].map((x) => (
          <path key={x} d={`M${x},0 L${x},100`} fill="none" stroke="url(#vw-fade)" strokeWidth="1.25" vectorEffect="non-scaling-stroke" />
        ))}
        {RAYS.map((x) => (
          <path key={x} d={`M${SEAM_X},0 C${SEAM_X},40 ${x},45 ${x},100`} fill="none" stroke="url(#vw-fade)" strokeWidth="1" vectorEffect="non-scaling-stroke" />
        ))}
      </svg>

      {/* Soft light round the hub — a gradient, not a blur filter, so it costs
          nothing to paint on a phone. Centred ON the seam, so it fades out
          above and below it alike: anchored at the footer's top edge it began
          at full strength there and drew a visible line across the page. */}
      <div
        className="absolute top-0 -translate-x-1/2 -translate-y-1/2 w-[26rem] h-[26rem]"
        style={{ left: `${SEAM_X}%`, background: "radial-gradient(circle at center, rgba(245,158,11,0.14) 0%, rgba(245,158,11,0) 62%)" }}
      />

      {/* The hub itself: the ValueWeave mark, on the seam. */}
      <div
        className="absolute top-0 -translate-x-1/2 -translate-y-1/2 w-14 h-14 rounded-2xl bg-gradient-to-br from-amber-500 to-yellow-400 flex items-center justify-center vw-hub-pulse"
        style={{ left: `${SEAM_X}%`, boxShadow: "0 0 0 6px rgba(251,191,36,0.18), 0 10px 30px -6px rgba(245,158,11,0.55)" }}
      >
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none"><path d="M12 3L4 7.5V16.5L12 21L20 16.5V7.5L12 3Z" stroke="#fff" strokeWidth="2" strokeLinejoin="round"/><path d="M4 7.5L12 12M12 12L20 7.5M12 12V21" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>
      </div>
    </div>
  );
}
