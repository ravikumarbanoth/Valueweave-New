"use client";
// REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { createClient } from "@/lib/supabase-browser";

export default function SignInPage() {
  const supabase = createClient();
  const router = useRouter();
  const [state, setState] = useState("checking"); // checking | ready | redirecting | error
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        // Already signed in — smart route
        const { data: profile } = await supabase
          .from("profiles")
          .select("profile_complete")
          .eq("id", user.id)
          .single();
        router.replace(profile?.profile_complete ? "/dashboard" : "/onboarding");
        return;
      }
      setState("ready");
    })();
  }, [supabase, router]);

  const signIn = async () => {
    setState("redirecting");
    setErr("");
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
          redirectTo: `${window.location.origin}/auth/callback`,
        },
      });
      if (error) throw error;
    } catch (e) {
      setState("ready");
      setErr(e.message || "Could not start Google sign-in.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-cream to-warm flex items-center justify-center px-6">
      <div className="max-w-md w-full text-center">
        <Link href="/" className="inline-flex items-center gap-2.5 mb-8">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-yellow-400 flex items-center justify-center">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M12 3L4 7.5V16.5L12 21L20 16.5V7.5L12 3Z" stroke="#fff" strokeWidth="2" strokeLinejoin="round"/><path d="M4 7.5L12 12M12 12L20 7.5M12 12V21" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>
          </div>
          <span className="font-display font-extrabold text-xl tracking-tight">Value<span className="text-amber-500">Weave</span></span>
        </Link>

        <h1 className="font-display font-extrabold text-3xl sm:text-4xl tracking-tight mb-3">
          Welcome back
        </h1>
        <p className="text-muted text-base mb-8">
          Sign in to your ValueWeave account to access your dashboard, connections, and opportunities.
        </p>

        {state === "checking" && (
          <div data-testid="signin-loading" className="flex flex-col items-center gap-3 py-6">
            <div className="w-9 h-9 rounded-full border-[3px] border-amber-200 border-t-amber-500 animate-spin" />
            <p className="text-sm text-muted">Checking your session…</p>
          </div>
        )}

        {state !== "checking" && (
          <>
            <button
              data-testid="signin-google"
              onClick={signIn}
              disabled={state === "redirecting"}
              className="btn-primary w-full !py-3.5 text-base disabled:opacity-60"
            >
              {state === "redirecting" ? "Redirecting…" : (
                <>
                  <GoogleIcon /> Continue with Google
                </>
              )}
            </button>
            {err && <div data-testid="signin-error" className="mt-4 text-sm text-rose-700 bg-rose-50 border border-rose-200 rounded-xl px-4 py-2.5">{err}</div>}
            <p className="text-xs text-stone-400 mt-5">
              New to ValueWeave? <Link href="/get-started" className="text-amber-600 font-semibold hover:underline">Create your profile →</Link>
            </p>
          </>
        )}

        <Link href="/" className="inline-block mt-8 text-xs text-muted hover:text-ink">← Back to home</Link>
      </div>
    </div>
  );
}

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" xmlns="http://www.w3.org/2000/svg">
      <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z" fill="#4285F4"/>
      <path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z" fill="#34A853"/>
      <path d="M3.964 10.71A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>
      <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z" fill="#EA4335"/>
    </svg>
  );
}
