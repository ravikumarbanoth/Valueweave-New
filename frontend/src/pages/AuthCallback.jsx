import React, { useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { exchangeSession } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export default function AuthCallback() {
  const location = useLocation();
  const navigate = useNavigate();
  const { refresh } = useAuth();
  const hasProcessed = useRef(false);

  React.useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const hash = location.hash || window.location.hash || "";
    const match = hash.match(/session_id=([^&]+)/);
    const session_id = match ? decodeURIComponent(match[1]) : null;

    (async () => {
      if (!session_id) { navigate("/login", { replace: true }); return; }
      try {
        await exchangeSession(session_id);
        await refresh();
        // Clear hash, navigate to dashboard
        window.history.replaceState({}, "", "/dashboard");
        navigate("/dashboard", { replace: true });
      } catch (e) {
        navigate("/login?error=session", { replace: true });
      }
    })();
  }, [location, navigate, refresh]);

  return (
    <div className="min-h-[60vh] flex items-center justify-center" data-testid="auth-callback">
      <div className="text-center">
        <div className="mx-auto h-10 w-10 rounded-full border-4 border-primary border-t-transparent animate-spin mb-4" />
        <p className="text-muted-foreground">Signing you in…</p>
      </div>
    </div>
  );
}
