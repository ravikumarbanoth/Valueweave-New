"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { createClient } from "@/lib/supabase-browser";
import AppNavbar from "@/components/AppNavbar";
import ShareButton from "@/components/ShareButton";
import { CATEGORY_META } from "@/components/OpportunityCard";
import { LogIn } from "lucide-react";

export default function OpportunityDetailPage() {
  const supabase = createClient();
  const { id } = useParams();
  const router = useRouter();
  const [me, setMe] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);
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
      setAuthChecked(true);

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

  if (loading) return <Shell me={me}>
    <div className="card-base p-6 md:p-8">
      <div className="skeleton h-6 w-32 mb-4" />
      <div className="skeleton h-10 w-3/4 mb-3" />
      <div className="skeleton h-4 w-1/2 mb-6" />
      <div className="skeleton h-4 w-full mb-2" />
      <div className="skeleton h-4 w-5/6 mb-2" />
      <div className="skeleton h-4 w-4/6" />
    </div>
  </Shell>;

  if (!opp) return <Shell me={me}>
    <div className="card-base p-10 text-center" data-testid="detail-not-found">
      <div className="text-5xl mb-3">🔍</div>
      <h2 className="font-display font-bold text-xl mb-2">Opportunity not found</h2>
      <p className="text-muted text-sm mb-5">This link may have been removed or doesn't exist.</p>
      <Link href={me ? "/dashboard" : "/"} className="btn-primary">Back to {me ? "feed" : "home"}</Link>
    </div>
  </Shell>;

  const isOwner = me?.id === opp.owner_id;
  const cat = CATEGORY_META[opp.category] || { emoji: "🌐", label: opp.category };
  const isAnon = authChecked && !me;

  return (
    <Shell me={me}>
      <div className="flex items-center justify-between flex-wrap gap-3 mb-4">
        <Link href={me ? "/dashboard" : "/"} className="text-sm font-display font-semibold text-muted hover:text-ink">
          ← {me ? "Back to feed" : "Back to home"}
        </Link>
        <ShareButton url={`/opportunities/${opp.id}`} title={opp.title} />
      </div>

      <article className="card-base p-6 md:p-8">
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="chip bg-amber-50 text-amber-700">{cat.emoji} {cat.label}</span>
          <span className="chip bg-teal-50 text-teal-600">{opp.collaboration_type}</span>
          <span className="chip bg-violet-50 text-violet-700">{opp.commitment}</span>
        </div>
        <h1 data-testid="detail-title" className="h-section mb-3">{opp.title}</h1>
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

        <Link href={`/profile/${opp.owner_id}`} className="flex items-center gap-3 py-4 border-y border-stone-100 mb-5 -mx-1 px-1 rounded-lg hover:bg-stone-50 transition-colors">
          {opp.owner?.picture ? (
            <img src={opp.owner.picture} alt="" className="w-11 h-11 rounded-full" />
          ) : (
            <div className="w-11 h-11 rounded-full bg-amber-200 text-amber-700 flex items-center justify-center font-bold">{(opp.owner?.name || "?")[0]}</div>
          )}
          <div className="flex-1">
            <div className="font-display font-bold text-sm">{opp.owner?.name}</div>
            <div className="text-xs text-teal-600 font-semibold">View profile →</div>
          </div>
        </Link>

        {existingConn && (
          <div data-testid="connect-existing" className="bg-teal-50 text-teal-700 px-4 py-3 rounded-xl text-sm font-display font-semibold mb-4">
            ✓ You've already requested to connect — status: <span className="uppercase">{existingConn.status}</span>
          </div>
        )}

        {isAnon && (
          <div data-testid="connect-anon-cta" className="bg-amber-50 border border-amber-200 rounded-2xl p-5">
            <h4 className="font-display font-bold text-base mb-1">Want to connect with {opp.owner?.name?.split(" ")[0] || "this builder"}?</h4>
            <p className="text-sm text-muted mb-4">Sign in with Google to send a connection request. Takes 10 seconds.</p>
            <Link href="/get-started" className="btn-primary">
              <LogIn size={15} /> Sign in to connect
            </Link>
          </div>
        )}

        {!isAnon && !isOwner && !existingConn && (
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
              <div className="flex gap-2 mt-3 flex-wrap">
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
          <button data-testid="opp-delete" onClick={removeOpp} className="inline-flex items-center gap-2 text-rose-700 border-2 border-rose-200 hover:bg-rose-50 rounded-full px-5 py-2.5 font-display font-bold text-sm min-h-[44px]">
            Delete opportunity
          </button>
        )}
      </article>
    </Shell>
  );
}

function Shell({ me, children }) {
  return (
    <div className="min-h-screen bg-cream pb-24 md:pb-12">
      <AppNavbar initialProfile={me} />
      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-6 sm:py-8">{children}</main>
    </div>
  );
}
