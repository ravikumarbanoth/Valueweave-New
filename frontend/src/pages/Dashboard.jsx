import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import { api } from "@/lib/api";
import AppNavbar from "@/components/AppNavbar";
import { useAuth } from "@/context/AuthContext";

const CATEGORIES = [
  { id: "", emoji: "🌐", label: "All" },
  { id: "ai-tech", emoji: "🤖", label: "AI & Tech" },
  { id: "local-business", emoji: "🏪", label: "Local Business" },
  { id: "ev-electronics", emoji: "⚡", label: "EV & Electronics" },
  { id: "drone", emoji: "🚁", label: "Drone" },
  { id: "agri", emoji: "🌾", label: "Agriculture" },
  { id: "student", emoji: "🎓", label: "Student" },
  { id: "trades", emoji: "🔧", label: "Trades" },
  { id: "digital", emoji: "📱", label: "Digital" },
];

export default function Dashboard() {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState("");
  const [search, setSearch] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (category) params.category = category;
      if (search.trim()) params.search = search.trim();
      const res = await api.get("/opportunities", { params });
      setItems(res.data);
    } finally { setLoading(false); }
  }, [category, search]);

  useEffect(() => { load(); }, [load]);

  return (
    <div style={{ minHeight: "100vh", background: "#FFFBF5", fontFamily: "'DM Sans',sans-serif" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@400;500;600&display=swap');`}</style>
      <AppNavbar />

      <main style={{ maxWidth: 1180, margin: "0 auto", padding: "36px 24px 80px" }}>
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: 16, marginBottom: 28 }}>
          <div>
            <h1 data-testid="dashboard-greeting" style={{ fontFamily: "'Syne',sans-serif", fontSize: 32, fontWeight: 800, color: "#1C1917", letterSpacing: "-0.8px", marginBottom: 6 }}>
              Hey {user?.name?.split(" ")[0]} 👋
            </h1>
            <p style={{ color: "#78716C", fontSize: 15 }}>Browse open opportunities, or post your own.</p>
          </div>
          <Link to="/opportunities/new" data-testid="cta-post-opportunity" style={{
            background: "#F97316", color: "white", textDecoration: "none",
            padding: "12px 22px", borderRadius: 50, fontFamily: "'Syne',sans-serif",
            fontWeight: 700, fontSize: 14, boxShadow: "0 8px 24px rgba(249,115,22,0.35)",
          }}>+ Post Opportunity</Link>
        </div>

        {/* Filters */}
        <div style={{ background: "white", border: "1px solid #E7E5E4", borderRadius: 16, padding: 16, marginBottom: 24 }}>
          <input
            data-testid="dashboard-search"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search opportunities by title, skill, or keyword…"
            style={{ width: "100%", padding: "11px 14px", borderRadius: 12, border: "1.5px solid #E7E5E4", fontSize: 14, outline: "none", marginBottom: 12 }}
          />
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6, overflowX: "auto" }}>
            {CATEGORIES.map(c => (
              <button
                key={c.id || "all"}
                data-testid={`filter-${c.id || "all"}`}
                onClick={() => setCategory(c.id)}
                style={{
                  background: category === c.id ? "#1C1917" : "#F5F4F0",
                  color: category === c.id ? "white" : "#57534E",
                  border: "none", borderRadius: 50, padding: "8px 14px",
                  fontSize: 13, fontWeight: 600, cursor: "pointer", whiteSpace: "nowrap",
                }}>
                {c.emoji} {c.label}
              </button>
            ))}
          </div>
        </div>

        {/* Feed */}
        {loading ? (
          <div data-testid="feed-loading" style={{ textAlign: "center", padding: 60, color: "#78716C" }}>Loading opportunities…</div>
        ) : items.length === 0 ? (
          <div data-testid="feed-empty" style={{ background: "white", border: "2px dashed #E7E5E4", borderRadius: 16, padding: 56, textAlign: "center" }}>
            <div style={{ fontSize: 48, marginBottom: 12 }}>🌱</div>
            <h3 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, color: "#1C1917", marginBottom: 8 }}>No opportunities yet</h3>
            <p style={{ color: "#78716C", fontSize: 14, marginBottom: 18 }}>Be the first to post one for your community.</p>
            <Link to="/opportunities/new" style={{ background: "#F97316", color: "white", textDecoration: "none", padding: "10px 22px", borderRadius: 50, fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 14 }}>Post the first opportunity →</Link>
          </div>
        ) : (
          <div data-testid="feed-list" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(320px,1fr))", gap: 18 }}>
            {items.map(opp => <OpportunityCard key={opp.opportunity_id} opp={opp} />)}
          </div>
        )}
      </main>
    </div>
  );
}

function OpportunityCard({ opp }) {
  const cat = CATEGORIES.find(c => c.id === opp.category);
  return (
    <Link
      to={`/opportunities/${opp.opportunity_id}`}
      data-testid={`opp-card-${opp.opportunity_id}`}
      style={{
        textDecoration: "none", color: "inherit", background: "white",
        border: "1px solid #E7E5E4", borderRadius: 16, padding: 22,
        display: "flex", flexDirection: "column", gap: 12,
        transition: "all 0.2s",
      }}
      onMouseEnter={e => { e.currentTarget.style.transform = "translateY(-4px)"; e.currentTarget.style.boxShadow = "0 16px 40px rgba(0,0,0,0.08)"; e.currentTarget.style.borderColor = "#F97316"; }}
      onMouseLeave={e => { e.currentTarget.style.transform = ""; e.currentTarget.style.boxShadow = ""; e.currentTarget.style.borderColor = "#E7E5E4"; }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8 }}>
        <span style={{ background: "#FFF7ED", color: "#C2410C", borderRadius: 50, padding: "4px 12px", fontSize: 11, fontWeight: 700 }}>
          {cat?.emoji} {cat?.label || opp.category}
        </span>
        <span style={{ fontSize: 11, color: "#A8A29E" }}>📍 {opp.location}</span>
      </div>
      <h3 style={{ fontFamily: "'Syne',sans-serif", fontSize: 17, fontWeight: 700, color: "#1C1917", lineHeight: 1.3 }}>{opp.title}</h3>
      <p style={{ fontSize: 13.5, color: "#78716C", lineHeight: 1.6, display: "-webkit-box", WebkitLineClamp: 3, WebkitBoxOrient: "vertical", overflow: "hidden" }}>{opp.description}</p>
      {opp.skills_needed.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
          {opp.skills_needed.slice(0, 4).map(s => (
            <span key={s} style={{ background: "#F5F4F0", color: "#57534E", borderRadius: 50, padding: "3px 9px", fontSize: 11, fontWeight: 600 }}>{s}</span>
          ))}
        </div>
      )}
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 6, paddingTop: 12, borderTop: "1px solid #F5F4F0" }}>
        {opp.owner_picture ? (
          <img src={opp.owner_picture} alt="" style={{ width: 28, height: 28, borderRadius: "50%" }} />
        ) : (
          <div style={{ width: 28, height: 28, borderRadius: "50%", background: "#FED7AA", color: "#C2410C", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 700 }}>{opp.owner_name[0]}</div>
        )}
        <span style={{ fontSize: 12, fontWeight: 600, color: "#1C1917" }}>{opp.owner_name}</span>
        <span style={{ fontSize: 11, color: "#A8A29E", marginLeft: "auto" }}>
          {opp.collaboration_type} · {opp.commitment}
        </span>
      </div>
    </Link>
  );
}
