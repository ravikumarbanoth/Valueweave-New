import { createClient } from "@/lib/supabase-server";
import { Activity } from "lucide-react";

const EVENT_TEMPLATES = {
  page_view: (row) => {
    if (row.detail?.includes("/explore")) return `Someone explored ${row.sector || "business"} opportunities`;
    if (row.detail?.includes("/discover")) return "Someone completed Discover Yourself";
    if (row.detail?.includes("/ideas")) return "Someone browsed business ideas";
    if (row.detail?.includes("/collaborators")) return "Someone joined as collaborator";
    if (row.district) return `Someone viewed an opportunity in ${row.district}`;
    return "Someone visited ValueWeave";
  },
  visitor: (row) => {
    if (row.detail === "mobile") return "Someone discovered ValueWeave on mobile";
    return "Someone explored ValueWeave";
  },
  search: (row) => `Someone searched on ValueWeave`,
  content_request: () => "Someone requested new content",
  feedback: () => "Someone shared feedback",
};

function anonymize(row) {
  const fn = EVENT_TEMPLATES[row.event_type] || (() => "Someone visited ValueWeave");
  return fn(row);
}

async function fetchActivity() {
  if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
    return [];
  }
  try {
    const sb = createClient();
    const { data } = await sb
      .from("visitor_sessions")
      .select("page_path, device_type, created_at")
      .order("created_at", { ascending: false })
      .limit(10);

    if (!data || data.length === 0) return [];

    return data.map((row) => {
      let text = "Someone visited ValueWeave";
      if (row.page_path?.includes("/explore")) text = "Someone explored business opportunities";
      else if (row.page_path?.includes("/discover")) text = "Someone completed Discover Yourself";
      else if (row.page_path?.includes("/ideas")) text = "Someone browsed 122 business ideas";
      else if (row.page_path?.includes("/collaborators")) text = "Someone joined as a collaborator";
      else if (row.page_path?.includes("/research")) text = "Someone read a research report";
      else if (row.page_path?.includes("/district")) text = "Someone explored district opportunities";
      return { text, created_at: row.created_at };
    });
  } catch {
    return [];
  }
}

function timeAgo(dateStr) {
  const diff = Math.floor((Date.now() - new Date(dateStr)) / 1000);
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

const PULSE_COLORS = [
  "bg-amber-400",
  "bg-teal-400",
  "bg-violet-400",
  "bg-emerald-400",
  "bg-rose-400",
];

export default async function HomeLiveActivity() {
  const items = await fetchActivity();

  if (items.length === 0) return null;

  return (
    <section className="py-16 sm:py-20 px-4 sm:px-6 bg-warm">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-10">
          <span className="chip bg-emerald-100 text-emerald-700 mb-4 inline-flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            LIVE ACTIVITY
          </span>
          <h2 className="font-display font-extrabold text-3xl sm:text-4xl tracking-tight text-ink mb-3">
            What&apos;s Happening Now
          </h2>
          <p className="text-muted text-sm">
            Anonymous activity from ValueWeave builders across India.
          </p>
        </div>

        <div className="card-base divide-y divide-stone-100 overflow-hidden">
          {items.map((item, i) => (
            <div key={i} className="flex items-center gap-3 px-5 py-3.5">
              <div className={`w-2 h-2 rounded-full shrink-0 ${PULSE_COLORS[i % PULSE_COLORS.length]}`} />
              <p className="text-sm text-ink flex-1">{item.text}</p>
              <span className="text-[11px] text-stone-400 shrink-0 font-semibold">
                {timeAgo(item.created_at)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
