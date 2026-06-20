"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { createClient } from "@/lib/supabase-browser";
import { slugify } from "@/lib/knowledge-graph";

function parseArray(value) {
  return String(value || "").split(",").map((v) => v.trim()).filter(Boolean);
}

function inputValue(record, field) {
  const value = record[field.name];
  if (field.type === "array") return Array.isArray(value) ? value.join(", ") : "";
  if (field.type === "json") return JSON.stringify(value ?? (field.name === "faq_json" ? [] : {}), null, 2);
  return value ?? "";
}

export default function KnowledgeEntityManager({ table, title, description, titleField = "name", fields = [] }) {
  const supabase = createClient();
  const [records, setRecords] = useState([]);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState({ status: "draft" });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  const allFields = useMemo(() => [
    { name: titleField, label: titleField === "title" ? "Title" : "Name", type: "text", required: true },
    { name: "slug", label: "Slug", type: "text", required: true },
    ...fields,
    { name: "summary", label: "Summary", type: "textarea" },
    { name: "ai_summary", label: "AI Summary", type: "textarea" },
    { name: "rich_text", label: "Rich Text / Notes", type: "textarea" },
    { name: "meta_title", label: "Meta Title", type: "text" },
    { name: "meta_description", label: "Meta Description", type: "textarea" },
    { name: "faq_json", label: "FAQ JSON", type: "json" },
    { name: "structured_data", label: "Structured Data JSON", type: "json" },
    { name: "status", label: "Status", type: "status" },
  ], [fields, titleField]);

  const load = useCallback(async () => {
    setLoading(true);
    const { data } = await supabase.from(table).select("*").order("updated_at", { ascending: false }).limit(200);
    setRecords(data || []);
    setLoading(false);
  }, [supabase, table]);

  useEffect(() => { load(); }, [load]);

  function startNew() {
    setSelected(null);
    setForm({ status: "draft", faq_json: "[]", structured_data: "{}" });
    setMessage("");
  }

  function edit(record) {
    setSelected(record.id);
    const next = {};
    for (const field of allFields) next[field.name] = inputValue(record, field);
    setForm(next);
    setMessage("");
  }

  function update(name, value) {
    setForm((prev) => {
      const next = { ...prev, [name]: value };
      if (name === titleField && !prev.slug) next.slug = slugify(value);
      if (name === "slug") next.slug = slugify(value);
      return next;
    });
  }

  function toRow() {
    const row = {};
    for (const field of allFields) {
      const raw = form[field.name];
      if (field.type === "array") row[field.name] = parseArray(raw);
      else if (field.type === "number") row[field.name] = raw === "" || raw == null ? null : Number(raw);
      else if (field.type === "json") {
        try { row[field.name] = raw ? JSON.parse(raw) : (field.name === "faq_json" ? [] : {}); }
        catch { row[field.name] = field.name === "faq_json" ? [] : {}; }
      } else row[field.name] = raw === "" ? null : raw;
    }
    if (row.status === "published") {
      const current = records.find((record) => record.id === selected);
      if (!selected || !current?.published_at) row.published_at = new Date().toISOString();
    }
    return row;
  }

  async function save() {
    setSaving(true);
    setMessage("");
    const row = toRow();
    if (!row[titleField] || !row.slug) {
      setMessage("Name/title and slug are required.");
      setSaving(false);
      return;
    }
    const result = selected
      ? await supabase.from(table).update(row).eq("id", selected).select("id").single()
      : await supabase.from(table).insert(row).select("id").single();
    setSaving(false);
    if (result.error) setMessage(`Save failed: ${result.error.message}`);
    else {
      setMessage("Saved successfully.");
      await load();
      if (!selected) setSelected(result.data.id);
    }
  }

  async function remove(record) {
    if (!window.confirm(`Delete ${record[titleField]}?`)) return;
    await supabase.from(table).delete().eq("id", record.id);
    if (selected === record.id) startNew();
    await load();
  }

  return (
    <div className="p-6 max-w-6xl space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <span className="chip bg-amber-100 text-amber-700 border border-amber-200">KNOWLEDGE GRAPH CMS</span>
          <h1 className="font-display font-extrabold text-3xl text-ink mt-2">{title}</h1>
          <p className="text-stone-500 text-sm mt-1 max-w-2xl">{description}</p>
        </div>
        <button onClick={startNew} className="btn-primary">+ New</button>
      </div>

      {message && <div className="rounded-xl px-4 py-3 text-sm bg-amber-50 border border-amber-200 text-amber-800">{message}</div>}

      <div className="grid lg:grid-cols-[320px_1fr] gap-5">
        <section className="card-base overflow-hidden">
          <div className="px-4 py-3 border-b border-stone-100 bg-stone-50 font-display font-bold text-sm">Existing Entries</div>
          {loading ? <div className="p-4 text-sm text-muted">Loading…</div> : records.length === 0 ? (
            <div className="p-6 text-sm text-muted">No entries yet. Add the first one from the editor.</div>
          ) : records.map((record) => (
            <div key={record.id} className="px-4 py-3 border-b border-stone-100 last:border-0 flex items-center gap-2">
              <button onClick={() => edit(record)} className="flex-1 text-left min-w-0">
                <p className="font-display font-bold text-sm text-ink truncate">{record[titleField]}</p>
                <p className="text-xs text-muted">/{record.slug} · {record.status}</p>
              </button>
              <button onClick={() => remove(record)} className="text-xs text-red-600 font-semibold px-2 py-1 rounded-lg hover:bg-red-50">Delete</button>
            </div>
          ))}
        </section>

        <section className="card-base p-5 space-y-4">
          {allFields.map((field) => (
            <div key={field.name}>
              <label className="label-display">{field.label}{field.required && <span className="text-amber-500"> *</span>}</label>
              {field.type === "textarea" || field.type === "json" ? (
                <textarea rows={field.type === "json" ? 6 : 3} value={form[field.name] ?? ""} onChange={(e) => update(field.name, e.target.value)} className="input-field font-mono !text-sm resize-y" />
              ) : field.type === "status" ? (
                <select value={form[field.name] || "draft"} onChange={(e) => update(field.name, e.target.value)} className="input-field">
                  <option value="draft">Draft</option>
                  <option value="published">Published</option>
                </select>
              ) : (
                <input type={field.type === "number" ? "number" : "text"} value={form[field.name] ?? ""} onChange={(e) => update(field.name, e.target.value)} className="input-field" />
              )}
              {field.help && <p className="text-xs text-stone-400 mt-1">{field.help}</p>}
            </div>
          ))}
          <div className="sticky bottom-0 bg-white/90 backdrop-blur border-t border-stone-100 pt-4 flex justify-end">
            <button onClick={save} disabled={saving} className="btn-primary disabled:opacity-50">{saving ? "Saving…" : "Save Entry"}</button>
          </div>
        </section>
      </div>
    </div>
  );
}
