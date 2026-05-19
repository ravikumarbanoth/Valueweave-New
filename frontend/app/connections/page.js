"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase-browser";
import AppNavbar from "@/components/AppNavbar";

export default function ConnectionsPage() {
  const supabase = createClient();
  const [me, setMe] = useState(null);
  const [tab, setTab] = useState("received");
  const [received, setReceived] = useState([]);
  const [sent, setSent] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return;
    const { data: myProfile } = await supabase.from("profiles").select("*").eq("id", user.id).single();
    setMe(myProfile);

    const [r, s] = await Promise.all([
      supabase.from("connections")
        .select("*, opportunity:opportunities(id,title), from_user:profiles!connections_from_user_id_fkey(id,name,picture), to_user:profiles!connections_to_user_id_fkey(id,name,picture)")
        .eq("to_user_id", user.id)
        .order("created_at", { ascending: false }),
      supabase.from("connections")
        .select("*, opportunity:opportunities(id,title), from_user:profiles!connections_from_user_id_fkey(id,name,picture), to_user:profiles!connections_to_user_id_fkey(id,name,picture)")
        .eq("from_user_id", user.id)
        .order("created_at", { ascending: false }),
    ]);
    setReceived(r.data || []);
    setSent(s.data || []);
    setLoading(false);
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, []);

  const update = async (id, status) => {
    await supabase.from("connections").update({ status }).eq("id", id);
    load();
  };

  const list = tab === "received" ? received : sent;

  return (
    <div className="min-h-screen bg-cream pb-20 md:pb-0">
      <AppNavbar initialProfile={me} />
      <main className="max-w-3xl mx-auto px-6 py-8">
        <h1 className="font-display font-extrabold text-3xl tracking-tight mb-5">Connections</h1>

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
          <div data-testid="connections-empty" className="card-base !border-dashed !border-2 p-12 text-center text-muted">
            <div className="text-4xl mb-2">📭</div>
            No {tab} connection requests yet.
          </div>
        ) : (
          <div className="grid gap-3">
            {list.map((c) => {
              const isReceived = tab === "received";
              const other = isReceived ? c.from_user : c.to_user;
              return (
                <div key={c.id} data-testid={`conn-${c.id}`} className="card-base p-5">
                  <div className="flex items-center gap-3 mb-3">
                    {other?.picture ? (
                      <img src={other.picture} alt="" className="w-10 h-10 rounded-full" />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-amber-200 text-amber-700 flex items-center justify-center font-bold">{(other?.name || "?")[0]}</div>
                    )}
                    <div className="flex-1">
                      <div className="font-display font-bold text-sm">
                        {isReceived ? other?.name : `To: ${other?.name}`}
                      </div>
                      {c.opportunity && (
                        <Link href={`/opportunities/${c.opportunity.id}`} className="text-xs text-teal-600 font-semibold">
                          re: {c.opportunity.title} →
                        </Link>
                      )}
                    </div>
                    <span className={`chip uppercase text-[10px] ${
                      c.status === "accepted" ? "bg-teal-50 text-teal-700" :
                      c.status === "rejected" ? "bg-rose-50 text-rose-700" : "bg-amber-50 text-amber-700"
                    }`}>{c.status}</span>
                  </div>
                  <p className="bg-cream rounded-xl px-4 py-2.5 text-sm text-ink leading-relaxed">"{c.message}"</p>
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
