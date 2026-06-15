"use client";
import { useState } from "react";
import { createClient } from "@/lib/supabase-browser";
import { DISTRICTS } from "@/lib/districts-data";
import {
  SECTOR_TEMPLATES,
  INVESTMENT_RANGES,
  FOUNDER_ROLES,
  generateOpportunityRecord,
} from "@/lib/opportunity-templates";
import { Zap, CheckCircle, Loader2, Eye, Send, Trash2 } from "lucide-react";

const SECTORS = Object.entries(SECTOR_TEMPLATES).map(([key, val]) => ({ key, label: val.label }));
const STATES = ["Telangana", "Andhra Pradesh"];

export default function GeneratorClient() {
  const [form, setForm] = useState({
    state: "Telangana",
    districts: [],
    sector: "healthcare",
    count: 5,
    investmentRange: "₹5L – ₹10L",
    founderRole: "",
  });
  const [previews, setPreviews] = useState([]);
  const [publishing, setPublishing] = useState(false);
  const [published, setPublished] = useState(0);
  const [error, setError] = useState("");

  const filteredDistricts = DISTRICTS.filter((d) => d.state === form.state);

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const toggleDistrict = (name) => {
    set("districts", form.districts.includes(name)
      ? form.districts.filter((d) => d !== name)
      : [...form.districts, name]);
  };

  const handleGenerate = () => {
    if (form.districts.length === 0) {
      setError("Select at least one district.");
      return;
    }
    setError("");
    const records = [];
    const template = SECTOR_TEMPLATES[form.sector];
    const count = Math.min(parseInt(form.count) || 5, 20);
    const perDistrict = Math.max(1, Math.ceil(count / form.districts.length));

    form.districts.forEach((district) => {
      for (let i = 0; i < perDistrict && records.length < count; i++) {
        const bt = template.businessTypes[i % template.businessTypes.length];
        const rec = generateOpportunityRecord({
          sector: form.sector,
          businessType: bt,
          district,
          state: form.state,
          investmentRange: form.investmentRange,
          founderRole: form.founderRole || template.founderRole,
          index: i,
        });
        if (rec) records.push({ ...rec, _preview_id: `${district}-${i}` });
      }
    });

    setPreviews(records.slice(0, count));
    setPublished(0);
  };

  const removePreview = (id) => setPreviews((p) => p.filter((r) => r._preview_id !== id));

  const handlePublish = async () => {
    if (previews.length === 0) return;
    setPublishing(true);
    setError("");
    let count = 0;
    const sb = createClient();

    for (const rec of previews) {
      const { _preview_id, _meta, ...row } = rec;
      const { error: err } = await sb.from("opportunities").insert(row);
      if (!err) count++;
      else console.error("Insert error:", err);
    }

    setPublished(count);
    setPublishing(false);
    if (count > 0) setPreviews([]);
  };

  return (
    <div className="space-y-8">

      {/* Form */}
      <div className="card-base p-6 space-y-6">
        <h2 className="font-display font-bold text-ink text-sm flex items-center gap-2">
          <Zap size={15} className="text-amber-500" /> Configure Generation
        </h2>

        {/* State */}
        <div>
          <label className="label-display">State</label>
          <div className="flex gap-2">
            {STATES.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => { set("state", s); set("districts", []); }}
                className={`px-4 py-2 rounded-full text-sm font-semibold transition-colors ${
                  form.state === s ? "bg-amber-500 text-white" : "btn-secondary"
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        {/* Districts */}
        <div>
          <label className="label-display">
            Districts ({form.districts.length} selected)
            <button
              type="button"
              className="ml-2 text-[11px] text-amber-600 font-semibold hover:underline"
              onClick={() => set("districts", filteredDistricts.map((d) => d.name))}
            >
              Select All
            </button>
            {form.districts.length > 0 && (
              <button
                type="button"
                className="ml-2 text-[11px] text-stone-400 hover:underline"
                onClick={() => set("districts", [])}
              >
                Clear
              </button>
            )}
          </label>
          <div className="flex flex-wrap gap-2 mt-2">
            {filteredDistricts.map((d) => (
              <button
                key={d.name}
                type="button"
                onClick={() => toggleDistrict(d.name)}
                className={`px-3 py-1.5 rounded-full text-[12px] font-semibold transition-colors border ${
                  form.districts.includes(d.name)
                    ? "bg-teal-500 text-white border-teal-500"
                    : "bg-white text-stone-500 border-stone-200 hover:border-teal-400"
                }`}
              >
                {d.name}
              </button>
            ))}
          </div>
        </div>

        {/* Sector */}
        <div>
          <label className="label-display">Sector</label>
          <div className="flex flex-wrap gap-2 mt-1">
            {SECTORS.map(({ key, label }) => (
              <button
                key={key}
                type="button"
                onClick={() => set("sector", key)}
                className={`px-3 py-1.5 rounded-full text-[12px] font-semibold transition-colors border ${
                  form.sector === key
                    ? "bg-amber-500 text-white border-amber-500"
                    : "bg-white text-stone-500 border-stone-200 hover:border-amber-400"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Count + Investment Range + Founder Role */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="label-display">Count (max 20)</label>
            <input
              type="number"
              min={1}
              max={20}
              value={form.count}
              onChange={(e) => set("count", e.target.value)}
              className="input-field"
            />
          </div>
          <div>
            <label className="label-display">Investment Range</label>
            <select
              value={form.investmentRange}
              onChange={(e) => set("investmentRange", e.target.value)}
              className="input-field"
            >
              {INVESTMENT_RANGES.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label-display">Founder Role (optional)</label>
            <select
              value={form.founderRole}
              onChange={(e) => set("founderRole", e.target.value)}
              className="input-field"
            >
              <option value="">Auto (from sector)</option>
              {FOUNDER_ROLES.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="button"
          onClick={handleGenerate}
          className="btn-primary gap-2"
        >
          <Eye size={16} /> Preview Opportunities
        </button>
      </div>

      {/* Published banner */}
      {published > 0 && (
        <div className="card-base p-4 bg-green-50 border-green-200 flex items-center gap-3">
          <CheckCircle size={18} className="text-green-600" />
          <p className="text-sm text-green-700 font-semibold">
            Successfully published {published} opportunit{published !== 1 ? "ies" : "y"} to the database.
          </p>
        </div>
      )}

      {/* Preview */}
      {previews.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-display font-bold text-ink text-sm">
              Preview ({previews.length} opportunities)
            </h2>
            <button
              type="button"
              onClick={handlePublish}
              disabled={publishing}
              className="btn-primary"
            >
              {publishing ? (
                <><Loader2 size={15} className="animate-spin" /> Publishing…</>
              ) : (
                <><Send size={15} /> Publish All</>
              )}
            </button>
          </div>

          {previews.map((rec) => (
            <div key={rec._preview_id} className="card-base p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-display font-bold text-ink text-sm">{rec.title}</h3>
                  </div>
                  <div className="flex flex-wrap gap-1.5 mb-3">
                    <span className="chip bg-amber-50 text-amber-700 border border-amber-200 text-[10px]">{rec.category}</span>
                    <span className="chip bg-stone-100 text-stone-500 text-[10px]">{rec.district}</span>
                    <span className="chip bg-stone-100 text-stone-500 text-[10px]">{rec.investment_range}</span>
                    <span className="chip bg-teal-50 text-teal-700 border border-teal-200 text-[10px]">{rec.founder_role}</span>
                  </div>
                  <p className="text-[12px] text-stone-500 line-clamp-3">{rec.description}</p>
                  <div className="mt-3">
                    <p className="text-[11px] text-stone-400 font-semibold uppercase tracking-wide mb-1">Skills Needed</p>
                    <div className="flex flex-wrap gap-1">
                      {rec.skills_needed?.map((s) => (
                        <span key={s} className="chip bg-stone-100 text-stone-500 text-[10px]">{s}</span>
                      ))}
                    </div>
                  </div>
                  {rec._meta?.collaboratorRoles && (
                    <div className="mt-2">
                      <p className="text-[11px] text-stone-400 font-semibold uppercase tracking-wide mb-1">Collaborator Roles</p>
                      <div className="flex flex-wrap gap-1">
                        {rec._meta.collaboratorRoles.map((r) => (
                          <span key={r} className="chip bg-blue-50 text-blue-700 text-[10px]">{r}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => removePreview(rec._preview_id)}
                  className="text-stone-300 hover:text-red-400 transition-colors shrink-0 mt-0.5"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
