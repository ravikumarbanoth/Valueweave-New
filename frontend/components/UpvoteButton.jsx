"use client";
import { useState } from "react";
import { createClient } from "@/lib/supabase-browser";
import { ArrowUp } from "lucide-react";

export default function UpvoteButton({ table, id, initialCount }) {
  const [count, setCount] = useState(initialCount || 0);
  const [voted, setVoted] = useState(false);
  const [saving, setSaving] = useState(false);

  async function upvote() {
    if (voted || saving) return;
    setSaving(true);
    const sb = createClient();
    const { data, error } = await sb
      .from(table)
      .update({ upvotes: count + 1 })
      .eq("id", id)
      .select("upvotes")
      .single();
    setSaving(false);
    if (!error && data) {
      setCount(data.upvotes);
      setVoted(true);
    }
  }

  return (
    <button
      onClick={upvote}
      disabled={voted || saving}
      title={voted ? "Already upvoted" : "Upvote"}
      className={`flex flex-col items-center gap-0.5 shrink-0 p-1.5 rounded-lg transition-colors ${
        voted
          ? "text-amber-500 bg-amber-50"
          : "text-stone-300 hover:text-amber-500 hover:bg-amber-50"
      } disabled:cursor-default`}
    >
      <ArrowUp size={16} />
      <span className="text-[11px] font-bold">{count}</span>
    </button>
  );
}
