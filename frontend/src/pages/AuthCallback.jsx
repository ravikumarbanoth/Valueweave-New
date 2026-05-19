// REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export default function AuthCallback() {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const hasProcessed = useRef(false);

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const hash = window.location.hash || "";
    const match = hash.match(/session_id=([^&]+)/);
    if (!match) {
      navigate("/", { replace: true });
      return;
    }
    const sessionId = match[1];

    (async () => {
      try {
        const res = await api.post(
          "/auth/session",
          {},
          { headers: { "X-Session-ID": sessionId } }
        );
        // store token as fallback for environments where cookies are blocked
        if (res.data.session_token) {
          localStorage.setItem("vw_token", res.data.session_token);
        }
        setUser(res.data.user);
        // Clear hash and route
        window.history.replaceState(null, "", "/dashboard");
        if (!res.data.user.profile_complete) {
          navigate("/onboarding", { replace: true, state: { user: res.data.user } });
        } else {
          navigate("/dashboard", { replace: true, state: { user: res.data.user } });
        }
      } catch (e) {
        console.error("Auth exchange failed", e);
        navigate("/", { replace: true });
      }
    })();
  }, [navigate, setUser]);

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#FFFBF5" }}>
      <div style={{ textAlign: "center" }}>
        <div data-testid="auth-callback-loading" style={{
          width: 48, height: 48, borderRadius: "50%",
          border: "3px solid #FED7AA", borderTopColor: "#F97316",
          animation: "spin 0.8s linear infinite", margin: "0 auto 16px"
        }} />
        <p style={{ fontFamily: "'Syne',sans-serif", fontWeight: 700, color: "#1C1917" }}>Signing you in…</p>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    </div>
  );
}
