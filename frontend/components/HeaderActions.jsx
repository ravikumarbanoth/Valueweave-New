"use client";

// The right-hand icon cluster in the site header: search, WhatsApp, YouTube.
//
// WHY THESE THREE AND WHY HERE
// -----------------------------
// Search was reachable only from the landing page's hero and from the
// /knowledge results page. On every other public page — Research, Schemes,
// Districts, an opportunity, a skill — a reader who thought of a second
// question had to go back to the home page to ask it. That is the whole
// reason this exists; the icons beside it are the two channels the platform
// actually publishes on.
//
// IT DOES NOT ADD A SEARCH ENGINE
// --------------------------------
// The panel renders the existing <LiveSearch>, unchanged. Same suggest
// endpoint, same debounce, same grouped results, same combobox keyboard
// handling, same English/Telugu/Tanglish resolution, same /knowledge?q=
// destination. Nothing here ranks, fetches or parses a query — it opens a box
// that was already built and already tested.
//
// Consequence worth stating: the panel is mounted only while it is open, so a
// reader who never taps the magnifier costs zero extra requests on every page
// that now carries this header.
//
// ONE CHANNEL LIST, NOT TWO
// --------------------------
// The YouTube URL comes from `useSocialUrls()` in SocialLinks.jsx — the same
// hook the footer uses, reading the same platform_settings row. The header
// cannot drift to a different channel than the footer, because there is only
// one place the URL is decided.
//
// WhatsApp renders only when a URL is configured. None is today, so the icon
// is absent rather than dead. An invented number on a careers platform is
// worse than a missing icon: somebody would message it.

import { useCallback, useEffect, useRef, useState } from "react";
import { Search, X, Youtube } from "lucide-react";
import LiveSearch from "@/components/search/LiveSearch";
import { useSocialUrls } from "@/components/SocialLinks";
import { useLanguage } from "@/lib/language";

//: Lucide has no WhatsApp mark, so it is drawn — the same approach SocialLinks
//: already takes for the X glyph rather than pulling in an icon package.
function WhatsAppGlyph({ size = 20, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor"
         aria-hidden="true" {...props}>
      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51a12.8 12.8 0 0 0-.57-.01c-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884a9.82 9.82 0 0 1 6.988 2.896 9.83 9.83 0 0 1 2.893 6.994c-.003 5.45-4.437 9.886-9.885 9.886m8.413-18.297A11.8 11.8 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.9 11.9 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.82 11.82 0 0 0 20.464 3.488" />
    </svg>
  );
}

//: The rounded-square tinted container from the reference header. One
//: definition so the three buttons cannot drift apart in size or radius, and
//: 44px so every one of them clears the tap minimum PX Phase 10 set.
const TILE = "inline-flex items-center justify-center w-11 h-11 rounded-2xl " +
             "transition-colors shrink-0";

export default function HeaderActions({ className = "" }) {
  const [open, setOpen] = useState(false);
  const urls = useSocialUrls();
  const { t } = useLanguage();
  const panelRef = useRef(null);
  const triggerRef = useRef(null);

  const close = useCallback(() => {
    setOpen(false);
    //: Focus goes back to the magnifier, not to the top of the document. A
    //: keyboard user who opens and closes the panel should be where they
    //: were, not tabbing in from the start of the page again.
    triggerRef.current?.focus();
  }, []);

  useEffect(() => {
    if (!open) return undefined;
    const onKey = (event) => { if (event.key === "Escape") close(); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, close]);

  //: Any navigation closes the panel. Without this, tapping a suggestion
  //: routes underneath an overlay that stays open on the new page.
  useEffect(() => {
    if (!open) return undefined;
    const node = panelRef.current;
    if (!node) return undefined;
    const onNavigate = (event) => {
      if (event.target.closest("a")) setOpen(false);
    };
    node.addEventListener("click", onNavigate);
    return () => node.removeEventListener("click", onNavigate);
  }, [open]);

  const youtubeLabel = t("header.youtube_aria", "Visit ValueWeave YouTube Channel");

  return (
    <>
      <div className={`flex items-center gap-2 ${className}`}>
        <button
          ref={triggerRef}
          type="button"
          onClick={() => setOpen((o) => !o)}
          data-testid="header-search-toggle"
          aria-label={t("header.search_aria", "Search ValueWeave")}
          aria-expanded={open}
          aria-controls="header-search-panel"
          title={t("header.search_aria", "Search ValueWeave")}
          className={`${TILE} bg-amber-50 text-amber-600 hover:bg-amber-100`}
        >
          {open ? <X size={20} aria-hidden="true" /> : <Search size={20} aria-hidden="true" />}
        </button>

        {urls.whatsapp ? (
          <a
            href={urls.whatsapp}
            target="_blank"
            rel="noopener noreferrer"
            data-testid="header-whatsapp"
            aria-label={t("header.whatsapp_aria", "Message ValueWeave on WhatsApp")}
            title="WhatsApp"
            className={`${TILE} bg-green-50 text-green-600 hover:bg-green-100`}
          >
            <WhatsAppGlyph size={20} />
          </a>
        ) : null}

        <a
          href={urls.youtube}
          target="_blank"
          rel="noopener noreferrer"
          data-testid="header-youtube"
          aria-label={youtubeLabel}
          title={youtubeLabel}
          className={`${TILE} bg-red-50 text-red-600 hover:bg-red-100`}
        >
          <Youtube size={20} aria-hidden="true" />
        </a>
      </div>

      {open ? (
        <>
          {/*
            The scrim sits below the panel and above the page. Clicking it
            closes; it is not focusable and is hidden from screen readers,
            which reach the close button instead.
          */}
          <div
            className="fixed inset-0 top-16 z-40 bg-ink/30 backdrop-blur-sm"
            aria-hidden="true"
            onClick={close}
          />
          <div
            id="header-search-panel"
            ref={panelRef}
            role="dialog"
            aria-modal="false"
            aria-label={t("header.search_panel", "Search ValueWeave")}
            data-testid="header-search-panel"
            className="fixed top-16 inset-x-0 z-50 bg-white border-b border-stone-200 shadow-xl"
          >
            {/*
              max-w matches the header's own container so the box lines up
              with the logo above it, and px-4 keeps a gutter at 390px — the
              width PX Phase 10 crawls — so nothing can push the page sideways.
            */}
            <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 sm:py-5">
              <div className="flex items-start gap-3">
                <div className="flex-1 min-w-0">
                  <LiveSearch
                    autoFocus
                    size="compact"
                    hiddenLabel
                    testId="header-live-search"
                    placeholder={t("header.search_placeholder",
                                   "Electrician, PMEGP, Medak…")}
                  />
                </div>
                <button
                  type="button"
                  onClick={close}
                  data-testid="header-search-close"
                  aria-label={t("header.search_close", "Close search")}
                  className="inline-flex items-center justify-center w-11 h-11 shrink-0
                             rounded-2xl text-stone-500 hover:bg-stone-100 hover:text-ink
                             transition-colors"
                >
                  <X size={20} aria-hidden="true" />
                </button>
              </div>
            </div>
          </div>
        </>
      ) : null}
    </>
  );
}
