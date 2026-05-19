import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";

export default function ProtectedRoute({ children, requireProfile = false }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#FFFBF5" }}>
        <div data-testid="protected-loading" style={{
          width: 40, height: 40, borderRadius: "50%",
          border: "3px solid #FED7AA", borderTopColor: "#F97316",
          animation: "spin 0.8s linear infinite"
        }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }
  if (!user) return <Navigate to="/" replace state={{ from: location }} />;
  if (requireProfile && !user.profile_complete) return <Navigate to="/onboarding" replace />;
  return children;
}
