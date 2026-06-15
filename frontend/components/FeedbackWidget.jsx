"use client";
// Floating feedback button fixed to the bottom-right corner of every page.
// Submits to the user_feedback table (type values match the DB check constraint).

import { useState } from "react";
import { MessageCircle, X, Send, CheckCircle } from "lucide-react";
import { createClient } from "@/lib/supabase-browser";

const TYPES = [
  { value: "general",  label: "Suggestion" },
  { value: "bug",      label: "Issue / Bug" },
  { value: "feature",  label: "Feature Request" },
  { value: "content",  label: "Content Request" },
  { value: "other",    label: "Other" },
];

export default function FeedbackWidget() {
  const [open, setOpen]       = useState(false);
  const [type, setType]       = useState("general");
  const [message, setMessage] = useState("");
  const [email, setEmail]     = useState("");
  const [status, setStatus]   = useState("idle"); // idle | submitting | success | error

  async function handleSubmit(e) {
    e.preventDefault();
    if (!message.trim()) return;
    setStatus("submitting");
    try {
      const sb = createClient();
      const { error } = await sb.from("user_feedback").insert({
        type,
        message: message.trim(),
        page: window.location.pathname,
        status: "unread",
      });
      if (error) throw error;
      setStatus("success");
      setTimeout(() => {
        setOpen(false);
        setStatus("idle");
        setMessage("");
        setEmail("");
        setType("general");
      }, 2200);
    } catch {
      setStatus("error");
    }
  }

  return (
    <>
      {/* Floating trigger */}
      <button
        onClick={() => setOpen(true)}
        aria-label="Send feedback"
        className="fixed bottom-5 right-5 z-50 flex items-center gap-2 px-4 py-2.5 rounded-full bg-amber-500 text-white shadow-lg shadow-amber-500/30 text-[13px] font-semibold hover:bg-amber-600 transition-all hover:scale-105 active:scale-95"
      >
        <MessageCircle size={15} />
        <span className="hidden sm:inline">Feedback</span>
      </button>

      {/* Modal overlay */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-black/30 backdrop-blur-sm">
          <div className="w-full max-w-sm bg-white rounded-2xl shadow-2xl overflow-hidden">

            {/* Header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-stone-100">
              <div>
                <p className="font-display font-bold text-ink text-[15px]">Share Feedback</p>
                <p className="text-[11px] text-stone-400 mt-0.5">We read every message</p>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="p-1.5 rounded-full hover:bg-stone-100 transition-colors text-stone-400"
              >
                <X size={16} />
              </button>
            </div>

            {/* Success state */}
            {status === "success" ? (
              <div className="flex flex-col items-center justify-center gap-3 py-10 px-6 text-center">
                <CheckCircle size={36} className="text-green-500" />
                <p className="font-display font-bold text-ink">Thank you!</p>
                <p className="text-[13px] text-stone-400">Your feedback was sent successfully.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="p-5 space-y-4">

                {/* Type selector */}
                <div>
                  <label className="block text-[11px] font-semibold text-stone-500 uppercase tracking-widest mb-2">
                    Type
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {TYPES.map(({ value, label }) => (
                      <button
                        key={value}
                        type="button"
                        onClick={() => setType(value)}
                        className={`px-3 py-1.5 rounded-full text-[12px] font-semibold transition-colors border ${
                          type === value
                            ? "bg-amber-500 text-white border-amber-500"
                            : "bg-white text-stone-500 border-stone-200 hover:border-amber-300"
                        }`}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Message */}
                <div>
                  <label className="block text-[11px] font-semibold text-stone-500 uppercase tracking-widest mb-1.5">
                    Message
                  </label>
                  <textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="What's on your mind?"
                    rows={4}
                    required
                    className="w-full rounded-xl border border-stone-200 px-3 py-2.5 text-[13px] text-ink placeholder-stone-300 focus:outline-none focus:border-amber-400 resize-none"
                  />
                </div>

                {status === "error" && (
                  <p className="text-[12px] text-rose-500 font-medium">Something went wrong. Please try again.</p>
                )}

                <button
                  type="submit"
                  disabled={status === "submitting" || !message.trim()}
                  className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-amber-500 text-white text-[13px] font-semibold hover:bg-amber-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send size={13} />
                  {status === "submitting" ? "Sending…" : "Send Feedback"}
                </button>
              </form>
            )}
          </div>
        </div>
      )}
    </>
  );
}
