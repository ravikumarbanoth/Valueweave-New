"use client";
import { Youtube, Instagram } from "lucide-react";

// ─────────────────────────────────────────────────────────────────────────────
// EDIT YOUR LINKS HERE. These are the official ValueWeave channels — to change a
// handle later, just replace the URL string on the matching line. Nothing else
// in this file needs touching.
// ─────────────────────────────────────────────────────────────────────────────
export const SOCIAL_URLS = {
  youtube:   "https://www.youtube.com/@valueweave",
  x:         "https://x.com/TeamValueweave",
  instagram: "https://www.instagram.com/valueweave?igsh=MXRuazU0aW53dHVwdg==",
};

// Lucide (already in the project) ships Youtube + Instagram in v0.453.0. It has
// no "X" mark, so X uses a small inline glyph below — no extra package needed.
const SOCIAL_LINKS = [
  {
    id: "youtube",
    label: "YouTube",
    href: SOCIAL_URLS.youtube,
    Icon: Youtube,
    hover: "hover:bg-red-50 hover:text-red-600 hover:border-red-200",
  },
  {
    id: "x",
    label: "X (Twitter)",
    href: SOCIAL_URLS.x,
    Icon: XGlyph,
    hover: "hover:bg-stone-900 hover:text-white hover:border-stone-900",
  },
  {
    id: "instagram",
    label: "Instagram",
    href: SOCIAL_URLS.instagram,
    Icon: Instagram,
    hover: "hover:bg-amber-50 hover:text-amber-600 hover:border-amber-200",
  },
];

// Inline X / Twitter mark — Lucide has no X logo, so we draw it.
function XGlyph({ size = 18, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" {...props}>
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );
}

/**
 * Reusable social row. Two variants, no redesign of anything:
 *   variant="icon"   → compact bordered icon buttons  (footer, About page, desktop header)
 *   variant="inline" → icon + label rows              (mobile menu / drawer)
 *
 * All links open in a new tab, are rel-safe, and carry aria-labels + tooltips.
 */
export default function SocialLinks({ variant = "icon", size = 18, className = "" }) {
  if (variant === "inline") {
    return (
      <div className={`flex flex-col gap-1 ${className}`}>
        {SOCIAL_LINKS.map(({ id, label, href, Icon }) => (
          <a
            key={id}
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            data-testid={`social-${id}`}
            aria-label={`${label} — opens in a new tab`}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-display font-semibold text-muted hover:text-ink hover:bg-stone-100 transition-colors"
          >
            <Icon size={size} aria-hidden="true" />
            <span>{label}</span>
          </a>
        ))}
      </div>
    );
  }

  return (
    <div className={`flex items-center gap-2.5 ${className}`}>
      {SOCIAL_LINKS.map(({ id, label, href, Icon, hover }) => (
        <a
          key={id}
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          data-testid={`social-${id}`}
          aria-label={`${label} — opens in a new tab`}
          title={label}
          className={`group inline-flex items-center justify-center w-9 h-9 rounded-full border border-stone-200 bg-white text-stone-500 transition-all hover:-translate-y-0.5 ${hover}`}
        >
          <Icon size={size} aria-hidden="true" />
        </a>
      ))}
    </div>
  );
}
