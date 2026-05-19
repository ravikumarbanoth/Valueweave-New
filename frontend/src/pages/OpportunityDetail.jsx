import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api } from "@/lib/api";
import AppNavbar from "@/components/AppNavbar";
import { useAuth } from "@/context/AuthContext";

export default function OpportunityDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [opp, setOpp] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showConnect, setShowConnect] = useState(false);
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [sentOk, setSentOk] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get(`/opportunities/${id}`);
        setOpp(res.data);
      } catch {} finally { setLoading(false); }
    })();
  }, [id]);

  const sendConnect = async () => {
    setErr("");
    if (!message.trim()) { setErr("Please add a message."); return; }
    setSending(true);
    try {
      await api.post(`/opportunities/${id}/connect`, { opportunity_id: id, message: message.trim() });
      setSentOk(true);
      setShowConnect(false);
    } catch (e) {
      setErr(e.response?.data?.detail || "Could not send.");
    } finally { setSending(false); }
  };

  const removeOpp = async () => {
    if (!window.confirm("Delete this opportunity?")) return;
    await api.delete(`/opportunities/${id}`);
    navigate("/dashboard");
  };

  if (loading) return <Shell><p data-testid="detail-loading">Loading…</p></Shell>;
  if (!opp) return <Shell><p data-testid="detail-not-found">Not found.</p></Shell>;

  const isOwner = user?.user_id === opp.owner_id;

  return (
    <Shell>
      <Link to="/dashboard" style={{ color: "#78716C", textDecoration: "none", fontSize: 14, marginBottom: 18, display: "inline-block" }}>← Back to feed</Link>

      <div style={{ background: "white", border: "1px solid #E7E5E4", borderRadius: 20, padding: 32 }}>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 14 }}>
          <span style={{ background: "#FFF7ED", color: "#C2410C", borderRadius: 50, padding: "5px 14px", fontSize: 12, fontWeight: 700 }}>{opp.category}</span>
          <span style={{ background: "#F0FDF4", color: "#0F766E", borderRadius: 50, padding: "5px 14px", fontSize: 12, fontWeight: 700 }}>{opp.collaboration_type}</span>
          <span style={{ background: "#F5F3FF", color: "#6D28D9", borderRadius: 50, padding: "5px 14px", fontSize: 12, fontWeight: 700 }}>{opp.commitment}</span>
        </div>

        <h1 data-testid="detail-title" style={{ fontFamily: "'Syne',sans-serif", fontSize: 30, fontWeight: 800, color: "#1C1917", letterSpacing: "-0.6px", marginBottom: 14, lineHeight: 1.2 }}>
          {opp.title}
        </h1>
        <p style={{ color: "#78716C", fontSize: 14, marginBottom: 24 }}>📍 {opp.location}</p>

        <div data-testid="detail-description" style={{ color: "#1C1917", fontSize: 15.5, lineHeight: 1.75, whiteSpace: "pre-wrap", marginBottom: 28 }}>
          {opp.description}
        </div>

        {opp.skills_needed.length > 0 && (
          <div style={{ marginBottom: 28 }}>
            <h3 style={{ fontFamily: "'Syne',sans-serif", fontSize: 13, fontWeight: 700, color: "#57534E", marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.5px" }}>Skills needed</h3>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {opp.skills_needed.map(s => (
                <span key={s} style={{ background: "#FED7AA", color: "#C2410C", borderRadius: 50, padding: "5px 12px", fontSize: 13, fontWeight: 700 }}>{s}</span>
              ))}
            </div>
          </div>
        )}

        <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "16px 0", borderTop: "1px solid #F5F4F0", borderBottom: "1px solid #F5F4F0", marginBottom: 24 }}>
          {opp.owner_picture ? (
            <img src={opp.owner_picture} alt="" style={{ width: 44, height: 44, borderRadius: "50%" }} />
          ) : (
            <div style={{ width: 44, height: 44, borderRadius: "50%", background: "#FED7AA", color: "#C2410C", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700 }}>{opp.owner_name[0]}</div>
          )}
          <div>
            <div style={{ fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 15, color: "#1C1917" }}>{opp.owner_name}</div>
            <Link to={`/profile/${opp.owner_id}`} style={{ fontSize: 12, color: "#0D9488", textDecoration: "none", fontWeight: 600 }}>View profile →</Link>
          </div>
        </div>

        {sentOk && <div data-testid="connect-success" style={{ background: "#F0FDF4", color: "#0F766E", padding: "12px 16px", borderRadius: 12, fontSize: 14, fontWeight: 600, marginBottom: 16 }}>✓ Connection request sent! Check the Connections page.</div>}

        {!isOwner && !sentOk && (
          showConnect ? (
            <div style={{ background: "#FFF7ED", borderRadius: 14, padding: 18 }}>
              <h4 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 700, marginBottom: 10, color: "#1C1917" }}>Send a connection request</h4>
              <textarea
                data-testid="connect-message"
                rows={4}
                value={message}
                onChange={e => setMessage(e.target.value)}
                placeholder="Introduce yourself — what's your background and why this opportunity?"
                style={{ width: "100%", padding: "11px 14px", borderRadius: 12, border: "1.5px solid #FED7AA", fontSize: 14, outline: "none", resize: "vertical", fontFamily: "inherit", background: "white" }}
              />
              {err && <div style={{ color: "#B91C1C", fontSize: 13, marginTop: 8 }}>{err}</div>}
              <div style={{ display: "flex", gap: 10, marginTop: 12 }}>
                <button data-testid="connect-send" onClick={sendConnect} disabled={sending} style={{
                  background: "#F97316", color: "white", border: "none", borderRadius: 50,
                  padding: "10px 22px", fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 13, cursor: "pointer",
                }}>{sending ? "Sending…" : "Send Request"}</button>
                <button onClick={() => setShowConnect(false)} style={{ background: "transparent", border: "1.5px solid #E7E5E4", borderRadius: 50, padding: "10px 22px", fontWeight: 600, cursor: "pointer", fontFamily: "'Syne',sans-serif", fontSize: 13 }}>Cancel</button>
              </div>
            </div>
          ) : (
            <button data-testid="connect-open" onClick={() => setShowConnect(true)} style={{
              background: "#0D9488", color: "white", border: "none", borderRadius: 50,
              padding: "13px 28px", fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 14,
              cursor: "pointer", boxShadow: "0 8px 24px rgba(13,148,136,0.3)",
            }}>🤝 Connect with {opp.owner_name.split(" ")[0]}</button>
          )
        )}
        {isOwner && (
          <button data-testid="opp-delete" onClick={removeOpp} style={{ background: "transparent", color: "#B91C1C", border: "1.5px solid #FECACA", borderRadius: 50, padding: "10px 22px", fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 13, cursor: "pointer" }}>Delete opportunity</button>
        )}
      </div>
    </Shell>
  );
}

function Shell({ children }) {
  return (
    <div style={{ minHeight: "100vh", background: "#FFFBF5", fontFamily: "'DM Sans',sans-serif" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@400;500;600&display=swap');`}</style>
      <AppNavbar />
      <main style={{ maxWidth: 820, margin: "0 auto", padding: "32px 24px 80px" }}>{children}</main>
    </div>
  );
}
