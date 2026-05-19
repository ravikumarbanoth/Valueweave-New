import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

const SKILL_SUGGESTIONS = ["Python","JavaScript","React","Design","Marketing","Sales","AI/ML","Mobile Dev","Content","Electronics","Agriculture","Finance","Operations","Writing","Video","Drone Piloting","EV Tech","Carpentry","Electrical","Photography"];

export default function Onboarding() {
  const navigate = useNavigate();
  const { user, setUser } = useAuth();
  const [city, setCity] = useState(user?.city || "");
  const [bio, setBio] = useState(user?.bio || "");
  const [skills, setSkills] = useState(user?.skills || []);
  const [skillInput, setSkillInput] = useState("");
  const [interests, setInterests] = useState(user?.interests || []);
  const [lookingFor, setLookingFor] = useState(user?.looking_for || localStorage.getItem("vw_intent") || "find-collaborators");
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState("");

  const addSkill = (s) => {
    const v = s.trim();
    if (!v || skills.includes(v)) return;
    setSkills([...skills, v]);
    setSkillInput("");
  };
  const removeSkill = (s) => setSkills(skills.filter(x => x !== s));

  const submit = async (e) => {
    e.preventDefault();
    setErr("");
    if (!city.trim() || skills.length === 0) {
      setErr("Please add your city and at least one skill.");
      return;
    }
    setSaving(true);
    try {
      const res = await api.put("/users/me", {
        city: city.trim(),
        bio: bio.trim(),
        skills,
        interests,
        looking_for: lookingFor,
      });
      setUser(res.data);
      localStorage.removeItem("vw_intent");
      navigate("/dashboard", { replace: true });
    } catch (e) {
      setErr(e.response?.data?.detail || "Could not save profile.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: "#FFFBF5", padding: "48px 24px 80px" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@400;500;600&display=swap');`}</style>
      <div style={{ maxWidth: 640, margin: "0 auto", fontFamily: "'DM Sans',sans-serif" }}>
        <div style={{ textAlign: "center", marginBottom: 36 }}>
          <span style={{ display: "inline-block", background: "#CCFBF1", color: "#0F766E", borderRadius: 50, padding: "6px 18px", fontSize: 12, fontWeight: 700, marginBottom: 14 }}>STEP 2 OF 3</span>
          <h1 style={{ fontFamily: "'Syne',sans-serif", fontSize: 32, fontWeight: 800, color: "#1C1917", letterSpacing: "-0.8px", marginBottom: 10 }}>
            Tell us about <span style={{ color: "#0D9488" }}>you</span>
          </h1>
          <p style={{ color: "#78716C", fontSize: 15 }}>This helps you find the right people to build with.</p>
        </div>

        <form onSubmit={submit} style={{ background: "white", border: "1px solid #E7E5E4", borderRadius: 20, padding: 28, display: "flex", flexDirection: "column", gap: 22 }}>
          <Field label="City" required>
            <input data-testid="onboarding-city" value={city} onChange={e => setCity(e.target.value)} placeholder="e.g. Nashik, Maharashtra" style={inputStyle} />
          </Field>

          <Field label="Skills" required hint="Add 3–6 skills that describe what you do best.">
            <div style={{ display: "flex", gap: 8 }}>
              <input
                data-testid="onboarding-skill-input"
                value={skillInput}
                onChange={e => setSkillInput(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter") { e.preventDefault(); addSkill(skillInput); } }}
                placeholder="Type a skill and press Enter"
                style={inputStyle}
              />
              <button type="button" onClick={() => addSkill(skillInput)} data-testid="onboarding-skill-add" style={{ background: "#0D9488", color: "white", border: "none", borderRadius: 12, padding: "0 18px", fontWeight: 700, cursor: "pointer", fontFamily: "'Syne',sans-serif" }}>Add</button>
            </div>
            <div style={{ marginTop: 10, display: "flex", flexWrap: "wrap", gap: 6 }}>
              {SKILL_SUGGESTIONS.filter(s => !skills.includes(s)).slice(0, 10).map(s => (
                <button key={s} type="button" onClick={() => addSkill(s)} style={chipSuggestion} data-testid={`skill-suggest-${s}`}>+ {s}</button>
              ))}
            </div>
            {skills.length > 0 && (
              <div style={{ marginTop: 12, display: "flex", flexWrap: "wrap", gap: 6 }}>
                {skills.map(s => (
                  <span key={s} data-testid={`skill-chip-${s}`} style={chipActive}>
                    {s}
                    <button type="button" onClick={() => removeSkill(s)} style={{ background: "none", border: "none", color: "#C2410C", cursor: "pointer", marginLeft: 4, fontWeight: 700 }}>×</button>
                  </span>
                ))}
              </div>
            )}
          </Field>

          <Field label="What are you looking for?">
            <select data-testid="onboarding-looking-for" value={lookingFor} onChange={e => setLookingFor(e.target.value)} style={inputStyle}>
              <option value="find-collaborators">Find Collaborators</option>
              <option value="start-business">Start a Business</option>
              <option value="local-opportunities">Local Opportunities</option>
              <option value="find-cofounder">Find a Co-founder</option>
              <option value="join-startup">Join a Startup Team</option>
              <option value="offer-skills">Offer My Skills</option>
              <option value="explore">Just Exploring</option>
              <option value="hire-collaborators">Hire Collaborators</option>
            </select>
          </Field>

          <Field label="Short bio" hint="One or two sentences about what you build and care about.">
            <textarea data-testid="onboarding-bio" value={bio} onChange={e => setBio(e.target.value)} rows={3} placeholder="e.g. Electronics diploma holder building EV charging stations in tier-2 cities." style={{ ...inputStyle, resize: "vertical", fontFamily: "inherit" }} />
          </Field>

          {err && <div data-testid="onboarding-error" style={{ background: "#FEF2F2", color: "#B91C1C", padding: "10px 14px", borderRadius: 10, fontSize: 13 }}>{err}</div>}

          <button data-testid="onboarding-submit" type="submit" disabled={saving} style={{
            background: "#F97316", color: "white", border: "none", borderRadius: 50,
            padding: "14px 28px", fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 15,
            cursor: saving ? "wait" : "pointer", boxShadow: "0 8px 24px rgba(249,115,22,0.35)",
          }}>
            {saving ? "Saving…" : "Continue to Dashboard →"}
          </button>
        </form>
      </div>
    </div>
  );
}

function Field({ label, hint, required, children }) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <span style={{ fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 13, color: "#1C1917" }}>
        {label}{required && <span style={{ color: "#F97316" }}> *</span>}
      </span>
      {children}
      {hint && <span style={{ fontSize: 12, color: "#A8A29E" }}>{hint}</span>}
    </label>
  );
}

const inputStyle = {
  width: "100%", padding: "11px 14px", borderRadius: 12,
  border: "1.5px solid #E7E5E4", fontSize: 14, outline: "none",
  background: "white", color: "#1C1917", fontFamily: "inherit",
  transition: "border-color 0.2s",
};
const chipSuggestion = {
  background: "#F5F4F0", color: "#57534E", border: "1px solid #E7E5E4",
  borderRadius: 50, padding: "4px 10px", fontSize: 12, fontWeight: 500, cursor: "pointer",
};
const chipActive = {
  background: "#FED7AA", color: "#C2410C", borderRadius: 50,
  padding: "4px 10px", fontSize: 12, fontWeight: 700,
  display: "inline-flex", alignItems: "center",
};
