import Link from "next/link";
import { createClient } from "@/lib/supabase-server";

async function fetchOpportunities() {
  if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
    return [];
  }
  try {
    const sb = createClient();
    const { data } = await sb
      .from("opportunities")
      .select("id, title, category, district, state, investment_range, status")
      .eq("status", "open")
      .order("created_at", { ascending: false })
      .limit(9);
    return data || [];
  } catch {
    return [];
  }
}

// The card lives in HomeFeaturedOpportunitiesClient.jsx. A second, never
// rendered copy of it used to sit here; the two had already drifted (this one
// prefixed "₹", the live one a corrupted "?"), so there is now one.

import HomeFeaturedOpportunitiesClient from "@/components/HomeFeaturedOpportunitiesClient";

export default async function HomeFeaturedOpportunities() {
  const opportunities = await fetchOpportunities();
  return <HomeFeaturedOpportunitiesClient opportunities={opportunities} />;
}
