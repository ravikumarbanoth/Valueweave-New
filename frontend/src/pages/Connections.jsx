import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "@/lib/api";
import AppNavbar from "@/components/AppNavbar";

export default function Connections() {
  const [tab, setTab] = useState("received");
  const [received, setReceived] = useState([]);
  const [sent, setSent] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const [r, s] = await Promise.all([
        api.get("/connections/received"),
        api.get("/connections/sent"),
      ]);
      setReceived(r.data);
      setSent(s.data);
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const update = async (id, status) => {
    await api.put(`/connections/${id}`, null, { params: { status } });
    load();
  };

  const list = tab === "received" ? received : sent;

  return (
    <div style={{ minHeight: "100vh", background: "#FFFBF5", fontFamily: "'DM Sans',sans-serif" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@400;500;600&display=swap');`}</style>
      <AppNavbar />
      <main style={{ maxWidth: 820, margin: "0 auto", padding: "32px 24px 80px" }}>
        <h1 style={{ fontFamily: "'Syne',sans-serif", fontSize: 28, fontWeight: 800, color: "#1C1917", marginBottom: 18 }}>Connections</h1>

        <div style={{ display: "flex", gap: 8, marginBottom: 20, background: "white", padding: 6, borderRadius: 50, border: "1px solid #E7E5E4", width: "fit-content" }}>
          {[["received","Received"],["sent","Sent"]].map(([k, l]) => (
            <button
              key={k}
              data-testid={`tab-${k}`}
              onClick={() => setTab(k)}
              style={{
                background: tab === k ? "#1C1917" : "transparent",
                color: tab === k ? "white" : "#57534E",
                border: "none", borderRadius: 50, padding: "8px 20px",
                fontWeight: 700, fontSize: 13, cursor: "pointer", fontFamily: "'Syne',sans-serif",
              }}>
              {l} ({(k === "received" ? received : sent).length})
            </button>
          ))}
        </div>

        {loading ? <p>Loading…</p> : list.length === 0 ? (
          <div data-testid="connections-empty" style={{ background: "white", border: "2px dashed #E7E5E4", borderRadius: 14, padding: 48, textAlign: "center", color: "#78716C" }}>
            <div style={{ fontSize: 36, marginBottom: 8 }}>📭</div>
            No {tab} connection requests yet.
          </div>
        ) : (
          <div style={{ display: "grid", gap: 14 }}>
            {list.map(c => (
              <div key={c.connection_id} data-testid={`conn-${c.connection_id}`} style={{ background: "white", border: "1px solid #E7E5E4", borderRadius: 16, padding: 20 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
                  {(tab === "received" ? c.from_user_picture : null) ? (
                    <img src={c.from_user_picture} alt="" style={{ width: 40, height: 40, borderRadius: "50%" }} />
                  ) : (
                    <div style={{ width: 40, height: 40, borderRadius: "50%", background: "#FED7AA", color: "#C2410C", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700 }}>
                      {(tab === "received" ? c.from_user_name : c.to_user_name)[0]}
                    </div>
                  )}
                  <div style={{ flex: 1 }}>
                    <div style={{ fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 14, color: "#1C1917" }}>
                      {tab === "received" ? c.from_user_name : `To: ${c.to_user_name}`}
                    </div>
                    <Link to={`/opportunities/${c.opportunity_id}`} style={{ fontSize: 12, color: "#0D9488", textDecoration: "none", fontWeight: 600 }}>
                      re: {c.opportunity_title} →
                    </Link>
                  </div>
                  <span style={{
                    background: c.status === "accepted" ? "#F0FDF4" : c.status === "rejected" ? "#FEF2F2" : "#FFF7ED",
                    color: c.status === "accepted" ? "#0F766E" : c.status === "rejected" ? "#B91C1C" : "#C2410C",
                    borderRadius: 50, padding: "4px 12px", fontSize: 11, fontWeight: 700, textTransform: "uppercase",
                  }}>{c.status}</span>
                </div>
                <p style={{ color: "#1C1917", fontSize: 14, lineHeight: 1.6, padding: "10px 14px", background: "#FFFBF5", borderRadius: 10 }}>"{c.message}"</p>
                {tab === "received" && c.status === "pending" && (
                  <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
                    <button data-testid={`accept-${c.connection_id}`} onClick={() => update(c.connection_id, "accepted")} style={btnAccept}>Accept</button>
                    <button data-testid={`reject-${c.connection_id}`} onClick={() => update(c.connection_id, "rejected")} style={btnReject}>Decline</button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

const btnAccept = {
  background: "#0D9488", color: "white", border: "none", borderRadius: 50,
  padding: "8px 20px", fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 13, cursor: "pointer",
};
const btnReject = {
  background: "transparent", color: "#57534E", border: "1.5px solid #E7E5E4", borderRadius: 50,
  padding: "8px 20px", fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 13, cursor: "pointer",
};
