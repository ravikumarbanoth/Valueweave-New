"use client";
// Reusable "Request Content" button/widget.
// Drops into idea, research, district, and opportunity pages.
// Submits to the user_requests table.

import { useState } from "react";
import { PlusCircle, X, CheckCircle, Send } from "lucide-react";
import { createClient } from "@/lib/supabase-browser";

// Valid types per the DB check constraint
const TYPE_LABELS = {
  research:     "Research Article",
  idea:         "Business Idea",
  district:     "District Report",
  opportunity:  "Opportunity Listing",
  general:      "General",
};

export default function RequestContentWidget({
  defaultType = "research",
  district = null,
  sector = null,
  prefillTitle = "",
  buttonLabel = "Request Content",
  compact = false,
}) {
  const [open, setOpen]       = useState(false);
  const [title, setTitle]     = useState(prefillTitle);
  const [type, setType]       = useState(defaultType);
  const [desc, setDesc]       = useState("");
  const [status, setStatus]   = useState("idle"); // idle | submitting | success | error

  async function handleSubmit(e) {
    e.preventDefault();
    if (!title.trim()) return;
    setStatus("submitting");
    try {
      const sb = createClient();
      const { error } = await sb.from("user_requests").insert({
        type,
        title: title.trim(),
        description: desc.trim() || null,
        district: district || null,
        sector: sector || null,
        status: "pending",
      });
      if (error) throw error;
      setStatus("success");
      setTimeout(() => {
        setOpen(false);
        setStatus("idle");
        setTitle(prefillTitle);
        setDesc("");
      }, 2200);
    } catch {
      setStatus("error");
    }
  }

  return (
    <>
      {compact ? (
        <button
          onClick={() => setOpen(true)}
          className="inline-flex items-center gap-1.5 text-[12px] font-semibold text-amber-600 hover:text-amber-700 transition-colors"
        >
          <PlusCircle size={13} />
          {buttonLabel}
        </button>
      ) : (
        <button
          onClick={() => setOpen(true)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-amber-200 bg-amber-50 text-amber-700 text-[13px] font-semibold hover:bg-amber-100 transition-colors"
        >
          <PlusCircle size={14} />
          {buttonLabel}
        </button>
      )}

      {open && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-black/30 backdrop-blur-sm">
          <div className="w-full max-w-sm bg-white rounded-2xl shadow-2xl overflow-hidden">

            <div className="flex items-center justify-between px-5 py-4 border-b border-stone-100">
              <div>
                <p className="font-display font-bold text-ink text-[15px]">Request Content</p>
                <p className="text-[11px] text-stone-400 mt-0.5">
                  {district ? `For ${district}` : "We'll prioritise high-demand topics"}
                </p>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="p-1.5 rounded-full hover:bg-stone-100 transition-colors text-stone-400"
              >
                <X size={16} />
              </button>
            </div>

            {status === "success" ? (
              <div className="flex flex-col items-center justify-center gap-3 py-10 px-6 text-center">
                <CheckCircle size={36} className="text-green-500" />
                <p className="font-display font-bold text-ink">Request Submitted!</p>
                <p className="text-[13px] text-stone-400">We'll create this content based on demand.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="p-5 space-y-4">

                {/* Type selector */}
                <div>
                  <label className="block text-[11px] font-semibold text-stone-500 uppercase tracking-widest mb-2">
                    Content Type
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(TYPE_LABELS).filter(([k]) => k !== "general").map(([value, label]) => (
                      <button
                        key={value}
                        type="button"
                        onClick={() => setType(value)}
                        className={`px-3 py-1.5 rounded-full text-[12px] font-semibold transition-colors border ${
                          type === value
                            ? "bg-teal-500 text-white border-teal-500"
                            : "bg-white text-stone-500 border-stone-200 hover:border-teal-300"
                        }`}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Topic title */}
                <div>
                  <label className="block text-[11px] font-semibold text-stone-500 uppercase tracking-widest mb-1.5">
                    Topic / Title
                  </label>
                  <input
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="e.g. Diagnostic Centers in Medak"
                    required
                    className="w-full rounded-xl border border-stone-200 px-3 py-2.5 text-[13px] text-ink placeholder-stone-300 focus:outline-none focus:border-teal-400"
                  />
                </div>

                {/* Optional description */}
                <div>
                  <label className="block text-[11px] font-semibold text-stone-500 uppercase tracking-widest mb-1.5">
                    Details <span className="text-stone-300 normal-case">(optional)</span>
                  </label>
                  <textarea
                    value={desc}
                    onChange={(e) => setDesc(e.target.value)}
                    placeholder="Why is this useful? Who would benefit?"
                    rows={2}
                    className="w-full rounded-xl border border-stone-200 px-3 py-2.5 text-[13px] text-ink placeholder-stone-300 focus:outline-none focus:border-teal-400 resize-none"
                  />
                </div>

                {status === "error" && (
                  <p className="text-[12px] text-rose-500 font-medium">Something went wrong. Try again.</p>
                )}

                <button
                  type="submit"
                  disabled={status === "submitting" || !title.trim()}
                  className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-teal-500 text-white text-[13px] font-semibold hover:bg-teal-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send size={13} />
                  {status === "submitting" ? "Submitting…" : "Submit Request"}
                </button>
              </form>
            )}
          </div>
        </div>
      )}
    </>
  );
}
