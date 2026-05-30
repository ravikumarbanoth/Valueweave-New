"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase-browser";

const SKILL_SUGGESTIONS = [
  "Agriculture", "Dairy Farming", "Poultry", "Food Processing", "Manufacturing", "Retail Operations",
  "Logistics", "Marketing", "Sales", "Accounting", "Packaging", "Solar Installation", "MSME Consulting",
  "Local Services", "Field Marketing", "Customer Handling", "Inventory Management", "Procurement", "Vendor Management",
  "Team Management", "Operations Coordination", "Business Development", "Organic Farming", "Soil Testing",
  "Irrigation Systems", "Agri Equipment Handling", "Seed Management", "Crop Advisory", "Electrical Work", "Plumbing",
  "Welding", "Carpentry", "CCTV Installation", "AC Repair", "Bike Repair", "Mobile Repair", "Tailoring",
  "Beautician Services", "Housekeeping Services", "Machine Operations", "Textile Production", "Furniture Manufacturing",
  "Printing Operations", "Photography", "Graphic Design", "Video Editing", "Event Management", "GST Filing",
  "Loan Documentation", "Financial Planning", "Legal Documentation", "Web Development", "AI", "Digital Marketing", "UI/UX",
];

const INTEREST_SUGGESTIONS = [
  "Small Business", "Local Commerce", "Agriculture", "Dairy", "Poultry", "Food Processing", "Manufacturing",
  "Retail", "Logistics", "Solar Energy", "MSME Growth", "Local Services", "Women-Led Business", "Student Business",
  "Rural Innovation", "Franchise", "Skill Development", "Community Building", "Entrepreneurship", "Self Employment",
  "Youth Collaboration", "Regional Startups", "Digital Business", "Financial Literacy", "AgriTech", "Sustainability",
  "Creator Economy", "Hardware", "EdTech", "FinTech",
];

const LOOKING_FOR_OPTIONS = [
  ["find-collaborators","Find Collaborators"],
  ["start-business","Start a Business"],
  ["local-opportunities","Local Opportunities"],
  ["find-cofounder","Find a Co-founder"],
  ["join-startup","Join a Startup Team"],
  ["offer-skills","Offer My Skills"],
  ["explore","Just Exploring"],
  ["hire-collaborators","Hire Collaborators"],
];

