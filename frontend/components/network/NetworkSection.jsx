// The continuous network behind the homepage.
//
// ONE COORDINATE SYSTEM, NOT ONE PICTURE PER SECTION
// --------------------------------------------------
// Every homepage section is wrapped in <NetworkSection>, and every wrapper
// draws the SAME geometry, defined once in ./geometry.js:
//
//   - two rails at fixed x positions (RAIL_LEFT / RAIL_RIGHT, in % of width)
//     that run the full height of the section and meet the next section's
//     rails at exactly the same x — so as you scroll they read as two lines
//     travelling down the whole page;
//   - at every seam between two sections, the rails curve in to a node at
//     the centre (SEAM_X) and curve back out on the other side. Each seam is a
//     visible "connection point" between one block of information and the
//     next, and it always sits in the section padding, never over content.
//
// Section heights differ, and differ again between phone and desktop, so a
// single drawing stretched over the whole page would put nodes on top of
// text at some widths. Drawing the same rails per section, with the forks in
// fixed-pixel bands, means continuity at every seam is guaranteed by
// construction at every width.
//
// COST: no JavaScript. This is a server component that emits a few SVG paths
// and dots per section. No canvas, no images, no client-side layout, so no
// layout shift. The only motion is a slow pulse on the seam nodes, switched
// off under prefers-reduced-motion (see globals.css).
//
// It never takes pointer events and sits behind the section's content in its
// own stacking context (`isolate` + `-z-10`), so it cannot cover a button or
// a word. Cards are opaque; the network shows in the gutters and the space
// between sections, which is where it is meant to be seen.
import { RAIL_LEFT, RAIL_RIGHT, SEAM_X, FORK_PX, WIGGLES, railPath } from "./geometry";

export default function NetworkSection({
  children,
  index = 0,
  first = false,
  last = false,
  tone = "plain",
  testId,
}) {
  const wiggle = WIGGLES[index % WIGGLES.length];
  return (
    <div
      data-network-section
      data-testid={testId}
      className={`vw-net relative isolate ${tone === "warm" ? "vw-net-warm" : ""}`}
    >
      {children}
      {/*
        After the children on purpose. A homepage section that has nothing to
        show renders null; the layer is then the wrapper's first child and the
        `.vw-net > .vw-net-layer:first-child` rule in globals.css hides it, so an
        empty section never leaves a stray fork floating on the page.
      */}
      <div aria-hidden="true" className="vw-net-layer absolute inset-0 -z-10 pointer-events-none overflow-x-clip">
        {/* Rails, full section height. */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
          <path d={railPath(RAIL_LEFT, wiggle)} className="vw-rail" />
          <path d={railPath(RAIL_RIGHT, -wiggle)} className="vw-rail" />
        </svg>

        {/* Top fork: from the seam node above, out to both rails. */}
        {!first && (
          <svg className="absolute top-0 left-0 w-full" style={{ height: FORK_PX }} viewBox={`0 0 100 ${FORK_PX}`} preserveAspectRatio="none">
            <path d={`M${SEAM_X},0 C${SEAM_X},${FORK_PX * 0.55} ${RAIL_LEFT},${FORK_PX * 0.45} ${RAIL_LEFT},${FORK_PX}`} className="vw-fork" />
            <path d={`M${SEAM_X},0 C${SEAM_X},${FORK_PX * 0.55} ${RAIL_RIGHT},${FORK_PX * 0.45} ${RAIL_RIGHT},${FORK_PX}`} className="vw-fork" />
          </svg>
        )}

        {/* Bottom fork: both rails in to the next seam node. */}
        <svg className="absolute bottom-0 left-0 w-full" style={{ height: FORK_PX }} viewBox={`0 0 100 ${FORK_PX}`} preserveAspectRatio="none">
          <path d={`M${RAIL_LEFT},0 C${RAIL_LEFT},${FORK_PX * 0.55} ${SEAM_X},${FORK_PX * 0.45} ${SEAM_X},${FORK_PX}`} className="vw-fork" />
          <path d={`M${RAIL_RIGHT},0 C${RAIL_RIGHT},${FORK_PX * 0.55} ${SEAM_X},${FORK_PX * 0.45} ${SEAM_X},${FORK_PX}`} className="vw-fork" />
        </svg>

        {/* Mid-section nodes on the rails. At y = 50% the rail is exactly at
            RAIL ± wiggle by construction, so the dot sits on the line. Hidden
            on phones, where the gutter is 16px and fewer marks read better. */}
        <span className="vw-node hidden sm:block" style={{ left: `${RAIL_LEFT + wiggle}%`, top: "50%" }} />
        <span className="vw-node hidden sm:block" style={{ left: `${RAIL_RIGHT - wiggle}%`, top: "50%" }} />

        {/* The seam node below this section. The last section's seam is the
            footer's hub instead, drawn by NetworkFooterHub. */}
        {!last && <span className="vw-seam" style={{ left: `${SEAM_X}%`, top: "100%" }} />}
      </div>
    </div>
  );
}
