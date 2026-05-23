import React from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { ArrowLeft, Sparkles } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function Login() {
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const [params] = useSearchParams();
  const next = params.get("next") || "/dashboard";

  React.useEffect(() => {
    if (!loading && user) navigate(next, { replace: true });
  }, [user, loading, navigate, next]);

  const handleGoogle = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + "/dashboard";
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  return (
    <div data-testid="login-page" className="min-h-[80vh] vw-container flex items-center justify-center py-12">
      <div className="grid grid-cols-1 lg:grid-cols-2 max-w-5xl w-full gap-10 items-center">
        <div className="space-y-5">
          <button onClick={() => navigate(-1)} className="inline-flex items-center gap-2 text-sm font-semibold text-muted-foreground hover:text-primary" data-testid="login-back">
            <ArrowLeft className="h-4 w-4" /> Back
          </button>
          <span className="vw-chip"><Sparkles className="h-3 w-3" /> Welcome to ValueWeave</span>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight leading-tight" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
            Sign in to build with Bharat's most ambitious community.
          </h1>
          <p className="text-muted-foreground max-w-md">
            Browsing is free — sign in to save ideas, join teams, message collaborators and create opportunities.
          </p>
        </div>

        <div className="vw-card p-8 md:p-10 space-y-5">
          <div>
            <div className="vw-section-label mb-2">Continue with</div>
            <h2 className="text-2xl font-bold tracking-tight" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>One click, no passwords</h2>
          </div>
          <button onClick={handleGoogle} data-testid="login-google-btn" className="w-full vw-btn-outline py-3 text-base hover:bg-muted/50">
            <GoogleIcon /> Continue with Google
          </button>
          <p className="text-xs text-muted-foreground">
            By continuing, you agree to ValueWeave's Terms and acknowledge our Privacy Policy.
            We only use Google to verify your identity — no posting on your behalf.
          </p>
        </div>
      </div>
    </div>
  );
}

function GoogleIcon() {
  return (
    <svg viewBox="0 0 48 48" className="h-5 w-5">
      <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3c-1.6 4.4-5.8 7.5-10.8 7.5-6.4 0-11.5-5.2-11.5-11.5S18 12.5 24.5 12.5c2.9 0 5.5 1 7.5 2.7l5.7-5.7C34 6.2 29.5 4.5 24.5 4.5 13.7 4.5 5 13.2 5 24s8.7 19.5 19.5 19.5c11.2 0 19-7.8 19-19.5 0-1.2-.1-2.3-.4-3.5z"/>
      <path fill="#FF3D00" d="M6.3 14.1l6.6 4.8C14.5 15.1 19 12.5 24 12.5c2.9 0 5.5 1 7.5 2.7l5.7-5.7C34 6.2 29.5 4.5 24.5 4.5 16.7 4.5 9.9 9 6.3 14.1z"/>
      <path fill="#4CAF50" d="M24.5 43.5c5 0 9.4-1.7 12.7-4.5l-5.9-4.8c-2 1.4-4.5 2.3-6.8 2.3-5 0-9.2-3.1-10.8-7.4l-6.5 5C9.7 39.4 16.5 43.5 24.5 43.5z"/>
      <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.1-2.1 3.9-3.9 5.2l5.9 4.8c-.4.4 6.7-4.9 6.7-14 0-1.2-.1-2.3-.4-3.5z"/>
    </svg>
  );
}
