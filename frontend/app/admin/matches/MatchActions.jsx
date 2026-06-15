"use client";
import { useState } from "react";
import { createClient } from "@/lib/supabase-browser";
import { CheckCircle, XCircle, Mail, Loader2 } from "lucide-react";

export default function MatchActions({ matchId, initialStatus }) {
  const [status, setStatus] = useState(initialStatus || "pending");
  const [loading, setLoading] = useState(false);

  const update = async (newStatus) => {
    setLoading(true);
    const sb = createClient();
    const { error } = await sb
      .from("founder_matches")
      .update({ status: newStatus, updated_at: new Date().toISOString() })
      .eq("id", matchId);
    if (!error) setStatus(newStatus);
    setLoading(false);
  };

  if (status === "approved") {
    return (
      <div className="flex items-center gap-1.5 text-green-600 text-[12px] font-semibold">
        <CheckCircle size={14} /> Approved
      </div>
    );
  }
  if (status === "ignored") {
    return (
      <div className="flex items-center gap-1.5 text-stone-400 text-[12px] font-semibold">
        <XCircle size={14} /> Ignored
      </div>
    );
  }
  if (status === "contacted") {
    return (
      <div className="flex items-center gap-1.5 text-blue-600 text-[12px] font-semibold">
        <Mail size={14} /> Contacted
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {loading && <Loader2 size={14} className="animate-spin text-stone-400" />}
      <button
        onClick={() => update("approved")}
        disabled={loading}
        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-green-50 text-green-700 border border-green-200 text-[12px] font-semibold hover:bg-green-100 transition-colors"
      >
        <CheckCircle size={12} /> Approve
      </button>
      <button
        onClick={() => update("contacted")}
        disabled={loading}
        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 text-[12px] font-semibold hover:bg-blue-100 transition-colors"
      >
        <Mail size={12} /> Contact Both
      </button>
      <button
        onClick={() => update("ignored")}
        disabled={loading}
        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-stone-50 text-stone-500 border border-stone-200 text-[12px] font-semibold hover:bg-stone-100 transition-colors"
      >
        <XCircle size={12} /> Ignore
      </button>
    </div>
  );
}
