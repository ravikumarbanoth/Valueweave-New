"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase-browser";
import AppNavbar from "@/components/AppNavbar";
import { CheckCircle2 } from "lucide-react";
import RecommendationRail from "@/components/knowledge/RecommendationRail";
import { getRecommendations, intelligenceState } from "@/lib/intelligence";
import { normaliseTerm } from "@/lib/knowledge";

// Phase 7 — skill complementarity on an accepted connection.
//
// Compares the two profiles' own `skills` arrays directly. No crosswalk is needed
// or wanted here: the question is "what does this pair have between them", which is
// answerable from what both people typed. The crosswalk exists to reach the
// knowledge graph, and this comparison never leaves the two profiles.
function skillOverlap(mine = [], theirs = []) {
  const mineNorm = new Map((mine || []).map((s) => [normaliseTerm(s), s]));
  const theirsNorm = new Map((theirs || []).map((s) => [normaliseTerm(s), s]));
  const shared = [];
  const complementary = [];
  for (const [key, label] of theirsNorm) {
    (mineNorm.has(key) ? shared : complementary).push(label);
  }
  return { shared: shared.sort(), complementary: complementary.sort() };
}

export default function ConnectionsPage() {
  const supabase = createClient();
  const [me, setMe] = useState(null);
  const [tab, setTab] = useState("received");
  const [received, setReceived] = useState([]);
  const [sent, setSent] = useState([]);
  const [loading, setLoading] = useState(true);
  // Phase 7 — engine-produced collaborator suggestions, replacing the static
  // sector-based matching. Read from user_recommendations; nothing is scored here.
  const [suggested, setSuggested] = useState([]);
  const [intel, setIntel] = useState(null);

  const load = async () => {
    setLoading(true);
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return;
    const { data: myProfile } = await supabase.from("profiles").select("*").eq("id", user.id).single();
    setMe(myProfile);

    const [r, s] = await Promise.all([
      supabase.from("connections")
        .select("*, opportunity:opportunities(id,title), from_user:profiles!connections_from_user_id_fkey(id,name,picture,skills), to_user:profiles!connections_to_user_id_fkey(id,name,picture,skills)")
        .eq("to_user_id", user.id)
        .order("created_at", { ascending: false }),
      supabase.from("connections")
        .select("*, opportunity:opportunities(id,title), from_user:profiles!connections_from_user_id_fkey(id,name,picture,skills), to_user:profiles!connections_to_user_id_fkey(id,name,picture,skills)")
        .eq("from_user_id", user.id)
        .order("created_at", { ascending: false }),
    ]);
    setReceived(r.data || []);
    setSent(s.data || []);
    setLoading(false);

    const state = await intelligenceState(user.id);
    setIntel(state);
    if (state.available) {
      setSuggested(await getRecommendations(user.id, { category: "collaborators", limit: 6 }));
    }
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, []);

  const update = async (id, status) => {
    await supabase.from("connections").update({ status }).eq("id", id);
    load();
  };

  const list = tab === "received" ? received : sent;

  return (
    <div className="min-h-screen bg-cream pb-24 md:pb-12">
      <AppNavbar initialProfile={me} />
      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        <h1 className="font-display font-extrabold text-3xl tracking-tight mb-5">Connections</h1>

        {/* ── Phase 7: suggested collaborators, from the intelligence engine ── */}
        {intel && (intel.available ? suggested.length > 0 : false) && (
          <RecommendationRail
            testId="rail-collaborators"
            title="Suggested collaborators"
            subtitle="Ranked by complementary skills, shared district and shared sector"
            category="collaborators"
            items={suggested}
            limit={3}
          />
        )}

        <div className="inline-flex items-center gap-1 mb-5 bg-white border border-stone-200 rounded-full p-1">
          {[["received","Received", received.length], ["sent","Sent", sent.length]].map(([k, l, n]) => (
            <button
              key={k}
              data-testid={`tab-${k}`}
              onClick={() => setTab(k)}
              className={`px-5 py-2 rounded-full text-xs font-display font-bold transition-colors ${tab === k ? "bg-ink text-white" : "text-muted hover:text-ink"}`}
            >
              {l} ({n})
            </button>
          ))}
        </div>

        {loading ? <p>Loading…</p> : list.length === 0 ? (
          <div data-testid="connections-empty" className="card-base !border-dashed !border-2 p-12 text-center">
            <div className="text-5xl mb-3">📭</div>
            <h3 className="font-display font-bold text-lg mb-2">
              {tab === "received" ? "No requests yet" : "You haven't sent any requests"}
            </h3>
            <p className="text-muted text-sm mb-5 max-w-sm mx-auto">
              {tab === "received"
                ? "When someone wants to collaborate on your opportunities, their request will show up here."
                : "Browse the feed and connect with builders working on things you care about."}
            </p>
            <Link href={tab === "received" ? "/opportunities/new" : "/dashboard"} className="btn-primary">
              {tab === "received" ? "Post an opportunity →" : "Browse feed →"}
            </Link>
          </div>
        ) : (
          <div className="grid gap-3">
            {list.map((c) => {
              const isReceived = tab === "received";
              const other = isReceived ? c.from_user : c.to_user;
              const accepted = c.status === "accepted";
              // Only shown once a connection is accepted: before that the pair is
              // not a working group and the comparison would be speculation.
              const overlap = accepted ? skillOverlap(me?.skills, other?.skills) : null;
              return (
                <div
                  key={c.id}
                  data-testid={`conn-${c.id}`}
                  className={`rounded-2xl p-5 transition-colors border ${
                    accepted ? "bg-emerald-50/60 border-emerald-200" : "bg-white border-stone-200"
                  }`}
                >
                  <div className="flex items-center gap-3 mb-3">
                    {other?.picture ? (
                      <img src={other.picture} alt="" className={`w-10 h-10 rounded-full ${accepted ? "ring-2 ring-emerald-300" : ""}`} />
                    ) : (
                      <div className={`w-10 h-10 rounded-full bg-amber-200 text-amber-700 flex items-center justify-center font-bold ${accepted ? "ring-2 ring-emerald-300" : ""}`}>{(other?.name || "?")[0]}</div>
                    )}
                    <div className="flex-1 min-w-0">
                      <Link href={`/profile/${other?.id}`} className="font-display font-bold text-sm hover:underline">
                        {isReceived ? other?.name : `To: ${other?.name}`}
                      </Link>
                      {c.opportunity && (
                        <div>
                          <Link href={`/opportunities/${c.opportunity.id}`} className="text-xs text-teal-600 font-semibold hover:underline">
                            re: {c.opportunity.title} →
                          </Link>
                        </div>
                      )}
                    </div>
                    <span
                      data-testid={`conn-status-${c.id}`}
                      className={`chip uppercase text-[10px] ${
                        accepted ? "bg-emerald-100 text-emerald-700" :
                        c.status === "rejected" ? "bg-rose-50 text-rose-700" :
                        "bg-amber-50 text-amber-700"
                      }`}
                    >
                      {accepted && <CheckCircle2 size={11} className="-ml-0.5" />}
                      {c.status}
                    </span>
                  </div>

                  {/* ── Phase 7: what this pair actually brings each other ──
                      Complementary skills are the reason to work together; shared
                      ones are the shorthand you already have. Both are useful and
                      they are not the same thing, so they are labelled apart. */}
                  {overlap && (overlap.complementary.length > 0 || overlap.shared.length > 0) && (
                    <div
                      data-testid={`conn-skills-${c.id}`}
                      className="mb-3 rounded-2xl bg-white/70 border border-emerald-150 p-3"
                    >
                      {overlap.complementary.length > 0 && (
                        <div className="mb-2 last:mb-0">
                          <h4 className="label-display !mb-1.5">
                            Brings skills you don&apos;t have
                            <span className="text-stone-400 font-normal tabular-nums ml-1.5">
                              {overlap.complementary.length}
                            </span>
                          </h4>
                          <div className="flex flex-wrap gap-1.5">
                            {overlap.complementary.slice(0, 8).map((sk) => (
                              <span key={sk} className="chip bg-teal-50 text-teal-700 border border-teal-200 text-[11px]">
                                {sk}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {overlap.shared.length > 0 && (
                        <div>
                          <h4 className="label-display !mb-1.5">
                            Shared
                            <span className="text-stone-400 font-normal tabular-nums ml-1.5">
                              {overlap.shared.length}
                            </span>
                          </h4>
                          <div className="flex flex-wrap gap-1.5">
                            {overlap.shared.slice(0, 8).map((sk) => (
                              <span key={sk} className="chip bg-stone-100 text-stone-600 border border-stone-200 text-[11px]">
                                {sk}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  <p className="bg-white/70 rounded-xl px-4 py-2.5 text-sm text-ink leading-relaxed">"{c.message}"</p>

                  {accepted && (
                    <div data-testid={`conn-accepted-helper-${c.id}`} className="mt-3 flex items-start gap-2 bg-emerald-100/70 border border-emerald-200 rounded-xl px-4 py-3">
                      <CheckCircle2 size={16} className="text-emerald-700 shrink-0 mt-0.5" />
                      <p className="text-xs sm:text-sm text-emerald-800 leading-relaxed">
                        <span className="font-display font-bold">Connection accepted.</span> You can now safely share contact details if you'd like to collaborate further. ValueWeave keeps contact sharing manual to protect your privacy.
                      </p>
                    </div>
                  )}

                  {isReceived && c.status === "pending" && (
                    <div className="flex gap-2 mt-3">
                      <button data-testid={`accept-${c.id}`} onClick={() => update(c.id, "accepted")} className="btn-teal !py-2 !px-5 text-xs">Accept</button>
                      <button data-testid={`reject-${c.id}`} onClick={() => update(c.id, "rejected")} className="btn-secondary !py-2 !px-5 text-xs">Decline</button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
