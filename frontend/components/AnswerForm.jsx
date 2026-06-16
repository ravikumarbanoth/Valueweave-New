"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase-browser";
import { Send, AlertCircle, CheckCircle } from "lucide-react";

export default function AnswerForm({ questionId }) {
  const router = useRouter();
  const [body, setBody] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [done, setDone] = useState(false);

  async function submit() {
    setError(null);
    if (!body.trim()) { setError("Answer cannot be empty."); return; }
    setSaving(true);
    const sb = createClient();
    const { data: { user } } = await sb.auth.getUser();
    if (!user) { setError("Sign in to post an answer."); setSaving(false); return; }

    const { error: err } = await sb.from("answers").insert({
      question_id: questionId,
      user_id: user.id,
      body: body.trim(),
    });

    setSaving(false);
    if (err) { setError("Failed to post. Please try again."); return; }
    setDone(true);
    setBody("");
    router.refresh();
  }

  if (done) {
    return (
      <div className="card-base p-4 flex items-center gap-3 border border-green-200 bg-green-50">
        <CheckCircle size={16} className="text-green-600 shrink-0" />
        <p className="text-sm font-semibold text-green-700">Answer posted!</p>
        <button onClick={() => setDone(false)} className="ml-auto text-[12px] text-green-600 underline">Add another</button>
      </div>
    );
  }

  return (
    <div className="card-base p-5 space-y-3">
      {error && (
        <div className="flex items-center gap-2 p-3 bg-rose-50 border border-rose-200 rounded-xl text-[12px] text-rose-700">
          <AlertCircle size={13} /> {error}
        </div>
      )}
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        rows={5}
        placeholder="Share your knowledge, experience, or relevant resources…"
        className="input-base w-full resize-none"
      />
      <div className="flex justify-end">
        <button
          onClick={submit}
          disabled={saving || !body.trim()}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-teal-500 text-white text-[13px] font-semibold hover:bg-teal-600 disabled:opacity-50"
        >
          <Send size={13} />
          {saving ? "Posting…" : "Post Answer"}
        </button>
      </div>
    </div>
  );
}
