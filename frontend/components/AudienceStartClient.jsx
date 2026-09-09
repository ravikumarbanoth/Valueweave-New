"use client";
import Link from "next/link";
import { AUDIENCES } from "@/lib/audiences";
import { useLanguage } from "@/lib/language";

export default function AudienceStartClient({ audience }) {
  const { t } = useLanguage();

  return (
    <main className="min-h-screen bg-cream font-body pb-16">
      <section className="bg-ink text-white px-4 sm:px-6 py-12 sm:py-14">
        <div className="max-w-3xl mx-auto">
          <Link href="/" className="inline-flex items-center min-h-[44px] text-xs text-white/50 hover:text-white/80">
            {t("ui.back_home", "← Back to home")}
          </Link>
          <p className="text-4xl mt-4 mb-3" aria-hidden="true">{audience.emoji}</p>
          <h1 className="font-display font-extrabold tracking-tight text-3xl sm:text-4xl leading-tight mb-4">
            {audience.headline}
          </h1>
          <p className="text-white/65 leading-relaxed max-w-2xl">{audience.intro}</p>
        </div>
      </section>

      <section className="max-w-3xl mx-auto px-4 sm:px-6 py-10">
        <h2 className="label-display mb-4">{t("audience_start.start_with", "Start with one of these")}</h2>
        <div className="flex flex-col gap-3" data-testid="audience-starts">
          {audience.starts.map((start, index) => (
            <Link
              key={start.href}
              href={start.href}
              data-testid="audience-start"
              className="card-base p-5 flex items-center gap-4 hover:border-amber-300 hover:shadow-md transition-all group"
            >
              <span className="shrink-0 w-8 h-8 rounded-full bg-amber-50 border border-amber-100 flex items-center justify-center font-display font-bold text-sm text-amber-700 tabular-nums">
                {index + 1}
              </span>
              <span className="min-w-0">
                <span className="block font-display font-bold text-ink group-hover:text-amber-700 transition-colors">
                  {start.label}
                </span>
                <span className="block text-sm text-muted mt-0.5">{start.hint}</span>
              </span>
              <span className="ml-auto text-amber-700 shrink-0" aria-hidden="true">→</span>
            </Link>
          ))}
        </div>

        <h2 className="label-display mt-10 mb-3">{t("audience_start.or_search", "Or search for something specific")}</h2>
        <div className="flex flex-wrap gap-2" data-testid="audience-prompts">
          {audience.prompts.map((prompt) => (
            <Link
              key={prompt}
              href={`/knowledge?q=${encodeURIComponent(prompt)}`}
              className="chip bg-white text-stone-600 border border-stone-200 hover:border-amber-300 hover:bg-amber-50 transition-colors"
            >
              {prompt}
            </Link>
          ))}
        </div>

        <div className="mt-10 pt-6 border-t border-stone-200">
          <p className="text-sm text-muted mb-3">{t("audience_start.not_quite_you", "Not quite you?")}</p>
          <div className="flex flex-wrap gap-2" data-testid="audience-switch">
            {AUDIENCES.filter((a) => a.slug !== audience.slug).map((other) => (
              <Link
                key={other.slug}
                href={`/start/${other.slug}`}
                className="chip bg-white text-stone-600 border border-stone-200 hover:border-teal-500 hover:bg-teal-50 transition-colors"
              >
                <span aria-hidden="true" className="mr-1">{other.emoji}</span>
                {t(`audience.${other.slug}`, other.label)}
              </Link>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
