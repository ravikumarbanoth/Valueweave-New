import { createClient } from "@/lib/supabase-server";
import Link from "next/link";
import { MessageSquare, ArrowUp, ChevronRight } from "lucide-react";
import AskQuestionForm from "@/components/AskQuestionForm";

export const revalidate = 60;

export const metadata = {
  title: "Community Questions | ValueWeave",
  description: "Ask questions about opportunities, districts, and sectors across India's startup ecosystem.",
};

async function fetchQuestions() {
  try {
    const sb = createClient();
    const { data } = await sb
      .from("questions")
      .select("id,title,body,district,sector,upvotes,answer_count,created_at")
      .eq("status", "open")
      .order("created_at", { ascending: false })
      .limit(50);
    return data || [];
  } catch {
    return [];
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

export default async function QuestionsPage() {
  const questions = await fetchQuestions();

  return (
    <div className="min-h-screen bg-stone-50">
      <div className="max-w-3xl mx-auto px-4 py-10">

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <div>
            <span className="chip bg-teal-100 text-teal-700 border border-teal-200">COMMUNITY</span>
            <h1 className="font-display font-extrabold text-2xl text-ink mt-2 flex items-center gap-2">
              <MessageSquare size={22} className="text-teal-500" />
              Community Questions
            </h1>
            <p className="text-stone-500 text-sm mt-1">
              Ask about opportunities, districts, sectors — get answers from the ValueWeave community.
            </p>
          </div>
        </div>

        {/* Ask Form */}
        <div className="mb-8">
          <AskQuestionForm />
        </div>

        {/* Questions List */}
        {questions.length === 0 ? (
          <div className="card-base p-10 text-center">
            <MessageSquare size={36} className="text-stone-200 mx-auto mb-3" />
            <p className="font-display font-bold text-stone-400">No questions yet</p>
            <p className="text-[13px] text-stone-300 mt-1">Be the first to ask something!</p>
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-[11px] font-semibold text-stone-400 uppercase tracking-widest">
              {questions.length} Open Question{questions.length !== 1 ? "s" : ""}
            </p>
            {questions.map((q) => (
              <Link
                key={q.id}
                href={`/questions/${q.id}`}
                className="card-base p-4 flex items-start gap-4 hover:shadow-md transition-shadow group block"
              >
                {/* Upvote count */}
                <div className="flex flex-col items-center gap-0.5 shrink-0 min-w-[36px]">
                  <ArrowUp size={14} className="text-stone-300 group-hover:text-amber-500 transition-colors" />
                  <span className="text-[12px] font-bold text-stone-500">{q.upvotes}</span>
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <p className="font-display font-semibold text-ink text-sm group-hover:text-amber-700 transition-colors line-clamp-2">
                    {q.title}
                  </p>
                  {q.body && (
                    <p className="text-[12px] text-stone-500 mt-0.5 line-clamp-1">{q.body}</p>
                  )}
                  <div className="flex items-center gap-3 mt-2 flex-wrap">
                    {q.district && (
                      <span className="chip bg-teal-50 text-teal-600 text-[10px]">{q.district}</span>
                    )}
                    {q.sector && (
                      <span className="chip bg-amber-50 text-amber-600 text-[10px]">{q.sector}</span>
                    )}
                    <span className="text-[10px] text-stone-300">{timeAgo(q.created_at)}</span>
                  </div>
                </div>

                {/* Answer count */}
                <div className="flex flex-col items-end gap-1 shrink-0">
                  <div className={`flex items-center gap-1 px-2 py-1 rounded-lg ${q.answer_count > 0 ? "bg-green-50 text-green-600" : "bg-stone-100 text-stone-400"}`}>
                    <span className="text-[11px] font-bold">{q.answer_count}</span>
                    <span className="text-[9px] uppercase tracking-wide">ans</span>
                  </div>
                  <ChevronRight size={12} className="text-stone-300 group-hover:text-amber-400" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
