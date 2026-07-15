import Link from "next/link";

export default function InfrastructureCard({ href, emoji, title, description, items = [], accent = "amber" }) {
  const styles = {
    amber: "bg-amber-50 border-amber-200 hover:border-amber-300",
    teal: "bg-teal-50 border-teal-200 hover:border-teal-300",
    blue: "bg-blue-50 border-blue-200 hover:border-blue-300",
    green: "bg-emerald-50 border-emerald-200 hover:border-emerald-300",
    rose: "bg-rose-50 border-rose-200 hover:border-rose-300",
    violet: "bg-violet-50 border-violet-200 hover:border-violet-300",
    stone: "bg-stone-50 border-stone-200 hover:border-stone-300",
  };

  return (
    <Link
      href={href}
      className={`${styles[accent] || styles.amber} border-2 rounded-2xl p-6 flex flex-col gap-4 hover:-translate-y-1 hover:shadow-md transition-all group min-h-[220px]`}
    >
      <div className="text-3xl" aria-hidden="true">{emoji}</div>
      <div>
        <h3 className="font-display font-bold text-lg text-ink mb-2 group-hover:text-amber-700 transition-colors">
          {title}
        </h3>
        <p className="text-sm text-muted leading-relaxed">{description}</p>
      </div>
      {items.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-auto">
          {items.slice(0, 4).map((item) => (
            <span key={item} className="chip bg-white/70 text-stone-600 border border-white text-[10px]">
              {item}
            </span>
          ))}
        </div>
      )}
    </Link>
  );
}
