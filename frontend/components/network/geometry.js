// The one coordinate system the homepage network is drawn in. Every section
// wrapper and the footer hub read these numbers, so a line that leaves one
// section is guaranteed to arrive at the same place in the next.
//
// x values are percentages of the page width.

// The two rails. 3% is inside the 16px phone gutter at 390px (12px) and well
// inside the margin beside a max-w-6xl container on desktop.
export const RAIL_LEFT = 3;
export const RAIL_RIGHT = 97;

// Where the rails meet at every seam between sections.
export const SEAM_X = 50;

// Height of the fork bands, in px. Smaller than the smallest section padding
// on the homepage (py-16 = 64px), so a fork never crosses a heading or a card.
export const FORK_PX = 56;

// How far each section's rails bow inwards at their midpoint, in % of width.
// A fixed sequence, not random: the page looks the same on every load and the
// rails never wander more than 1.6% — about 6px on a phone.
export const WIGGLES = [1.2, 0.6, 1.6, 0.9, 1.4, 0.7];

/**
 * A rail that leaves the top of its section at x, bows to x + bow at the
 * vertical midpoint, and returns to x at the bottom. The tangent is vertical
 * at both ends, which is what makes two sections' rails join without a kink.
 * In the section's own 0–100 viewBox.
 */
export function railPath(x, bow) {
  const mid = x + bow;
  return `M${x},0 C${x},25 ${mid},25 ${mid},50 S${x},75 ${x},100`;
}
