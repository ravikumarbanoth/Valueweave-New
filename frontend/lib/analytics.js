"use client";
// ValueWeave — Client-side analytics helpers.
// All functions are silent-fail — tracking must never break UX.
// Call from "use client" components or useEffect hooks only.

import { createClient } from "@/lib/supabase-browser";

// ─── Session / Visitor ID helpers ────────────────────────────

export function getSessionId() {
  if (typeof window === "undefined") return null;
  let sid = sessionStorage.getItem("vw_sid");
  if (!sid) {
    sid = crypto.randomUUID();
    sessionStorage.setItem("vw_sid", sid);
  }
  return sid;
}

export function getVisitorId() {
  if (typeof window === "undefined") return null;
  let vid = localStorage.getItem("vw_vid");
  if (!vid) {
    vid = crypto.randomUUID();
    localStorage.setItem("vw_vid", vid);
  }
  return vid;
}

function detectDevice() {
  if (typeof navigator === "undefined") return "other";
  const ua = navigator.userAgent;
  if (/Tablet|iPad/i.test(ua)) return "tablet";
  if (/Mobi|Android|iPhone/i.test(ua)) return "mobile";
  return "desktop";
}

function detectBrowser() {
  if (typeof navigator === "undefined") return "other";
  const ua = navigator.userAgent;
  if (ua.includes("Edg/")) return "edge";
  if (ua.includes("Chrome/")) return "chrome";
  if (ua.includes("Firefox/")) return "firefox";
  if (ua.includes("Safari/")) return "safari";
  return "other";
}

// ─── Visitor session tracker ──────────────────────────────────
// Fires once per browser session (deduplicated via sessionStorage).

export async function trackVisitor({ pagePath } = {}) {
  if (typeof window === "undefined") return;
  const sessionId = getSessionId();
  const dedupeKey = `vw_vs_${sessionId}`;
  if (sessionStorage.getItem(dedupeKey)) return;
  sessionStorage.setItem(dedupeKey, "1");

  try {
    const sb = createClient();
    await sb.from("visitor_sessions").insert({
      session_id: sessionId,
      visitor_id: getVisitorId(),
      page_path: pagePath || window.location.pathname,
      referrer: document.referrer || null,
      device_type: detectDevice(),
      browser: detectBrowser(),
    });
  } catch {
    // silent
  }
}

// ─── Page view tracker ────────────────────────────────────────
// Fires once per page slug per session (deduplicated via sessionStorage).

export async function trackPageView({
  pageType,
  slug,
  title = null,
  district = null,
  sector = null,
} = {}) {
  if (typeof window === "undefined" || !pageType || !slug) return;
  const sessionId = getSessionId();
  const dedupeKey = `vw_pv_${sessionId}_${slug}`;
  if (sessionStorage.getItem(dedupeKey)) return;
  sessionStorage.setItem(dedupeKey, "1");

  try {
    const sb = createClient();
    await sb.from("page_views").insert({
      page_type: pageType,
      page_slug: slug,
      page_title: title || null,
      district: district || null,
      sector: sector || null,
      session_id: sessionId,
      referrer: document.referrer || null,
    });
  } catch {
    // silent
  }
}

// ─── Convenience: track both visitor + page view in one call ──

export async function trackSession({ pageType, slug, title, district, sector } = {}) {
  await Promise.all([
    trackVisitor({ pagePath: typeof window !== "undefined" ? window.location.pathname : "/" }),
    trackPageView({ pageType, slug, title, district, sector }),
  ]);
}
