"use client";

import { useMemo, useState } from "react";
import { createClient } from "@/lib/supabase-browser";
import { PLATFORM_SETTING_DEFINITIONS, coerceSettingValue } from "@/lib/settings-schema";

function serializeValue(def, value) {
  if (def.type === "boolean") return value === true || value === "true";
  if (def.type === "json") {
    if (Array.isArray(value) || (value && typeof value === "object")) return value;
    try { return JSON.parse(value || "[]"); } catch { return []; }
  }
  return value == null ? "" : String(value);
}

function toInputValue(def, value) {
  if (def.type === "json") return JSON.stringify(value ?? [], null, 2);
  return coerceSettingValue(def.type, value);
}

export default function DevopsSettingsClient({ initialSettings }) {
  const supabase = createClient();
  const [values, setValues] = useState(() => {
    const seeded = {};
    for (const def of PLATFORM_SETTING_DEFINITIONS) seeded[def.key] = toInputValue(def, initialSettings[def.key]);
    return seeded;
  });
  const [savingKey, setSavingKey] = useState("");
  const [message, setMessage] = useState("");

  const groups = useMemo(() => {
    return PLATFORM_SETTING_DEFINITIONS.reduce((acc, def) => {
      if (!acc[def.category]) acc[def.category] = [];
      acc[def.category].push(def);
      return acc;
    }, {});
  }, []);

  function update(key, value) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  async function save(def) {
    setSavingKey(def.key);
    setMessage("");
    const { error } = await supabase.from("platform_settings").upsert({
      key: def.key,
      value: serializeValue(def, values[def.key]),
      type: def.type,
      category: def.category,
    });
    setSavingKey("");
    setMessage(error ? `Could not save ${def.label}: ${error.message}` : `Saved ${def.label}`);
  }

  async function saveAll() {
    setSavingKey("all");
    setMessage("");
    const rows = PLATFORM_SETTING_DEFINITIONS.map((def) => ({
      key: def.key,
      value: serializeValue(def, values[def.key]),
      type: def.type,
      category: def.category,
    }));
    const { error } = await supabase.from("platform_settings").upsert(rows);
    setSavingKey("");
    setMessage(error ? `Could not save settings: ${error.message}` : "All platform settings saved. Changes may take up to 60 seconds to appear publicly.");
  }

  return (
    <div className="p-6 max-w-6xl space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <span className="chip bg-stone-100 text-stone-700 border border-stone-200">DEVOPS CONTROL CENTER</span>
          <h1 className="font-display font-extrabold text-3xl text-ink mt-2">Platform Configuration</h1>
          <p className="text-stone-500 text-sm mt-1 max-w-2xl">
            Non-technical controls for branding, homepage copy, navigation, footer, theme colors, SEO text, and emergency banners.
          </p>
        </div>
        <button onClick={saveAll} disabled={savingKey === "all"} className="btn-primary disabled:opacity-50">
          {savingKey === "all" ? "Saving…" : "Save All"}
        </button>
      </div>

      {message && (
        <div className={`rounded-xl px-4 py-3 text-sm border ${message.startsWith("Could") ? "bg-red-50 text-red-700 border-red-200" : "bg-teal-50 text-teal-700 border-teal-200"}`}>
          {message}
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-5">
        {Object.entries(groups).map(([category, defs]) => (
          <section key={category} className="card-base p-5">
            <h2 className="font-display font-bold text-lg text-ink mb-4">{category}</h2>
            <div className="space-y-4">
              {defs.map((def) => (
                <div key={def.key} className="border-b border-stone-100 pb-4 last:border-0 last:pb-0">
                  <div className="flex items-center justify-between gap-3 mb-2">
                    <label className="label-display !mb-0">{def.label}</label>
                    <button
                      onClick={() => save(def)}
                      disabled={savingKey === def.key || savingKey === "all"}
                      className="btn-ghost !min-h-0 !px-3 !py-1.5 text-xs border border-stone-200 disabled:opacity-50"
                    >
                      {savingKey === def.key ? "Saving…" : "Save"}
                    </button>
                  </div>

                  {def.type === "boolean" ? (
                    <label className="inline-flex items-center gap-2 text-sm font-semibold text-stone-600">
                      <input
                        type="checkbox"
                        checked={values[def.key] === true || values[def.key] === "true"}
                        onChange={(e) => update(def.key, e.target.checked)}
                        className="w-4 h-4 accent-amber-500"
                      />
                      Enabled
                    </label>
                  ) : def.type === "textarea" || def.type === "json" ? (
                    <textarea
                      value={values[def.key] || ""}
                      onChange={(e) => update(def.key, e.target.value)}
                      rows={def.type === "json" ? 7 : 3}
                      className="input-field font-mono !text-sm resize-y"
                    />
                  ) : (
                    <input
                      type={def.type === "color" ? "color" : def.type === "email" ? "email" : "text"}
                      value={values[def.key] || ""}
                      onChange={(e) => update(def.key, e.target.value)}
                      className={def.type === "color" ? "w-20 h-11 rounded-xl border-2 border-stone-200 bg-white p-1" : "input-field"}
                    />
                  )}
                  <p className="text-[11px] text-stone-400 mt-1 font-mono">{def.key}</p>
                </div>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
