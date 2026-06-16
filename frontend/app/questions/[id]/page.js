import { createClient } from "@/lib/supabase-server";
import { notFound } from "next/navigation";
import Link from "next/link";
import { MessageSquare, ArrowUp } from "lucide-react";
import AnswerForm from "@/components/AnswerForm";
import UpvoteButton from "@/components/UpvoteButton";

export const revalidate = 30;

export async function generateMetadata({ params }) {
  try {
    const sb = createClient();
    const { data } = await sb.from("questions").select("title").eq("id", params.id).single();
    return { title: `${data?.title || "Question"} | ValueWeave` };
  } catch {
    return { title: "Question | ValueWeave" };
  }
}

async function fetchQuestion(id) {
  try {
    const sb = createClient();
    const [{ data: q, error }, { data: answers }] = await Promise.all([
      sb.from("questions").select("*").eq("id", id).eq("status", "open").single(),
      sb.from("answers").select("*").eq("question_id", id).order("upvotes", { ascending: false }).limit(50),
    ]);
    if (error || !q) return null;
    return { question: q, answers: answers || [] };
  } catch {
    return null;
  }
}

function timeAgo(ts) {
  const diff = Date.now() - new Date(ts).getTime();
  const hours = Math.floor(diff / 3600000);
  const days  = Math.floor(diff / 86400000);
  if (hours < 1)  return "just now";
  if (hours < 24) return `${hours}h ago`;
  return `${days}d ago`;
}

export default async function QuestionPage({ params }) {
  const data = await fetchQuestion(params.id);
  if (!data) notFound();

  const { question: q, answers } = data;

  return (
    <div className="min-h-screen bg-stone-50">
      <div className="max-w-3xl mx-auto px-4 py-10">

        {/* Back nav */}
        <Link href="/questions" className="inline-flex items-center gap-1 text-[13px] text-stone-400 hover:text-amber-600 mb-6 transition-colors">
          ← All Questions
        </Link>

        {/* Question */}
        <div className="card-base p-6 mb-6">
          <div className="flex items-start gap-4">
            <UpvoteButton table="questions" id={q.id} initialCount={q.upvotes} />
            <div className="flex-1">
              <h1 className="font-display font-extrabold text-xl text-ink leading-snug">{q.title}</h1>
              {q.body && <p className="text-stone-500 mt-3 text-[14px] leading-relaxed">{q.body}</p>}
              <div className="flex items-center gap-3 mt-4 flex-wrap">
                {q.district && <span className="chip bg-teal-50 text-teal-600 text-[10px]">{q.district}</span>}
                {q.sector   && <span className="chip bg-amber-50 text-amber-600 text-[10px]">{q.sector}</span>}
                <span className="text-[11px] text-stone-300">{timeAgo(q.created_at)}</span>
                <span className="text-[11px] text-stone-300">·</span>
                <span className="text-[11px] text-stone-300">{q.answer_count} answer{q.answer_count !== 1 ? "s" : ""}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Answers */}
        {answers.length > 0 && (
          <div className="mb-6">
            <p className="text-[11px] font-semibold text-stone-400 uppercase tracking-widest mb-3">
              {answers.length} Answer{answers.length !== 1 ? "s" : ""}
            </p>
            <div className="space-y-3">
              {answers.map((a) => (
                <div key={a.id} className={`card-base p-5 flex items-start gap-4 ${a.is_accepted ? "border border-green-200 bg-green-50/40" : ""}`}>
                  <UpvoteButton table="answers" id={a.id} initialCount={a.upvotes} />
                  <div className="flex-1">
                    {a.is_accepted && (
                      <span className="chip bg-green-100 text-green-700 text-[10px] mb-2 inline-block">✓ Accepted</span>
                    )}
                    <p className="text-[14px] text-stone-700 leading-relaxed whitespace-pre-line">{a.body}</p>
                    <p className="text-[11px] text-stone-300 mt-2">{timeAgo(a.created_at)}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Answer form */}
        <div>
          <p className="text-[11px] font-semibold text-stone-400 uppercase tracking-widest mb-3">
            Your Answer
          </p>
          <AnswerForm questionId={q.id} />
        </div>

      </div>
    </div>
  );
}
