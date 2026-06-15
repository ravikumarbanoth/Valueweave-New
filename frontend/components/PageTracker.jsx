"use client";
// Drop into any page (server or client) to track a page view + visitor session.
// Renders nothing visible. Safe to include multiple times — deduplication is
// handled in analytics.js via sessionStorage keys.

import { useEffect } from "react";
import { trackSession } from "@/lib/analytics";

export default function PageTracker({ pageType, slug, title, district, sector }) {
  useEffect(() => {
    trackSession({ pageType, slug, title, district, sector });
  }, [slug]); // eslint-disable-line react-hooks/exhaustive-deps
  return null;
}
