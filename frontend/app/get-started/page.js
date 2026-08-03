"use client";
import { useState } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase-browser";

const INTENTS = [
  { id: "find-collaborators", emoji: "🤝", title: "Find Collaborators", desc: "Connect with people who complement your skills" },
  { id: "start-business", emoji: "🚀", title: "Start a Business", desc: "Build a local venture or startup from scratch" },
  { id: "local-opportunities", emoji: "📍", title: "Local Opportunities", desc: "Discover projects and businesses near you" },
  { id: "find-cofounder", emoji: "💡", title: "Find a Co-founder", desc: "Meet someone to build your dream with" },
  { id: "join-startup", emoji: "🛠️", title: "Join a Startup Team", desc: "Become part of an existing builder team" },
  { id: "offer-skills", emoji: "🎯", title: "Offer My Skills", desc: "Lend your expertise to meaningful projects" },
  { id: "explore", emoji: "🌍", title: "Just Exploring", desc: "See what's happening across Bharat" },
  { id: "hire-collaborators", emoji: "👥", title: "Hire Collaborators", desc: "Bring talent for your existing project" },
];

export default function GetStartedPage() {
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const supabase = createClient();

  const handleContinue = async () => {
    if (!selected) return;
    setLoading(true);
    setErr("");
    try {
      localStorage.setItem("vw_intent", selected);
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: `${window.location.origin}/auth/callback?intent=${selected}`,
        },
      });
      if (error) throw error;
    } catch (e) {
      setErr(e.message || "Could not start Google sign-in.");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-cream to-warm py-12 px-6">
      <div className="max-w-4xl mx-auto">
        <Link href="/" data-testid="back-to-home" className="inline-flex items-center gap-1.5 min-h-[44px] text-sm font-semibold text-muted hover:text-ink mb-6">
          ← Back to home
        </Link>

        <div className="text-center mb-12">
          <span className="chip bg-amber-200 text-amber-700 mb-4">CREATING AN ACCOUNT</span>
          <h1 className="font-display font-extrabold text-3xl sm:text-4xl md:text-5xl leading-tight tracking-tight mb-3 break-words">
            What brings you to<br className="sm:hidden" /> <span className="text-amber-500">ValueWeave</span>?
          </h1>
          <p className="text-muted max-w-lg mx-auto">
            An account is for working with people — collaborators, teams and
            posting your own ideas. Pick what fits best.
          </p>

          {/* PX PHASE 9 REFINEMENT — THE WALL CAME DOWN
              ------------------------------------------
              Every path off this page went through "Continue with Google". A
              first-generation student who wanted to know whether ValueWeave
              held anything useful had to hand over a Google account to find
              out, and the eight options above are all about collaborating
              with people — none of them is a scheme, a skill or a crop.

              So the knowledge is now reachable from here without an account,
              and the page says plainly which half needs one. Signing in is
              still the whole point of THIS page; it is no longer the price of
              admission to the site. */}
          <div className="mt-6 rounded-2xl border border-teal-200 bg-teal-50/60 px-5 py-4 max-w-lg mx-auto">
            <p className="font-display font-bold text-sm text-ink mb-1">
              Just want to look around?
            </p>
            <p className="text-sm text-muted mb-3">
              Every skill, scheme, business idea and district is free to read —
              no account, no sign-in.
            </p>
            <Link
              href="/knowledge"
              data-testid="getstarted-explore-free"
              className="inline-flex items-center justify-center gap-2 rounded-full bg-teal-500 text-white
                         px-5 py-2.5 font-display font-bold text-sm hover:bg-teal-600
                         transition-colors min-h-[44px]"
            >
              Explore without an account →
            </Link>
          </div>

          <p className="mt-4 text-sm text-stone-500">
            Already a member? <Link href="/signin" data-testid="getstarted-signin-link" className="inline-flex items-center min-h-[44px] text-amber-600 font-semibold hover:underline">Sign in →</Link>
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
          {INTENTS.map((it) => {
            const isSel = selected === it.id;
            return (
              <button
                key={it.id}
                data-testid={`intent-${it.id}`}
                onClick={() => setSelected(it.id)}
                className={`text-left p-5 rounded-2xl border-2 transition-all hover:-translate-y-1 ${
                  isSel ? "border-amber-500 bg-gradient-to-br from-amber-50 to-cream shadow-lg shadow-amber-500/20" : "border-stone-200 bg-white hover:border-amber-300"
                }`}
              >
                <div className="text-3xl mb-3">{it.emoji}</div>
                <div className="font-display font-bold text-sm mb-1">{it.title}</div>
                <div className="text-xs text-muted leading-relaxed">{it.desc}</div>
                {isSel && <div className="mt-3 text-xs font-bold text-amber-600">✓ Selected</div>}
              </button>
            );
          })}
        </div>

        {err && <div data-testid="auth-error" className="bg-rose-50 text-rose-700 text-sm rounded-lg px-4 py-3 mb-4 max-w-md mx-auto text-center">{err}</div>}

        <div className="flex flex-col items-center gap-3">
          <button
            data-testid="continue-to-auth"
            disabled={!selected || loading}
            onClick={handleContinue}
            className={`btn-primary !px-8 !py-4 text-base ${(!selected || loading) ? "!bg-stone-300 !shadow-none cursor-not-allowed" : ""}`}
          >
            {loading ? "Redirecting…" : "Continue with Google →"}
          </button>
          <p className="text-xs text-stone-400">We'll sign you in with Google. No password needed.</p>
        </div>
      </div>
    </div>
  );
}
