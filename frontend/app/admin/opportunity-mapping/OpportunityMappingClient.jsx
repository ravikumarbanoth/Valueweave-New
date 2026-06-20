"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase-browser";

const TARGET_TYPES = [
  ["district", "District"],
  ["skill", "Skill"],
  ["research_article", "Research Article"],
  ["collaborator_type", "Collaborator Type"],
  ["resource", "Resource"],
];

export default function OpportunityMappingClient() {
  const supabase = createClient();
  const [opportunities, setOpportunities] = useState([]);
  const [relationships, setRelationships] = useState([]);
  const [form, setForm] = useState({ source_external_id: "", target_type: "skill", target_external_id: "", relationship_type: "opportunity_to_skill", notes: "" });
  const [message, setMessage] = useState("");

  useEffect(() => {
    supabase.from("opportunities").select("id,title,district,category").order("created_at", { ascending: false }).limit(100).then(({ data }) => setOpportunities(data || []));
    loadRelationships();
  }, []);

  async function loadRelationships() {
    const { data } = await supabase.from("kg_relationships").select("*").eq("source_type", "opportunity").order("created_at", { ascending: false }).limit(100);
    setRelationships(data || []);
  }

  async function save() {
    setMessage("");
    if (!form.source_external_id || !form.target_external_id) {
      setMessage("Choose an opportunity and enter a target slug/id.");
      return;
    }
    const { error } = await supabase.from("kg_relationships").insert({
      source_type: "opportunity",
      source_external_id: form.source_external_id,
      target_type: form.target_type,
      target_external_id: form.target_external_id,
      relationship_type: form.relationship_type,
      notes: form.notes || null,
    });
    if (error) setMessage(`Save failed: ${error.message}`);
    else {
      setMessage("Relationship saved.");
      setForm((prev) => ({ ...prev, target_external_id: "", notes: "" }));
      await loadRelationships();
    }
  }

  return (
    <div className="p-6 max-w-6xl space-y-6">
      <div>
        <span className="chip bg-purple-100 text-purple-700 border border-purple-200">RELATIONSHIP EDITOR</span>
        <h1 className="font-display font-extrabold text-3xl text-ink mt-2">Opportunity Mapping Engine</h1>
        <p className="text-stone-500 text-sm mt-1 max-w-2xl">Map opportunities to districts, skills, research articles, collaborator roles, and resources. This stores graph relationships without changing existing opportunity records.</p>
      </div>
      {message && <div className="rounded-xl px-4 py-3 bg-amber-50 border border-amber-200 text-sm text-amber-800">{message}</div>}
      <section className="card-base p-5 grid md:grid-cols-2 gap-4">
        <div>
          <label className="label-display">Opportunity</label>
          <select value={form.source_external_id} onChange={(e) => setForm({ ...form, source_external_id: e.target.value })} className="input-field">
            <option value="">Select opportunity</option>
            {opportunities.map((opp) => <option key={opp.id} value={opp.id}>{opp.title}</option>)}
          </select>
        </div>
        <div>
          <label className="label-display">Target Type</label>
          <select value={form.target_type} onChange={(e) => setForm({ ...form, target_type: e.target.value, relationship_type: `opportunity_to_${e.target.value}` })} className="input-field">
            {TARGET_TYPES.map(([id, label]) => <option key={id} value={id}>{label}</option>)}
          </select>
        </div>
        <div>
          <label className="label-display">Target Slug or ID</label>
          <input value={form.target_external_id} onChange={(e) => setForm({ ...form, target_external_id: e.target.value })} className="input-field" placeholder="e.g. dairy-farming or research slug" />
        </div>
        <div>
          <label className="label-display">Relationship Type</label>
          <input value={form.relationship_type} onChange={(e) => setForm({ ...form, relationship_type: e.target.value })} className="input-field" />
        </div>
        <div className="md:col-span-2">
          <label className="label-display">Notes</label>
          <textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} rows={3} className="input-field resize-y" />
        </div>
        <div className="md:col-span-2 flex justify-end">
          <button onClick={save} className="btn-primary">Save Relationship</button>
        </div>
      </section>
      <section className="card-base overflow-hidden">
        <div className="px-5 py-3 border-b border-stone-100 bg-stone-50 font-display font-bold text-sm">Recent Opportunity Links</div>
        {relationships.length === 0 ? <p className="p-5 text-sm text-muted">No relationships created yet.</p> : relationships.map((rel) => (
          <div key={rel.id} className="px-5 py-3 border-b border-stone-100 last:border-0 text-sm">
            <span className="font-mono text-xs text-stone-500">{rel.source_external_id}</span>
            <span className="mx-2 text-amber-600 font-bold">→</span>
            <span className="font-semibold text-ink">{rel.target_type}</span>
            <span className="ml-2 font-mono text-xs text-stone-500">{rel.target_external_id}</span>
          </div>
        ))}
      </section>
    </div>
  );
}
