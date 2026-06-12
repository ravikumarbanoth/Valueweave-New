"use client";
import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase-browser";
import AppNavbar from "@/components/AppNavbar";
import OpportunityCard from "@/components/OpportunityCard";
import { FeedSkeleton } from "@/components/Skeleton";
import { Search, Lock } from "lucide-react";
import { MARKETPLACE_DISTRICTS } from "@/lib/collab";

const CATEGORIES = [
  { id: "", emoji: "🌐", label: "All" },
  { id: "healthcare", emoji: "🏥", label: "Healthcare" },
  { id: "education", emoji: "📚", label: "Education" },
  { id: "agri", emoji: "🌾", label: "Agriculture" },
  { id: "ai-tech", emoji: "🤖", label: "Technology" },
  { id: "manufacturing", emoji: "🏭", label: "Manufacturing" },
  { id: "local-business", emoji: "🏪", label: "Local Business" },
  { id: "ev-electronics", emoji: "⚡", label: "EV & Electronics" },
  { id: "drone", emoji: "🚁", label: "Drone" },
  { id: "student", emoji: "🎓", label: "Student" },
  { id: "trades", emoji: "🔧", label: "Trades" },
  { id: "digital", emoji: "📱", label: "Digital" },
];

export default function ExplorePage() {
  const supabase = createClient();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState("");
  const [district, setDistrict] = useState("");
  const [search, setSearch] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    let q = supabase
      .from("opportunities")
      .select("*, owner:profiles!opportunities_owner_id_fkey(id,name,picture)")
      .order("created_at", { ascending: false })
      .limit(60);
    if (category) q = q.eq("category", category);
    if (district) q = q.eq("district", district);
    if (search.trim()) {
      const s = search.trim().replace(/[%,]/g, "");
      q = q.or(`title.ilike.%${s}%,description.ilike.%${s}%`);
    }
    const { data, error } = await q;
    if (!error) setItems(data || []);
    setLoading(false);
  }, [supabase, category, district, search]);

  useEffect(() => { load(); }, [load]);

  return (
    <div className="min-h-screen bg-cream pb-16">
      <AppNavbar />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        <div className="mb-6">
          <h1 data-testid="explore-title" className="font-display font-extrabold text-3xl sm:text-4xl tracking-tight mb-2">
            Explore opportunities
          </h1>
          <p className="text-muted text-base max-w-xl">
            Browse what builders across Bharat are creating. Sign in to connect or post your own.
          </p>
        </div>

        <div className="card-base p-3 sm:p-4 mb-5">
          <div className="relative mb-3">
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400" />
            <input
              data-testid="explore-search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search opportunities…"
              className="input-field !pl-10"
            />
          </div>
          <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1 mb-3">
            {CATEGORIES.map((c) => (
              <button
                key={c.id || "all"}
                data-testid={`explore-filter-${c.id || "all"}`}
                onClick={() => setCategory(c.id)}
                className={`shrink-0 px-3.5 py-2 rounded-full text-xs font-display font-semibold whitespace-nowrap transition-colors min-h-[36px] ${
                  category === c.id ? "bg-ink text-white" : "bg-stone-100 text-stone-600 hover:bg-stone-200"
                }`}
              >
                {c.emoji} {c.label}
              </button>
            ))}
          </div>
          <select
            data-testid="explore-district"
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
            className="rounded-lg border border-stone-200 bg-white px-3 py-2 text-xs font-display font-semibold text-ink outline-none focus:border-amber-500"
          >
            <option value="">📍 All districts</option>
            <optgroup label="Telangana">
              {MARKETPLACE_DISTRICTS.filter((d) => d.state === "Telangana").map((d) => (
                <option key={d.slug} value={d.name}>{d.name}</option>
              ))}
            </optgroup>
            <optgroup label="Andhra Pradesh">
              {MARKETPLACE_DISTRICTS.filter((d) => d.state === "Andhra Pradesh").map((d) => (
                <option key={d.slug} value={d.name}>{d.name}</option>
              ))}
            </optgroup>
          </select>
        </div>

        {loading ? <FeedSkeleton count={6} /> : items.length === 0 ? (
          <div data-testid="explore-empty" className="card-base !border-dashed !border-2 p-12 text-center">
            <div className="text-5xl mb-3">🌱</div>
            <h3 className="font-display font-bold text-lg mb-2">No opportunities yet</h3>
            <p className="text-muted text-sm mb-4 max-w-sm mx-auto">Be among the first builders to post an opportunity for your community.</p>
            <Link href="/get-started" className="btn-primary">Join & post the first →</Link>
          </div>
        ) : (
          <>
            <div data-testid="explore-list" className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {items.map((opp) => <OpportunityCard key={opp.id} opp={opp} />)}
            </div>
            <div className="mt-10 bg-gradient-to-r from-amber-50 to-teal-50 border border-amber-200 rounded-2xl p-6 text-center">
              <Lock className="inline-block text-amber-600 mb-2" size={22} />
              <h3 className="font-display font-bold text-lg mb-1">Like what you see?</h3>
              <p className="text-sm text-muted mb-4 max-w-md mx-auto">Join ValueWeave free to send connection requests, post your own opportunities, and build with other Bharat builders.</p>
              <div className="flex items-center justify-center gap-2 flex-wrap">
                <Link href="/get-started" data-testid="explore-join" className="btn-primary">Join ValueWeave</Link>
                <Link href="/signin" data-testid="explore-signin" className="btn-secondary">Sign in</Link>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
