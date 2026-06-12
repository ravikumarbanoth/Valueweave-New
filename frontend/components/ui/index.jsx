// Shared UI primitives for Research Hub / District / Radar pages.
// Styled to the existing ValueWeave theme (cream, amber/teal, font-display).

import Link from "next/link";
import { CATEGORY_LABELS } from "@/lib/theme";

export function ScoreBadge({ score, label, variant = "fit" }) {
  const color =
    score >= 85
      ? variant === "fit"
        ? "bg-teal-100 text-teal-700 border-teal-200"
        : "bg-amber-100 text-amber-700 border-amber-200"
      : score >= 70
      ? "bg-stone-100 text-stone-600 border-stone-200"
      : "bg-red-50 text-red-600 border-red-200";

  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-display font-bold border ${color}`}>
      {score}
      {label && <span className="font-normal opacity-70">{label}</span>}
    </span>
  );
}

export function InvestmentBadge({ label }) {
  return (
    <span className="chip bg-amber-50 text-amber-700 border border-amber-200">{label}</span>
  );
}

export function SectionHeader({ eyebrow, title, subtitle, centered }) {
  return (
    <div className={`mb-8 ${centered ? "text-center" : ""}`}>
      {eyebrow && <span className="chip bg-teal-100 text-teal-600 mb-3">{eyebrow.toUpperCase()}</span>}
      <h2 className="font-display font-extrabold tracking-tight leading-tight text-2xl sm:text-3xl text-ink">{title}</h2>
      {subtitle && <p className="mt-3 text-base text-muted max-w-2xl">{subtitle}</p>}
    </div>
  );
}

export function Breadcrumb({ items }) {
  return (
    <nav className="flex items-center gap-1.5 text-sm text-muted flex-wrap" aria-label="Breadcrumb">
      {items.map((item, i) => (
        <span key={i} className="flex items-center gap-1.5">
          {i > 0 && <span className="text-stone-300">/</span>}
          {item.href ? (
            <Link href={item.href} className="hover:text-amber-600 transition-colors font-display font-semibold">
              {item.label}
            </Link>
          ) : (
            <span className="text-ink font-display font-semibold">{item.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}

export function CategoryBadge({ category }) {
  return (
    <span className="chip bg-teal-50 text-teal-700 border border-teal-200">
      {CATEGORY_LABELS[category] ?? category}
    </span>
  );
}

export function EmptyState({ title, description, action }) {
  return (
    <div className="text-center py-16 px-6">
      <div className="text-5xl mb-4">🔍</div>
      <h3 className="font-display font-bold text-lg text-ink mb-2">{title}</h3>
      <p className="text-muted text-sm max-w-sm mx-auto">{description}</p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
