"use client";
import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase-browser";
import AppNavbar from "@/components/AppNavbar";
import OpportunityCard from "@/components/OpportunityCard";

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
      const s = search.trim();
      q = q.or(`title.ilike.%${s}%,description.ilike.%${s}%`);
    }
    const { data, error } = await q;
    if (!error) setItems(data || []);
    setLoading(false);
  }, [supabase, category, search]);

  useEffect(() => { load(); }, [load]);

  return (
    <div className="min-h-screen bg-cream pb-20 md:pb-0">
      <AppNavbar initialProfile={profile} />
      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="flex items-end justify-between flex-wrap gap-4 mb-6">
          <div>
            <h1 data-testid="dashboard-greeting" className="font-display font-extrabold text-3xl tracking-tight mb-1">
              Hey {profile?.name?.split(" ")[0] || "builder"} 👋
            </h1>
            <p className="text-muted text-sm">Browse open opportunities, or post your own.</p>
          </div>
          <Link href="/opportunities/new" data-testid="cta-post-opportunity" className="btn-primary">
            + Post Opportunity
          </Link>
        </div>

        <div className="card-base p-4 mb-6">
          <input
            data-testid="dashboard-search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search opportunities by title or description…"
            className="input-field mb-3"
          />
          <div className="flex gap-2 overflow-x-auto pb-1">
            {CATEGORIES.map((c) => (
              <button
                key={c.id || "all"}
                data-testid={`filter-${c.id || "all"}`}
                onClick={() => setCategory(c.id)}
                className={`shrink-0 px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-colors ${
                  category === c.id ? "bg-ink text-white" : "bg-stone-100 text-stone-600 hover:bg-stone-200"
                }`}
              >
                {c.emoji} {c.label}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div data-testid="feed-loading" className="text-center py-16 text-muted">Loading opportunities…</div>
        ) : items.length === 0 ? (
          <div data-testid="feed-empty" className="card-base !border-dashed !border-2 p-12 text-center">
            <div className="text-5xl mb-3">🌱</div>
            <h3 className="font-display font-bold mb-2">No opportunities yet</h3>
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
