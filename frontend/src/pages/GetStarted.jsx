// REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
import { useState } from "react";
import { Link } from "react-router-dom";

const INTENTS = [
  { id: "find-collaborators", emoji: "🤝", title: "Find Collaborators", desc: "Connect with people who complement your skills" },
  { id: "start-business", emoji: "🚀", title: "Start a Business", desc: "Build a local venture or startup from scratch" },
  { id: "local-opportunities", emoji: "📍", title: "Local Opportunities", desc: "Discover projects and businesses near you" },
  { id: "find-cofounder", emoji: "💡", title: "Find a Co-founder", desc: "Meet someone to build your dream with" },
  { id: "join-startup", emoji: "🛠️", title: "Join a Startup Team", desc: "Become part of an existing builder team" },
  { id: "offer-skills", emoji: "🎯", title: "Offer My Skills", desc: "Lend your expertise to meaningful projects" },
  { id: "explore", emoji: "🌍", title: "Just Exploring", desc: "See what's happening across Bharat" },
  { id: "hire-collaborators", emoji: "👥", title: "Hire Collaborators", desc: "Bring in talent for your existing project" },
];

export default function GetStarted() {
  const [selected, setSelected] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleContinue = () => {
    if (!selected) return;
    setSubmitting(true);
    localStorage.setItem("vw_intent", selected);
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + "/dashboard";
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  return (
    <div style={{ minHeight: "100vh", background: "linear-gradient(180deg,#FFFBF5 0%, #FFF8F0 100%)", padding: "48px 24px 80px" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@400;500;600&display=swap');
        .gs-card { transition: all 0.2s ease; }
        .gs-card:hover { transform: translateY(-3px); box-shadow: 0 12px 32px rgba(0,0,0,0.08); border-color: #F97316; }
        .gs-card.selected { border-color: #F97316 !important; background: linear-gradient(135deg,#FFF7ED,#FFFBF5) !important; box-shadow: 0 8px 28px rgba(249,115,22,0.18) !important; }
      `}</style>

      <div style={{ maxWidth: 920, margin: "0 auto" }}>
        <Link to="/" data-testid="back-to-home" style={{ display: "inline-flex", alignItems: "center", gap: 6, color: "#78716C", textDecoration: "none", fontSize: 14, fontWeight: 500, marginBottom: 32 }}>
          ← Back to home
        </Link>

        <div style={{ textAlign: "center", marginBottom: 48 }}>
          <span style={{ display: "inline-block", background: "#FED7AA", color: "#C2410C", borderRadius: 50, padding: "6px 18px", fontSize: 12, fontWeight: 700, marginBottom: 18, letterSpacing: "0.5px" }}>STEP 1 OF 3</span>
          <h1 style={{ fontFamily: "'Syne',sans-serif", fontSize: "clamp(28px,4vw,46px)", fontWeight: 800, color: "#1C1917", letterSpacing: "-1px", lineHeight: 1.1, marginBottom: 14 }}>
            What brings you to <span style={{ color: "#F97316" }}>ValueWeave</span>?
          </h1>
          <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: 16, color: "#78716C", maxWidth: 520, margin: "0 auto" }}>
            Pick what fits best. You can always change this later or pick multiple things on your profile.
          </p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(220px,1fr))", gap: 16, marginBottom: 36 }}>
          {INTENTS.map((it) => (
            <button
              key={it.id}
              data-testid={`intent-${it.id}`}
              onClick={() => setSelected(it.id)}
              className={`gs-card${selected === it.id ? " selected" : ""}`}
              style={{
                background: "white", border: "2px solid #E7E5E4", borderRadius: 16,
                padding: 22, textAlign: "left", cursor: "pointer", fontFamily: "'DM Sans',sans-serif",
              }}>
              <div style={{ fontSize: 32, marginBottom: 12 }}>{it.emoji}</div>
              <div style={{ fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 15, color: "#1C1917", marginBottom: 6 }}>{it.title}</div>
              <div style={{ fontSize: 13, color: "#78716C", lineHeight: 1.55 }}>{it.desc}</div>
              {selected === it.id && (
                <div style={{ marginTop: 12, display: "inline-flex", alignItems: "center", gap: 4, fontSize: 12, fontWeight: 700, color: "#F97316" }}>
                  ✓ Selected
                </div>
              )}
            </button>
          ))}
        </div>

        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 14 }}>
          <button
            data-testid="continue-to-auth"
            disabled={!selected || submitting}
            onClick={handleContinue}
            style={{
              background: selected ? "#F97316" : "#E7E5E4",
              color: selected ? "white" : "#A8A29E",
              border: "none", borderRadius: 50, padding: "16px 40px",
              fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 15,
              cursor: selected ? "pointer" : "not-allowed",
              boxShadow: selected ? "0 8px 24px rgba(249,115,22,0.35)" : "none",
              transition: "all 0.2s",
            }}>
            {submitting ? "Redirecting…" : "Continue with Google →"}
          </button>
          <p style={{ fontSize: 12, color: "#A8A29E", fontFamily: "'DM Sans',sans-serif" }}>
            We'll sign you in with Google. No password needed.
          </p>
        </div>
      </div>
    </div>
  );
}