export default function OnboardingPage() {
  const supabase = createClient();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState("");
  const [form, setForm] = useState({
    name: "",
    city: "",
    bio: "",
    skills: [],
    interests: [],
    looking_for: "find-collaborators",
  });
  const [skillInput, setSkillInput] = useState("");
  const [interestInput, setInterestInput] = useState("");

  useEffect(() => {
    (async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) { router.replace("/"); return; }
      const { data: profile } = await supabase.from("profiles").select("*").eq("id", user.id).single();
      const localIntent = typeof window !== "undefined" ? localStorage.getItem("vw_intent") : null;
      if (profile) {
        setForm({
          name: profile.name || user.user_metadata?.full_name || "",
          city: profile.city || "",
          bio: profile.bio || "",
          skills: profile.skills || [],
          interests: profile.interests || [],
          looking_for: profile.looking_for || localIntent || "find-collaborators",
        });
      }
      setLoading(false);
    })();
  }, [supabase, router]);

  const addToList = (key, value, clearInput) => {
    const v = value.trim();
    if (!v || form[key].includes(v)) return;
    setForm({ ...form, [key]: [...form[key], v] });
    clearInput("");
  };
  const removeFromList = (key, v) => setForm({ ...form, [key]: form[key].filter(x => x !== v) });

  const submit = async (e) => {
    e.preventDefault();
    setErr("");
    if (!form.name.trim() || !form.city.trim() || form.skills.length === 0) {
      setErr("Name, city, and at least one skill are required.");
      return;
    }
    setSaving(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      const { error } = await supabase.from("profiles").update({
        name: form.name.trim(),
        city: form.city.trim(),
        bio: form.bio.trim(),
        skills: form.skills,
        interests: form.interests,
        looking_for: form.looking_for,
        profile_complete: true,
      }).eq("id", user.id);
      if (error) throw error;
      localStorage.removeItem("vw_intent");
      router.replace("/dashboard");
      router.refresh();
    } catch (e) {
      setErr(e.message || "Could not save profile.");
    } finally { setSaving(false); }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-cream"><p data-testid="onboarding-loading">Loading…</p></div>;

  return (
    <div className="min-h-screen bg-cream py-12 px-6">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <span className="chip bg-teal-100 text-teal-600 mb-3">STEP 2 OF 3</span>
          <h1 className="font-display font-extrabold text-3xl md:text-4xl tracking-tight mb-2">
            Tell us about <span className="text-teal-500">you</span>
          </h1>
          <p className="text-muted text-sm">A lightweight profile to help you find the right people to build with.</p>
        </div>

        <form onSubmit={submit} className="card-base p-6 md:p-8 flex flex-col gap-5">
          <Field label="Your name" required>
            <input data-testid="ob-name" className="input-field" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Arjun Patil" />
          </Field>

          <Field label="City" required>
            <input data-testid="ob-city" className="input-field" value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} placeholder="e.g. Hyderabad, Telangana" />
          </Field>

          <Field label="Skills" required hint="What do you do best? Add 3–6 skills.">
            <ChipInput
              testid="skill"
              value={skillInput}
              onChange={setSkillInput}
              onAdd={(v) => addToList("skills", v, setSkillInput)}
              suggestions={SKILL_SUGGESTIONS.filter(s => !form.skills.includes(s)).slice(0, 18)}
            />
            <Chips items={form.skills} onRemove={(v) => removeFromList("skills", v)} testidPrefix="skill-chip" tone="amber" />
          </Field>

          <Field label="Interests" hint="Domains you're excited about.">
            <ChipInput
              testid="interest"
              value={interestInput}
              onChange={setInterestInput}
              onAdd={(v) => addToList("interests", v, setInterestInput)}
              suggestions={INTEREST_SUGGESTIONS.filter(s => !form.interests.includes(s)).slice(0, 16)}
            />
            <Chips items={form.interests} onRemove={(v) => removeFromList("interests", v)} testidPrefix="interest-chip" tone="teal" />
          </Field>

          <Field label="I'm here to…">
            <select data-testid="ob-looking-for" className="input-field" value={form.looking_for} onChange={(e) => setForm({ ...form, looking_for: e.target.value })}>
              {LOOKING_FOR_OPTIONS.map(([id, l]) => <option key={id} value={id}>{l}</option>)}
            </select>
          </Field>

          <Field label="Short bio" hint="One or two sentences about what you build.">
            <textarea data-testid="ob-bio" rows={3} className="input-field resize-y" value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} placeholder="e.g. Electronics diploma holder building EV charging stations in tier-2 cities." />
          </Field>

          {err && <div data-testid="ob-error" className="bg-rose-50 text-rose-700 text-sm rounded-lg px-4 py-2.5">{err}</div>}

          <button data-testid="ob-submit" type="submit" disabled={saving} className="btn-primary !py-3.5 disabled:opacity-50">
            {saving ? "Saving…" : "Continue to Dashboard →"}
          </button>
        </form>
      </div>
    </div>
  );
}

function Field({ label, hint, required, children }) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="font-display font-bold text-xs text-ink">
        {label}{required && <span className="text-amber-500"> *</span>}
      </span>
      {children}
      {hint && <span className="text-xs text-stone-400">{hint}</span>}
    </label>
  );
}

function ChipInput({ value, onChange, onAdd, suggestions, testid }) {
  return (
    <>
      <div className="flex gap-2">
        <input
          data-testid={`${testid}-input`}
          className="input-field"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); onAdd(value); } }}
          placeholder="Type and press Enter"
        />
        <button type="button" data-testid={`${testid}-add`} onClick={() => onAdd(value)} className="btn-teal !px-5 !py-2.5 shrink-0">Add</button>
      </div>
      {suggestions.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-2">
          {suggestions.map((s) => (
            <button type="button" key={s} data-testid={`${testid}-suggest-${s}`} onClick={() => onAdd(s)} className="chip bg-stone-100 text-stone-600 hover:bg-stone-200 cursor-pointer">+ {s}</button>
          ))}
        </div>
      )}
    </>
  );
}

function Chips({ items, onRemove, testidPrefix, tone }) {
  if (!items.length) return null;
  const cls = tone === "teal" ? "bg-teal-100 text-teal-700" : "bg-amber-200 text-amber-700";
  return (
    <div className="flex flex-wrap gap-1.5 mt-2.5">
      {items.map((s) => (
        <span key={s} data-testid={`${testidPrefix}-${s}`} className={`chip ${cls}`}>
          {s}
          <button type="button" onClick={() => onRemove(s)} className="font-bold ml-1 hover:text-amber-900">×</button>
        </span>
      ))}
    </div>
  );
}
