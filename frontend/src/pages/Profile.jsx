import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "@/lib/api";
import AppNavbar from "@/components/AppNavbar";
import { useAuth } from "@/context/AuthContext";

export default function Profile() {
  const { userId } = useParams();
  const { user: me } = useAuth();
  const [profileUser, setProfileUser] = useState(null);
  const [opps, setOpps] = useState([]);
  const [loading, setLoading] = useState(true);

  const targetId = userId || me?.user_id;
  const isMe = !userId || userId === me?.user_id;

  useEffect(() => {
    if (!targetId) return;
    (async () => {
      try {
        const u = isMe ? { data: me } : await api.get(`/users/${targetId}`);
        setProfileUser(u.data);
        const o = await api.get("/opportunities", { params: { owner_id: targetId } });
        setOpps(o.data);
      } finally { setLoading(false); }
    })();
  }, [targetId, isMe, me]);

  if (loading) return <Shell><p>Loading…</p></Shell>;
  if (!profileUser) return <Shell><p>User not found.</p></Shell>;

  return (
    <Shell>
      <div style={{ background: "white", border: "1px solid #E7E5E4", borderRadius: 20, padding: 32, marginBottom: 24 }}>
        <div style={{ display: "flex", gap: 20, alignItems: "center", flexWrap: "wrap" }}>
          {profileUser.picture ? (
            <img src={profileUser.picture} alt="" style={{ width: 90, height: 90, borderRadius: "50%", border: "3px solid #FED7AA" }} />
          ) : (
            <div style={{ width: 90, height: 90, borderRadius: "50%", background: "#FED7AA", color: "#C2410C", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 36, fontWeight: 800 }}>{profileUser.name[0]}</div>
          )}
          <div style={{ flex: 1, minWidth: 220 }}>
            <h1 data-testid="profile-name" style={{ fontFamily: "'Syne',sans-serif", fontSize: 26, fontWeight: 800, color: "#1C1917", marginBottom: 4 }}>{profileUser.name}</h1>
            {profileUser.city && <p style={{ color: "#78716C", fontSize: 14, marginBottom: 6 }}>📍 {profileUser.city}</p>}
            {profileUser.looking_for && <span style={{ display: "inline-block", background: "#CCFBF1", color: "#0F766E", borderRadius: 50, padding: "4px 12px", fontSize: 12, fontWeight: 700 }}>Looking for: {profileUser.looking_for.replace(/-/g, " ")}</span>}
          </div>
          {isMe && <Link to="/onboarding" data-testid="edit-profile" style={{ background: "#F5F4F0", color: "#1C1917", textDecoration: "none", padding: "10px 20px", borderRadius: 50, fontWeight: 700, fontSize: 13, fontFamily: "'Syne',sans-serif" }}>Edit profile</Link>}
        </div>
        {profileUser.bio && <p style={{ marginTop: 18, color: "#1C1917", fontSize: 15, lineHeight: 1.7 }}>{profileUser.bio}</p>}
        {profileUser.skills?.length > 0 && (
          <div style={{ marginTop: 18 }}>
            <h3 style={{ fontFamily: "'Syne',sans-serif", fontSize: 12, fontWeight: 700, color: "#57534E", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.5px" }}>Skills</h3>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {profileUser.skills.map(s => <span key={s} style={{ background: "#F5F4F0", color: "#1C1917", borderRadius: 50, padding: "5px 12px", fontSize: 13, fontWeight: 600 }}>{s}</span>)}
            </div>
          </div>
        )}
      </div>

      <h2 style={{ fontFamily: "'Syne',sans-serif", fontSize: 20, fontWeight: 800, color: "#1C1917", marginBottom: 14 }}>
        {isMe ? "My opportunities" : `${profileUser.name.split(" ")[0]}'s opportunities`} ({opps.length})
      </h2>
      {opps.length === 0 ? (
        <div data-testid="profile-no-opps" style={{ background: "white", border: "2px dashed #E7E5E4", borderRadius: 14, padding: 36, textAlign: "center", color: "#78716C" }}>
          No opportunities posted yet.
        </div>
      ) : (
        <div style={{ display: "grid", gap: 12 }}>
          {opps.map(o => (
            <Link key={o.opportunity_id} to={`/opportunities/${o.opportunity_id}`} style={{
              textDecoration: "none", color: "inherit", background: "white",
              border: "1px solid #E7E5E4", borderRadius: 14, padding: 18,
            }}>
              <h3 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 16, color: "#1C1917", marginBottom: 4 }}>{o.title}</h3>
              <p style={{ fontSize: 13, color: "#78716C" }}>{o.category} · {o.location}</p>
            </Link>
          ))}
        </div>
      )}
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
