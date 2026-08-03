"use client";
import { useEffect, useMemo, useState } from "react";
import { Youtube, Instagram } from "lucide-react";
import { createClient } from "@/lib/supabase-browser";

export const SOCIAL_URLS = {
  youtube:   "https://www.youtube.com/@valueweave",
  x:         "https://x.com/TeamValueweave",
  instagram: "https://www.instagram.com/valueweave?igsh=MXRuazU0aW53dHVwdg==",
};

// Lucide (already in the project) ships Youtube + Instagram in v0.453.0. It has
// no "X" mark, so X uses a small inline glyph below — no extra package needed.
function buildLinks(urls) {
  return [
    {
      id: "youtube",
      label: "YouTube",
      href: urls.youtube,
      Icon: Youtube,
      hover: "hover:bg-red-50 hover:text-red-600 hover:border-red-200",
    },
    {
      id: "x",
      label: "X (Twitter)",
      href: urls.x,
      Icon: XGlyph,
      hover: "hover:bg-stone-900 hover:text-white hover:border-stone-900",
    },
    {
      id: "instagram",
      label: "Instagram",
      href: urls.instagram,
      Icon: Instagram,
      hover: "hover:bg-amber-50 hover:text-amber-600 hover:border-amber-200",
    },
  ].filter((link) => link.href);
}

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
  const [urls, setUrls] = useState(SOCIAL_URLS);

  useEffect(() => {
    createClient()
      .from("platform_settings")
      .select("key,value")
      .in("key", ["social.youtube", "social.instagram", "social.x"])
      .then(({ data }) => {
        const map = Object.fromEntries((data || []).map((row) => [row.key, row.value]));
        setUrls({
          youtube: map["social.youtube"] || SOCIAL_URLS.youtube,
          instagram: map["social.instagram"] || SOCIAL_URLS.instagram,
          x: map["social.x"] || SOCIAL_URLS.x,
        });
      });
  }, []);

  const socialLinks = useMemo(() => buildLinks(urls), [urls]);

  if (variant === "inline") {
    return (
      <div className={`flex flex-col gap-1 ${className}`}>
        {socialLinks.map(({ id, label, href, Icon }) => (
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
      {socialLinks.map(({ id, label, href, Icon, hover }) => (
        <a
          key={id}
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          data-testid={`social-${id}`}
          aria-label={`${label} — opens in a new tab`}
          title={label}
          // PX Phase 10: was w-9 h-9 (36px) — under the 44px tap minimum on
          // every page that renders the footer. The visible circle is
          // unchanged; only the touchable box grew.
          className={`group inline-flex items-center justify-center w-11 h-11 rounded-full border border-stone-200 bg-white text-stone-500 transition-all hover:-translate-y-0.5 ${hover}`}
        >
          <Icon size={size} aria-hidden="true" />
        </a>
      ))}
    </div>
  );
}
