// Server component — queries real Supabase data for homepage social proof.
// Renders honest empty state if no data exists yet.

import { createClient } from "@/lib/supabase-server";
import { Users, Briefcase, MapPin, UserCheck, Eye } from "lucide-react";

async function fetchStats() {
  if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
    return { visitors: 0, collaborators: 0, opportunities: 0, districts: 0, assessments: 0 };
  }
  try {
    const sb = createClient();
    const [
      { count: visitors },
      { count: collaborators },
      { count: opportunities },
      { data: districtRows },
      { count: assessments },
    ] = await Promise.all([
      sb.from("visitor_sessions").select("visitor_id", { count: "exact", head: true }),
      sb.from("collaborator_profiles").select("*", { count: "exact", head: true }),
      sb.from("opportunities").select("*", { count: "exact", head: true }).eq("status", "open"),
      sb.from("collaborator_profiles").select("district").not("district", "is", null).limit(200),
      // Discover assessments = collaborator_profiles (completing the quiz creates a profile)
      sb.from("collaborator_profiles").select("*", { count: "exact", head: true }),
    ]);

    const districtSet = new Set((districtRows || []).map((r) => r.district).filter(Boolean));

    return {
      visitors: visitors || 0,
      collaborators: collaborators || 0,
      opportunities: opportunities || 0,
      districts: districtSet.size,
      assessments: assessments || 0,
    };
  } catch {
    return { visitors: 0, collaborators: 0, opportunities: 0, districts: 0, assessments: 0 };
  }
}

function fmt(n) {
  if (n >= 1000) return (n / 1000).toFixed(1).replace(/\.0$/, "") + "K+";
  return n > 0 ? n.toLocaleString() : null;
}

const STATS = [
  { key: "visitors",     icon: Eye,       label: "Visitors",           emptyLabel: "Early access" },
  { key: "assessments",  icon: Users,     label: "Discover Profiles",  emptyLabel: "Be the first" },
  // "Coming soon" was wrong on both counts: the feature is live, and the number
  // being zero is a fact about the marketplace rather than a promise about it.
  { key: "opportunities",icon: Briefcase, label: "Open Opportunities", emptyLabel: "None open yet" },
  { key: "collaborators",icon: UserCheck, label: "Collaborators",      emptyLabel: "Join us" },
  { key: "districts",    icon: MapPin,    label: "Districts Covered",  emptyLabel: "Expanding" },
];

import HomepageStatsClient from "@/components/HomepageStatsClient";

export default async function HomepageStats() {
  const stats = await fetchStats();
  return <HomepageStatsClient stats={stats} />;
}
