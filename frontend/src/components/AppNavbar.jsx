import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { useState } from "react";

export default function AppNavbar() {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();

  const linkStyle = ({ isActive }) => ({
    padding: "8px 14px",
    borderRadius: 8,
    fontSize: 14,
    fontWeight: 600,
    color: isActive ? "#C2410C" : "#78716C",
    background: isActive ? "#FED7AA" : "transparent",
    textDecoration: "none",
    transition: "all 0.2s",
  });

  return (
    <nav style={{
      position: "sticky", top: 0, zIndex: 50,
      background: "rgba(255,251,245,0.94)", backdropFilter: "blur(14px)",
      borderBottom: "1px solid #E7E5E4", padding: "0 24px",
    }}>
      <div style={{
        maxWidth: 1180, margin: "0 auto", height: 64,
        display: "flex", alignItems: "center", justifyContent: "space-between",
      }}>
        <Link to="/dashboard" data-testid="navbar-logo" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: "linear-gradient(135deg,#F97316,#FBBF24)", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 4px 12px rgba(249,115,22,0.35)" }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 3L4 7.5V16.5L12 21L20 16.5V7.5L12 3Z" stroke="#fff" strokeWidth="2" strokeLinejoin="round"/><path d="M4 7.5L12 12M12 12L20 7.5M12 12V21" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>
          </div>
          <span style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: 19, color: "#1C1917", letterSpacing: "-0.5px" }}>
            Value<span style={{ color: "#F97316" }}>Weave</span>
          </span>
        </Link>

        <div style={{ display: "flex", gap: 4, alignItems: "center" }} className="vw-desktop-only">
          <NavLink to="/dashboard" style={linkStyle} data-testid="nav-feed">Feed</NavLink>
          <NavLink to="/opportunities/new" style={linkStyle} data-testid="nav-post">Post</NavLink>
          <NavLink to="/connections" style={linkStyle} data-testid="nav-connections">Connections</NavLink>
          <NavLink to="/profile" style={linkStyle} data-testid="nav-profile">Profile</NavLink>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 10, position: "relative" }}>
          <button
            data-testid="user-menu-trigger"
            onClick={() => setMenuOpen(o => !o)}
            style={{
              display: "flex", alignItems: "center", gap: 8,
              background: "white", border: "1px solid #E7E5E4",
              borderRadius: 50, padding: "5px 14px 5px 5px", cursor: "pointer",
            }}>
            {user?.picture ? (
              <img src={user.picture} alt="" style={{ width: 30, height: 30, borderRadius: "50%" }} />
            ) : (
              <div style={{ width: 30, height: 30, borderRadius: "50%", background: "#FED7AA", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, color: "#C2410C", fontSize: 13 }}>
                {(user?.name || "?")[0].toUpperCase()}
              </div>
            )}
            <span style={{ fontSize: 13, fontWeight: 600, color: "#1C1917" }} className="vw-desktop-only">{user?.name?.split(" ")[0]}</span>
          </button>
          {menuOpen && (
            <div style={{
              position: "absolute", top: 50, right: 0, background: "white",
              border: "1px solid #E7E5E4", borderRadius: 12, minWidth: 200,
              boxShadow: "0 12px 32px rgba(0,0,0,0.1)", padding: 6, zIndex: 100,
            }}>
              <button onClick={() => { setMenuOpen(false); navigate("/profile"); }} style={menuItem} data-testid="menu-profile">My Profile</button>
              <button onClick={() => { setMenuOpen(false); navigate("/connections"); }} style={menuItem} data-testid="menu-connections">My Connections</button>
              <div style={{ height: 1, background: "#E7E5E4", margin: "4px 0" }} />
              <button onClick={logout} style={{ ...menuItem, color: "#C2410C" }} data-testid="menu-logout">Sign out</button>
            </div>
          )}
        </div>
      </div>
      <style>{`@media (max-width: 720px) { .vw-desktop-only { display: none !important; } }`}</style>
    </nav>
  );
}

const menuItem = {
  display: "block", width: "100%", textAlign: "left",
  padding: "10px 12px", background: "transparent", border: "none",
  borderRadius: 8, fontSize: 14, fontWeight: 500, color: "#1C1917", cursor: "pointer",
};
