import Link from "next/link";
import { CapabilityChip } from "@/components/knowledge/CapabilityStatus";

export default function InfrastructureCard({
  href,
  emoji,
  title,
  subtitle,
  description,
  items = [],
  accent = "amber",
  buttonLabel = "Explore",
  // Step 4: was `comingSoon`, a boolean that could only say "not yet" and never
  // said why. `status` distinguishes a capability waiting to be built from one
  // with no data source at all, and CapabilityChip renders both honestly.
  status = null,
}) {
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
      className={`${styles[accent] || styles.amber} border-2 rounded-2xl p-6 flex flex-col gap-4 hover:-translate-y-1 hover:shadow-md transition-all group min-h-[320px]`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="text-4xl" aria-hidden="true">{emoji}</div>
        {status && <CapabilityChip status={status} className="bg-white/80" />}
      </div>
      <div>
        <h3 className="font-display font-extrabold text-xl text-ink mb-2 group-hover:text-amber-700 transition-colors leading-tight">
          {title}
        </h3>
        {subtitle && <p className="font-display font-bold text-sm text-teal-700 mb-3">{subtitle}</p>}
        {description && <p className="text-sm text-muted leading-relaxed">{description}</p>}
      </div>
      {items.length > 0 && (
        <div className="grid grid-cols-1 gap-2">
          {items.map((item) => (
            <span key={item} className="flex items-center gap-2 text-sm text-stone-700">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0" />
              {item}
            </span>
          ))}
        </div>
      )}
      <div className="mt-auto pt-2">
        <span className="inline-flex items-center justify-center rounded-full bg-white/85 border border-white px-4 py-2 text-sm font-display font-bold text-ink group-hover:text-amber-700 transition-colors">
          {buttonLabel} →
        </span>
      </div>
    </Link>
  );
}
