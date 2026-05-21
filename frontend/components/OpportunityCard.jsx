import Link from "next/link";
import { MapPin } from "lucide-react";

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

const COLLAB_LABEL = {
  "cofounder": "Co-founder",
  "partner": "Partner",
  "team-member": "Team member",
  "freelance": "Freelance",
  "mentor": "Mentor",
};
const COMMIT_LABEL = {
  "full-time": "Full-time",
  "part-time": "Part-time",
  "project-based": "Project",
  "casual": "Casual",
};

export default function OpportunityCard({ opp, isNearby = false }) {
  const cat = CATEGORY_META[opp.category] || { emoji: "🌐", label: opp.category };
  const owner = opp.owner || {};
  return (
    <Link
      href={`/opportunities/${opp.id}`}
      data-testid={`opp-card-${opp.id}`}
      className="card-base p-5 flex flex-col gap-3 hover:-translate-y-1 hover:shadow-lg hover:border-amber-400 transition-all relative"
    >
      {isNearby && (
        <span data-testid={`opp-nearby-${opp.id}`} className="absolute top-3 right-3 chip bg-teal-100 text-teal-700 text-[10px]">
          <MapPin size={10} /> Nearby
        </span>
      )}

      {/* Lightweight tag row */}
      <div className="flex flex-wrap gap-1.5">
        <span data-testid={`opp-tag-category-${opp.id}`} className="chip bg-amber-50 text-amber-700">
          {cat.emoji} {cat.label}
        </span>
        <span data-testid={`opp-tag-collab-${opp.id}`} className="chip bg-teal-50 text-teal-700">
          {COLLAB_LABEL[opp.collaboration_type] || opp.collaboration_type}
        </span>
        <span data-testid={`opp-tag-commit-${opp.id}`} className="chip bg-violet-50 text-violet-700">
          {COMMIT_LABEL[opp.commitment] || opp.commitment}
        </span>
      </div>

      <h3 className="h-card line-clamp-2">{opp.title}</h3>
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
        <span data-testid={`opp-location-${opp.id}`} className="ml-auto inline-flex items-center gap-1 text-[11px] text-muted">
          <MapPin size={11} /> {opp.location}
        </span>
      </div>
    </Link>
  );
}

export { CATEGORY_META };
