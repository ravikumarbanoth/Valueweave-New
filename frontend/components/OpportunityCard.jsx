import Link from "next/link";

const CATEGORY_META = {
  "ai-tech": { emoji: "🤖", label: "AI & Tech" },
  "local-business": { emoji: "🏪", label: "Local Business" },
  "ev-electronics": { emoji: "⚡", label: "EV & Electronics" },
  "drone": { emoji: "🚁", label: "Drone" },
  "agri": { emoji: "🌾", label: "Agriculture" },
  "student": { emoji: "🎓", label: "Student" },
  "trades": { emoji: "🔧", label: "Trades" },
  "digital": { emoji: "📱", label: "Digital" },
};

export default function OpportunityCard({ opp }) {
  const cat = CATEGORY_META[opp.category] || { emoji: "🌐", label: opp.category };
  const owner = opp.owner || {};
  return (
    <Link
      href={`/opportunities/${opp.id}`}
      data-testid={`opp-card-${opp.id}`}
      className="card-base p-5 flex flex-col gap-3 hover:-translate-y-1 hover:shadow-xl hover:border-amber-500 transition-all"
    >
      <div className="flex justify-between items-start gap-2">
        <span className="chip bg-amber-50 text-amber-700">{cat.emoji} {cat.label}</span>
        <span className="text-xs text-muted shrink-0">📍 {opp.location}</span>
      </div>
      <h3 className="font-display font-bold text-base text-ink leading-snug line-clamp-2">{opp.title}</h3>
      <p className="text-sm text-muted leading-relaxed line-clamp-3">{opp.description}</p>
      {opp.skills_needed?.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {opp.skills_needed.slice(0, 4).map((s) => (
            <span key={s} className="chip bg-stone-100 text-stone-700">{s}</span>
          ))}
        </div>
      )}
      <div className="flex items-center gap-2 pt-3 border-t border-stone-100">
        {owner.picture ? (
          <img src={owner.picture} alt="" className="w-7 h-7 rounded-full" />
        ) : (
          <div className="w-7 h-7 rounded-full bg-amber-200 text-amber-700 flex items-center justify-center font-bold text-xs">
            {(owner.name || "?")[0]?.toUpperCase()}
          </div>
        )}
        <span className="text-xs font-semibold text-ink">{owner.name || "Builder"}</span>
        <span className="text-[11px] text-muted ml-auto">{opp.collaboration_type} · {opp.commitment}</span>
      </div>
    </Link>
  );
}

export { CATEGORY_META };
