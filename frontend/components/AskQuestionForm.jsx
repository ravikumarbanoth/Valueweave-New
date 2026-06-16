"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase-browser";
import { MessageSquare, ChevronDown, ChevronUp, Send, AlertCircle } from "lucide-react";

export default function AskQuestionForm() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ title: "", body: "", district: "", sector: "" });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [done, setDone] = useState(false);

  async function submit() {
    setError(null);
    if (!form.title.trim()) { setError("Question title is required."); return; }
    setSaving(true);
    const sb = createClient();
    const { data: { user } } = await sb.auth.getUser();
    if (!user) { setError("Sign in to ask a question."); setSaving(false); return; }

    const { error: err } = await sb.from("questions").insert({
      user_id:  user.id,
      title:    form.title.trim(),
      body:     form.body.trim() || null,
      district: form.district.trim() || null,
      sector:   form.sector.trim() || null,
    });

    setSaving(false);
    if (err) { setError("Failed to post. Please try again."); return; }
    setDone(true);
    setForm({ title: "", body: "", district: "", sector: "" });
    setOpen(false);
    router.refresh();
  }

  if (done) {
    return (
      <div className="card-base p-4 flex items-center gap-3 border border-green-200 bg-green-50">
        <MessageSquare size={16} className="text-green-600 shrink-0" />
        <p className="text-sm font-semibold text-green-700">Your question was posted!</p>
        <button onClick={() => setDone(false)} className="ml-auto text-[12px] text-green-600 underline">Ask another</button>
      </div>
    );
  }

  return (
    <div className="card-base overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between p-4 hover:bg-stone-50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <MessageSquare size={16} className="text-teal-500" />
          <span className="font-display font-semibold text-sm text-ink">Ask the community</span>
        </div>
        {open ? <ChevronUp size={14} className="text-stone-400" /> : <ChevronDown size={14} className="text-stone-400" />}
      </button>

      {open && (
        <div className="px-4 pb-4 border-t border-stone-100 pt-4 space-y-3">
          {error && (
            <div className="flex items-center gap-2 p-3 bg-rose-50 border border-rose-200 rounded-xl text-[12px] text-rose-700">
              <AlertCircle size={13} /> {error}
            </div>
          )}
          <div>
            <label className="label-sm">Question *</label>
            <input
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="e.g. What funding schemes are available for food tech startups in Warangal?"
              className="input-base w-full"
            />
          </div>
          <div>
            <label className="label-sm">More detail (optional)</label>
            <textarea
              value={form.body}
              onChange={(e) => setForm({ ...form, body: e.target.value })}
              rows={2}
              placeholder="Add context, constraints, or what you've already tried…"
              className="input-base w-full resize-none"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label-sm">District (optional)</label>
              <input
                value={form.district}
                onChange={(e) => setForm({ ...form, district: e.target.value })}
                placeholder="e.g. Hyderabad"
                className="input-base w-full"
              />
            </div>
            <div>
              <label className="label-sm">Sector (optional)</label>
              <input
                value={form.sector}
                onChange={(e) => setForm({ ...form, sector: e.target.value })}
                placeholder="e.g. AgriTech"
                className="input-base w-full"
              />
            </div>
          </div>
          <div className="flex justify-end pt-1">
            <button
              onClick={submit}
              disabled={saving}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-teal-500 text-white text-[13px] font-semibold hover:bg-teal-600 disabled:opacity-50"
            >
              <Send size={13} />
              {saving ? "Posting…" : "Post Question"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
