"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { createClient } from "@/lib/supabase-browser";
import AppNavbar from "@/components/AppNavbar";
import { CATEGORY_META } from "@/components/OpportunityCard";

export default function OpportunityDetailPage() {
  const supabase = createClient();
  const { id } = useParams();
  const router = useRouter();
  const [me, setMe] = useState(null);
  const [opp, setOpp] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showConnect, setShowConnect] = useState(false);
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [err, setErr] = useState("");
  const [existingConn, setExistingConn] = useState(null);

  useEffect(() => {
    (async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        const { data: profile } = await supabase.from("profiles").select("*").eq("id", user.id).single();
        setMe(profile);
      }
      const { data: oppData } = await supabase
        .from("opportunities")
        .select("*, owner:profiles!opportunities_owner_id_fkey(id,name,picture,city,bio)")
        .eq("id", id)
        .single();
      setOpp(oppData);

      if (user && oppData) {
        const { data: conn } = await supabase
          .from("connections")
          .select("*")
          .eq("opportunity_id", id)
          .eq("from_user_id", user.id)
          .maybeSingle();
        setExistingConn(conn);
      }
      setLoading(false);
    })();
  }, [supabase, id]);

  const sendConnect = async () => {
    setErr("");
    if (!message.trim()) { setErr("Please add a message."); return; }
    setSending(true);
    try {
      const { data, error } = await supabase
        .from("connections")
        .insert({
          opportunity_id: opp.id,
          from_user_id: me.id,
          to_user_id: opp.owner_id,
          message: message.trim(),
        })
        .select()
        .single();
      if (error) throw error;
      setExistingConn(data);
      setShowConnect(false);
    } catch (e) {
      setErr(e.message || "Could not send.");
    } finally { setSending(false); }
  };

  const removeOpp = async () => {
    if (!window.confirm("Delete this opportunity?")) return;
    await supabase.from("opportunities").delete().eq("id", opp.id);
    router.push("/dashboard");
  };

  if (loading) return <Shell me={me}><p data-testid="detail-loading">Loading…</p></Shell>;
  if (!opp) return <Shell me={me}><p data-testid="detail-not-found">Opportunity not found.</p></Shell>;

  const isOwner = me?.id === opp.owner_id;
  const cat = CATEGORY_META[opp.category] || { emoji: "🌐", label: opp.category };

  return (
    <Shell me={me}>
      <Link href="/dashboard" className="text-sm text-muted hover:text-ink inline-block mb-4">← Back to feed</Link>

      <div className="card-base p-6 md:p-8">
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="chip bg-amber-50 text-amber-700">{cat.emoji} {cat.label}</span>
          <span className="chip bg-teal-50 text-teal-600">{opp.collaboration_type}</span>
          <span className="chip bg-violet-50 text-violet-700">{opp.commitment}</span>
        </div>
        <h1 data-testid="detail-title" className="font-display font-extrabold text-3xl md:text-4xl tracking-tight leading-tight mb-3">{opp.title}</h1>
        <p className="text-muted text-sm mb-6">📍 {opp.location}</p>
        <div data-testid="detail-description" className="text-ink text-base leading-relaxed whitespace-pre-wrap mb-7">{opp.description}</div>

        {opp.skills_needed?.length > 0 && (
          <div className="mb-7">
            <h3 className="label-display">Skills needed</h3>
            <div className="flex flex-wrap gap-1.5">
              {opp.skills_needed.map((s) => <span key={s} className="chip bg-amber-200 text-amber-700">{s}</span>)}
            </div>
          </div>
        )}

        <div className="flex items-center gap-3 py-4 border-y border-stone-100 mb-5">
          {opp.owner?.picture ? (
            <img src={opp.owner.picture} alt="" className="w-11 h-11 rounded-full" />
          ) : (
            <div className="w-11 h-11 rounded-full bg-amber-200 text-amber-700 flex items-center justify-center font-bold">{(opp.owner?.name || "?")[0]}</div>
          )}
          <div>
            <div className="font-display font-bold text-sm">{opp.owner?.name}</div>
            <Link href={`/profile/${opp.owner_id}`} className="text-xs text-teal-600 font-semibold">View profile →</Link>
          </div>
        </div>

        {existingConn && (
          <div data-testid="connect-existing" className="bg-teal-50 text-teal-700 px-4 py-3 rounded-xl text-sm font-semibold mb-4">
            ✓ You already requested to connect — status: <span className="uppercase">{existingConn.status}</span>
          </div>
        )}

        {!isOwner && !existingConn && (
          showConnect ? (
            <div className="bg-amber-50 rounded-2xl p-5">
              <h4 className="font-display font-bold text-sm mb-2">Send a connection request</h4>
              <textarea
                data-testid="connect-message"
                rows={4}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Introduce yourself — what's your background and why this opportunity?"
                className="w-full px-3 py-2.5 rounded-xl border-2 border-amber-200 bg-white text-sm outline-none focus:border-amber-500 resize-y"
              />
              {err && <div className="text-rose-700 text-sm mt-2">{err}</div>}
              <div className="flex gap-2 mt-3">
                <button data-testid="connect-send" onClick={sendConnect} disabled={sending} className="btn-primary !py-2.5 disabled:opacity-50">
                  {sending ? "Sending…" : "Send Request"}
                </button>
                <button onClick={() => setShowConnect(false)} className="btn-secondary !py-2.5">Cancel</button>
              </div>
            </div>
          ) : (
            <button data-testid="connect-open" onClick={() => setShowConnect(true)} className="btn-teal">
              🤝 Connect with {opp.owner?.name?.split(" ")[0]}
            </button>
          )
        )}
        {isOwner && (
          <button data-testid="opp-delete" onClick={removeOpp} className="inline-flex items-center gap-2 text-rose-700 border-2 border-rose-200 hover:bg-rose-50 rounded-full px-5 py-2 font-display font-bold text-sm">
            Delete opportunity
          </button>
        )}
      </div>
    </Shell>
  );
}

function Shell({ me, children }) {
  return (
    <div className="min-h-screen bg-cream pb-20 md:pb-0">
      <AppNavbar initialProfile={me} />
      <main className="max-w-3xl mx-auto px-6 py-8">{children}</main>
    </div>
  );
}
