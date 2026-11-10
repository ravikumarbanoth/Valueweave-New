// Display formatting for an opportunity's stored budget text
// (`opportunities.investment_range`).
//
// The column is free text and already carries its own rupee signs — the post
// form stores "Under ₹50K", "₹2L – ₹5L", "₹10L+"; the seed data stores
// "₹1L – ₹3L" and similar. This module only tidies how that text reads. It
// never invents an amount, never converts lakhs, and never prefixes a symbol,
// because the value already has one: the homepage card once rendered
// `₹ {investment_range}`, which would have read "₹ ₹2L – ₹5L".

const PLACEHOLDERS = new Set(["", "-", "—", "na", "n/a", "none", "null", "tbd", "not specified", "unspecified"]);

// "₹50K" → "₹50,000". Thousands only: below one lakh an exact figure reads
// better than an abbreviation, and anything in lakhs stays in lakhs, which is
// how the rest of the site writes them.
function expandThousands(text) {
  return text.replace(/₹\s*(\d+(?:\.\d+)?)\s*[kK]\b/g, (whole, num) => {
    const value = Math.round(parseFloat(num) * 1000);
    if (!Number.isFinite(value) || value >= 100000) return whole;
    return "₹" + value.toLocaleString("en-IN");
  });
}

/**
 * Tidy a stored budget for display, or return null when there is nothing
 * meaningful to show (the caller then renders no budget chip at all rather
 * than "Not specified" or an empty pill).
 *
 *   "Under ₹50K"     → "Under ₹50,000"
 *   "₹2L – ₹5L"      → "₹2L – ₹5L"
 *   "₹2L-₹5L"        → "₹2L – ₹5L"
 *   "₹5K–15K"        → "₹5,000 – ₹15,000"
 *   "₹10L+"          → "₹10L+"
 *   "", null, "N/A"  → null
 */
export function formatBudgetLabel(raw) {
  if (raw == null) return null;
  let text = String(raw).replace(/\s+/g, " ").trim();
  if (PLACEHOLDERS.has(text.toLowerCase())) return null;

  // One spacing for every range separator: hyphen, en dash, em dash, "to".
  text = text.replace(/\s*(?:–|—|-|\bto\b)\s*/g, " – ");

  // A range whose second amount lost its symbol ("₹5K – 15K") gets the same
  // symbol as its first. Only when the first side has one: a bare "5 – 10"
  // is left alone rather than guessed at.
  text = text.replace(/(₹\s*[\d.]+\s*[kKlL]?) – (\d)/g, "$1 – ₹$2");

  text = text.replace(/₹\s+/g, "₹");
  text = expandThousands(text);
  return text || null;
}
