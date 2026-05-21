"use client";
import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase-browser";
import AppNavbar from "@/components/AppNavbar";
import OpportunityCard from "@/components/OpportunityCard";
import { FeedSkeleton } from "@/components/Skeleton";
import { Search } from "lucide-react";

const CATEGORIES = [
  { id: "", emoji: "🌐", label: "All" },
  { id: "ai-tech", emoji: "🤖", label: "AI & Tech" },
  { id: "local-business", emoji: "🏪", label: "Local Business" },
  { id: "ev-electronics", emoji: "⚡", label: "EV & Electronics" },
  { id: "drone", emoji: "🚁", label: "Drone" },
  { id: "agri", emoji: "🌾", label: "Agriculture" },
  { id: "student", emoji: "🎓", label: "Student" },
  { id: "trades", emoji: "🔧", label: "Trades" },
  { id: "digital", emoji: "📱", label: "Digital" },
];

function completionPct(p) {
  if (!p) return 0;
  const checks = [
    !!p.name, !!p.city, (p.skills?.length || 0) >= 1, (p.interests?.length || 0) >= 1,
    !!p.bio, !!p.looking_for,
  ];
  return Math.round((checks.filter(Boolean).length / checks.length) * 100);
}

export default function DashboardPage() {
  const supabase = createClient();
  const [profile, setProfile] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    (async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;
      const { data } = await supabase.from("profiles").select("*").eq("id", user.id).single();
      if (data && !data.profile_complete) {
        window.location.replace("/onboarding");
        return;
      }
      setProfile(data);
    })();
  }, [supabase]);

  const load = useCallback(async () => {
    setLoading(true);
    let q = supabase
      .from("opportunities")
      .select("*, owner:profiles!opportunities_owner_id_fkey(id,name,picture)")
      .order("created_at", { ascending: false })
      .limit(50);

    if (category) q = q.eq("category", category);
    if (search.trim()) {
      const s = search.trim().replace(/[%,]/g, "");
      q = q.or(`title.ilike.%${s}%,description.ilike.%${s}%`);
    }
    const { data, error } = await q;
    if (!error) setItems(data || []);
    setLoading(false);
  }, [supabase, category, search]);

  useEffect(() => { load(); }, [load]);

  const pct = completionPct(profile);

  return (
    <div className="min-h-screen bg-cream pb-24 md:pb-12">
      <AppNavbar initialProfile={profile} />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        <div className="flex items-end justify-between flex-wrap gap-4 mb-6">
          <div>
            <h1 data-testid="dashboard-greeting" className="font-display font-extrabold text-2xl sm:text-3xl tracking-tight mb-1">
              Hey {profile?.name?.split(" ")[0] || "builder"} 👋
            </h1>
            <p className="text-muted text-sm">Browse open opportunities, or post your own.</p>
          </div>
          <Link href="/opportunities/new" data-testid="cta-post-opportunity" className="btn-primary">
            + Post Opportunity
          </Link>
        </div>

        {profile && pct < 100 && (
          <Link
            href="/onboarding"
            data-testid="profile-completion-banner"
            className="block bg-gradient-to-r from-amber-50 to-teal-50 border border-amber-200 rounded-2xl p-4 mb-5 hover:border-amber-400 transition-colors"
          >
            <div className="flex items-center justify-between gap-3 flex-wrap">
              <div className="flex-1 min-w-[180px]">
                <div className="font-display font-bold text-sm">Complete your profile · {pct}%</div>
                <div className="text-xs text-muted mt-0.5">A complete profile helps you stand out and get better connections.</div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-32 sm:w-40 h-2 bg-white rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-amber-500 to-teal-500 rounded-full transition-all" style={{ width: `${pct}%` }} />
                </div>
                <span className="text-xs font-bold text-amber-700">Complete →</span>
              </div>
            </div>
          </Link>
        )}

        <div className="card-base p-3 sm:p-4 mb-5">
          <div className="relative mb-3">
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400" />
            <input
              data-testid="dashboard-search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search opportunities by title or description…"
              className="input-field !pl-10"
            />
          </div>
          <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1">
            {CATEGORIES.map((c) => (
              <button
                key={c.id || "all"}
                data-testid={`filter-${c.id || "all"}`}
                onClick={() => setCategory(c.id)}
                className={`shrink-0 px-3.5 py-2 rounded-full text-xs font-display font-semibold whitespace-nowrap transition-colors min-h-[36px] ${
                  category === c.id ? "bg-ink text-white" : "bg-stone-100 text-stone-600 hover:bg-stone-200"
                }`}
              >
                {c.emoji} {c.label}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <FeedSkeleton count={6} />
        ) : items.length === 0 ? (
          <div data-testid="feed-empty" className="card-base !border-dashed !border-2 p-12 text-center">
            <div className="text-5xl mb-3">🌱</div>
            <h3 className="font-display font-bold text-lg mb-2">No opportunities yet</h3>
            <p className="text-muted text-sm mb-4">Be the first to post one for your community.</p>
            <Link href="/opportunities/new" className="btn-primary">Post the first opportunity →</Link>
          </div>
        ) : (
          <div data-testid="feed-list" className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {items.map((opp) => <OpportunityCard key={opp.id} opp={opp} />)}
          </div>
        )}
      </main>
    </div>
  );
}
