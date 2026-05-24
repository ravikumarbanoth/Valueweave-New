"use client";
import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { createClient } from "@/lib/supabase-browser";
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

export default function OpportunityFormClient() {
  const supabase = createClient();
  const router = useRouter();
  const params = useSearchParams();
  const [profile, setProfile] = useState(null);
  const [form, setForm] = useState({
    title: params.get("title") || "",
    description: params.get("description") || "",
    category: params.get("category") || "ai-tech",
    location: params.get("location") || "",
    skills_raw: params.get("skills") || "",
    collaboration_type: params.get("collab") || "cofounder",
    commitment: params.get("commit") || "part-time",
  });
  const [submitting, setSubmitting] = useState(false);
  const [err, setErr] = useState("");
  const isPrefilled = !!(params.get("title") || params.get("skills"));

  useEffect(() => {
    (async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;
      const { data } = await supabase.from("profiles").select("*").eq("id", user.id).single();
      setProfile(data);
    })();
  }, [supabase]);

  const submit = async (e) => {
    e.preventDefault();
    setErr("");
    if (!form.title.trim() || !form.description.trim() || !form.location.trim()) {
      setErr("Title, description, and location are required.");
      return;
    }
    setSubmitting(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      const skills_needed = form.skills_raw.split(",").map(s => s.trim()).filter(Boolean);
      const { data, error } = await supabase
        .from("opportunities")
        .insert({
          owner_id: user.id,
          title: form.title.trim(),
          description: form.description.trim(),
          category: form.category,
          skills_needed,
          location: form.location.trim(),
          collaboration_type: form.collaboration_type,
          commitment: form.commitment,
        })
        .select()
        .single();
      if (error) throw error;
      router.push(`/opportunities/${data.id}`);
    } catch (e) {
      setErr(e.message || "Could not post.");
    } finally { setSubmitting(false); }
  };

  return (
    <div className="min-h-screen bg-cream pb-20 md:pb-0">
      <AppNavbar initialProfile={profile} />
      <main className="max-w-2xl mx-auto px-6 py-8">
        <h1 className="font-display font-extrabold text-3xl tracking-tight mb-1">Post an opportunity</h1>
        <p className="text-muted text-sm mb-6">Share what you're building or looking for. The community can connect with you.</p>

        {isPrefilled && (
          <div data-testid="post-prefilled-banner" className="mb-5 bg-teal-50 border border-teal-200 text-teal-800 rounded-xl px-4 py-3 text-sm font-display font-semibold">
            ✨ Pre-filled from the Idea Library. Edit anything before posting.
          </div>
        )}

        <form onSubmit={submit} className="card-base p-6 flex flex-col gap-4">
          <Field label="Title" required>
            <input data-testid="post-title" className="input-field" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="e.g. Need AI developer for agri-data MVP" />
          </Field>
          <Field label="Description" required>
            <textarea data-testid="post-description" rows={5} className="input-field resize-y" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="What's the project? What stage? What kind of person are you looking for?" />
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Category" required>
              <select data-testid="post-category" className="input-field" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
                {CATEGORIES.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
              </select>
            </Field>
            <Field label="Location" required>
              <input data-testid="post-location" className="input-field" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} placeholder="e.g. Hyderabad, Telangana" />
            </Field>
          </div>
          <Field label="Skills needed" hint="Comma separated">
            <input data-testid="post-skills" className="input-field" value={form.skills_raw} onChange={(e) => setForm({ ...form, skills_raw: e.target.value })} placeholder="Python, React, Marketing" />
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Collaboration type">
              <select data-testid="post-collab" className="input-field" value={form.collaboration_type} onChange={(e) => setForm({ ...form, collaboration_type: e.target.value })}>
                <option value="cofounder">Co-founder</option>
                <option value="partner">Business partner</option>
                <option value="team-member">Team member</option>
                <option value="freelance">Freelance / Project</option>
                <option value="mentor">Mentor</option>
              </select>
            </Field>
            <Field label="Commitment">
              <select data-testid="post-commit" className="input-field" value={form.commitment} onChange={(e) => setForm({ ...form, commitment: e.target.value })}>
                <option value="full-time">Full-time</option>
                <option value="part-time">Part-time</option>
                <option value="project-based">Project-based</option>
                <option value="casual">Casual</option>
              </select>
            </Field>
          </div>
          {err && <div data-testid="post-error" className="bg-rose-50 text-rose-700 text-sm rounded-lg px-4 py-2.5">{err}</div>}
          <button data-testid="post-submit" type="submit" disabled={submitting} className="btn-primary !py-3.5 disabled:opacity-50">
            {submitting ? "Posting…" : "Post Opportunity"}
          </button>
        </form>
      </main>
    </div>
  );
}

function Field({ label, hint, required, children }) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="font-display font-bold text-xs text-ink">{label}{required && <span className="text-amber-500"> *</span>}</span>
      {children}
      {hint && <span className="text-xs text-stone-400">{hint}</span>}
    </label>
  );
}
