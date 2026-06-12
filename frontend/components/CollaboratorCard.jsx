// Collaborator profile card — used on /collaborators pages and the
// Discover Yourself "Network" recommendations.

const ARCHETYPE_ICONS = {
  Innovator: "💡", Leader: "🦁", Builder: "🏗️", Analyst: "📊",
  Caregiver: "❤️", Explorer: "🧭", Researcher: "🔬", Influencer: "🎙️",
};

export default function CollaboratorCard({ collaborator: c }) {
  return (
    <div data-testid={`collab-card-${c.user_id}`} className="card-base p-5 flex flex-col gap-3 hover:border-amber-300 hover:shadow-md transition-all">
      <div className="flex items-start gap-3">
        <div className="w-11 h-11 rounded-full bg-gradient-to-br from-amber-300 to-teal-400 flex items-center justify-center text-xl shrink-0">
          {ARCHETYPE_ICONS[c.archetype] || "🤝"}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-display font-bold text-sm text-ink">{c.archetype}{c.secondary_archetype ? ` · ${c.secondary_archetype}` : ""}</h3>
          <p className="text-xs text-muted mt-0.5">
            {c.district ? `📍 ${c.district}${c.state ? `, ${c.state}` : ""}` : "📍 India"}
          </p>
        </div>
        {typeof c.ep_score === "number" && (
          <span className="chip bg-teal-50 text-teal-700 font-display font-bold shrink-0">EP {c.ep_score}</span>
        )}
      </div>

      {c.founder_role && (
        <div className="bg-stone-50 border border-stone-200 rounded-xl px-3 py-2">
          <p className="text-[10px] text-muted uppercase tracking-wider">Founder role</p>
          <p className="font-display font-bold text-xs text-ink">{c.founder_role}</p>
        </div>
      )}

      {c.top_sectors?.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {c.top_sectors.slice(0, 3).map((s) => (
            <span key={s} className="chip bg-amber-50 text-amber-700 capitalize">{s.replace(/-/g, " ")}</span>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between pt-2 border-t border-stone-100 text-xs text-muted">
        <span>{c.top_idea ? `Building: ${c.top_idea}` : "Open to ideas"}</span>
        {c.budget && <span className="font-display font-semibold text-amber-700">{c.budget}</span>}
      </div>
    </div>
  );
}
