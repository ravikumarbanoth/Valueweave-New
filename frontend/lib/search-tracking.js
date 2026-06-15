// ValueWeave — Lightweight search event recorder.
// Call trackSearch() from any client component's search input handler.
// Silently fails so tracking never breaks user experience.

import { createClient } from "@/lib/supabase-browser";

export async function trackSearch({
  query,
  page,
  resultsCount = 0,
  district = null,
  sector = null,
  clickedResult = null,
}) {
  if (!query || query.trim().length < 2) return;
  try {
    const sb = createClient();
    await sb.from("search_events").insert({
      query: query.trim().toLowerCase(),
      page: page || null,
      results_count: resultsCount,
      district: district || null,
      sector: sector || null,
      clicked_result: clickedResult || null,
    });
  } catch {
    // silent — never disrupt UX
  }
}
