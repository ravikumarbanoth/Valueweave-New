"use client";
import { useState } from "react";
import { createClient } from "@/lib/supabase-browser";
import { CheckCheck, Archive, Loader2 } from "lucide-react";

export function NotificationRowActions({ id, initialStatus, onUpdate }) {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(initialStatus);

  const update = async (newStatus) => {
    setLoading(true);
    const sb = createClient();
    await sb.from("admin_notifications").update({ status: newStatus }).eq("id", id);
    setStatus(newStatus);
    setLoading(false);
    onUpdate?.();
  };

  if (status !== "unread") {
    return (
      <span className={`chip text-[10px] ${status === "archived" ? "bg-stone-100 text-stone-400" : "bg-green-50 text-green-600"}`}>
        {status}
      </span>
    );
  }

  return (
    <div className="flex items-center gap-1.5">
      {loading && <Loader2 size={12} className="animate-spin text-stone-400" />}
      <button
        onClick={() => update("read")}
        disabled={loading}
        title="Mark read"
        className="p-1.5 rounded-lg hover:bg-green-50 text-stone-400 hover:text-green-600 transition-colors"
      >
        <CheckCheck size={13} />
      </button>
      <button
        onClick={() => update("archived")}
        disabled={loading}
        title="Archive"
        className="p-1.5 rounded-lg hover:bg-stone-100 text-stone-400 hover:text-stone-600 transition-colors"
      >
        <Archive size={13} />
      </button>
    </div>
  );
}

export function MarkAllRead({ onDone }) {
  const [loading, setLoading] = useState(false);

  const markAll = async () => {
    setLoading(true);
    const sb = createClient();
    await sb.from("admin_notifications").update({ status: "read" }).eq("status", "unread");
    setLoading(false);
    onDone?.();
    window.location.reload();
  };

  return (
    <button
      onClick={markAll}
      disabled={loading}
      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-green-50 text-green-700 border border-green-200 text-[12px] font-semibold hover:bg-green-100 transition-colors"
    >
      {loading ? <Loader2 size={13} className="animate-spin" /> : <CheckCheck size={13} />}
      Mark All Read
    </button>
  );
}
