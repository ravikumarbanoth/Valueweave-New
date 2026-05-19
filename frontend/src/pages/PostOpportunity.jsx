import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import AppNavbar from "@/components/AppNavbar";

const CATEGORIES = [
  { id: "ai-tech", label: "AI & Tech" },
  { id: "local-business", label: "Local Business" },
  { id: "ev-electronics", label: "EV & Electronics" },
  { id: "drone", label: "Drone Services" },
  { id: "agri", label: "Agriculture" },
  { id: "student", label: "Student Startup" },
  { id: "trades", label: "Skilled Trades" },
  { id: "digital", label: "Digital Services" },
];

export default function PostOpportunity() {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("ai-tech");
  const [location, setLocation] = useState("");
  const [skillsRaw, setSkillsRaw] = useState("");
  const [collab, setCollab] = useState("cofounder");
  const [commit, setCommit] = useState("part-time");
  const [submitting, setSubmitting] = useState(false);
  const [err, setErr] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setErr("");
    if (!title.trim() || !description.trim() || !location.trim()) {
      setErr("Title, description, and location are required.");
      return;
    }
    setSubmitting(true);
    try {
      const skills_needed = skillsRaw.split(",").map(s => s.trim()).filter(Boolean);
      const res = await api.post("/opportunities", {
        title: title.trim(),
        description: description.trim(),
        category,
        skills_needed,
        location: location.trim(),
        collaboration_type: collab,
        commitment: commit,
      });
      navigate(`/opportunities/${res.data.opportunity_id}`);
    } catch (e) {
      setErr(e.response?.data?.detail || "Could not post.");
    } finally { setSubmitting(false); }
  };

  return (
    <div style={{ minHeight: "100vh", background: "#FFFBF5", fontFamily: "'DM Sans',sans-serif" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@400;500;600&display=swap');`}</style>
      <AppNavbar />
      <main style={{ maxWidth: 700, margin: "0 auto", padding: "36px 24px 80px" }}>
        <h1 style={{ fontFamily: "'Syne',sans-serif", fontSize: 28, fontWeight: 800, color: "#1C1917", marginBottom: 8 }}>Post an opportunity</h1>
        <p style={{ color: "#78716C", fontSize: 14, marginBottom: 28 }}>Share what you're building or looking for. The community can connect with you.</p>

        <form onSubmit={submit} style={{ background: "white", border: "1px solid #E7E5E4", borderRadius: 20, padding: 28, display: "flex", flexDirection: "column", gap: 18 }}>
          <Field label="Title" required>
            <input data-testid="post-title" value={title} onChange={e => setTitle(e.target.value)} placeholder="e.g. Need AI developer for agri-data MVP" style={inputStyle} />
          </Field>
          <Field label="Description" required>
            <textarea data-testid="post-description" rows={5} value={description} onChange={e => setDescription(e.target.value)} placeholder="What's the project? What stage? What kind of person are you looking for?" style={{ ...inputStyle, resize: "vertical" }} />
          </Field>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
            <Field label="Category" required>
              <select data-testid="post-category" value={category} onChange={e => setCategory(e.target.value)} style={inputStyle}>
                {CATEGORIES.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
              </select>
            </Field>
            <Field label="Location" required>
              <input data-testid="post-location" value={location} onChange={e => setLocation(e.target.value)} placeholder="e.g. Pune, Maharashtra" style={inputStyle} />
            </Field>
          </div>
          <Field label="Skills needed" hint="Comma separated (e.g. Python, ML, Agri-data)">
            <input data-testid="post-skills" value={skillsRaw} onChange={e => setSkillsRaw(e.target.value)} placeholder="Python, React, Marketing" style={inputStyle} />
          </Field>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
            <Field label="Collaboration type">
              <select data-testid="post-collab" value={collab} onChange={e => setCollab(e.target.value)} style={inputStyle}>
                <option value="cofounder">Co-founder</option>
                <option value="partner">Business partner</option>
                <option value="team-member">Team member</option>
                <option value="freelance">Freelance / Project</option>
                <option value="mentor">Mentor</option>
              </select>
            </Field>
            <Field label="Commitment">
              <select data-testid="post-commit" value={commit} onChange={e => setCommit(e.target.value)} style={inputStyle}>
                <option value="full-time">Full-time</option>
                <option value="part-time">Part-time</option>
                <option value="project-based">Project-based</option>
                <option value="casual">Casual</option>
              </select>
            </Field>
          </div>
          {err && <div data-testid="post-error" style={{ background: "#FEF2F2", color: "#B91C1C", padding: "10px 14px", borderRadius: 10, fontSize: 13 }}>{err}</div>}
          <button data-testid="post-submit" type="submit" disabled={submitting} style={{
            background: "#F97316", color: "white", border: "none", borderRadius: 50,
            padding: "14px 28px", fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 15,
            cursor: submitting ? "wait" : "pointer", boxShadow: "0 8px 24px rgba(249,115,22,0.35)",
          }}>
            {submitting ? "Posting…" : "Post Opportunity"}
          </button>
        </form>
      </main>
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
};
