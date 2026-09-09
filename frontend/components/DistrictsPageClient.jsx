"use client";
import Link from "next/link";
import ModuleShell from "@/components/platform/ModuleShell";
import { DISTRICTS } from "@/lib/districts-data";
import { hrefFor } from "@/lib/knowledge";
import ConfidenceBadge from "@/components/knowledge/ConfidenceBadge";
import SourceBadge from "@/components/knowledge/SourceBadge";
import KnowledgeEmptyState from "@/components/knowledge/KnowledgeEmptyState";
import { useLanguage } from "@/lib/language";

export default function DistrictsPageClient({ entities, researchedOnly, groups }) {
  const { t } = useLanguage();

  return (
    <ModuleShell
      badge={t("districts.badge", "DISTRICTS")}
      title={t("districts.hero_title", "Discover Where Opportunities Exist")}
      description={t("districts.hero_desc", "Start with where you already are. Every district here shows the industries around it, the businesses people start there, where to learn the skills, and which government schemes apply.")}
    >
      <div className="space-y-10">
        {entities.length > 0 && (
          <p className="text-sm text-muted" data-testid="districts-coverage">
            <strong className="text-ink tabular-nums">{entities.length}</strong> districts
            with information gathered from official sources.{" "}
            <strong className="text-ink tabular-nums">{DISTRICTS.length}</strong> have a
            written profile; the rest have data but no write-up yet.
          </p>
        )}

        {groups.map(({ state, districts }) => (
          <section key={state} data-testid="district-editorial-group">
            <div className="flex items-center justify-between gap-3 mb-5">
              <h2 className="font-display font-extrabold text-2xl text-ink">{state}</h2>
              <span className="text-sm text-muted">{districts.length} written profiles</span>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {districts.map((district) => (
                <Link key={district.slug} href={`/districts/${district.slug}`} data-testid="district-editorial-card" className="card-base p-5 hover:border-teal-300 hover:shadow-md hover:-translate-y-1 transition-all group">
                  <h3 className="font-display font-bold text-lg text-ink group-hover:text-teal-700 transition-colors">{district.name}</h3>
                  <p className="text-xs text-stone-400 mt-1">{district.region}</p>
                  <p className="text-sm text-muted line-clamp-2 mt-3 leading-relaxed">{district.profileSummary}</p>
                  <div className="mt-4 text-amber-700 text-sm font-display font-bold">{t("districts.open_module", "Open district module →")}</div>
                </Link>
              ))}
            </div>
          </section>
        ))}

        <section data-testid="districts-researched">
          <div className="flex items-center justify-between gap-3 mb-2">
            <h2 className="font-display font-extrabold text-2xl text-ink">
              {t("districts.every_researched", "Every researched district")}
            </h2>
            {researchedOnly.length > 0 && (
              <span className="text-sm text-muted tabular-nums">{researchedOnly.length} more</span>
            )}
          </div>
          <p className="text-sm text-muted mb-5 max-w-2xl leading-relaxed">
            Population, area, literacy and headquarters for every district, plus the
            industries, businesses and schemes connected to each one. No write-up yet —
            we are working through them.
          </p>

          {entities.length === 0 ? (
            <KnowledgeEmptyState reason="NOT_DEPLOYED" entityLabel="districts" />
          ) : researchedOnly.length === 0 ? (
            <KnowledgeEmptyState
              reason="NO_MATCH"
              entityLabel="districts"
              note="Every researched district already has a written profile above."
            />
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {researchedOnly.map((entity) => (
                <Link
                  key={entity.global_entity_id}
                  href={hrefFor(entity)}
                  data-testid="district-researched-card"
                  className="card-base p-4 hover:border-teal-300 hover:shadow-md transition-all group flex flex-col gap-2"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-display font-bold text-[15px] text-ink group-hover:text-teal-700 transition-colors leading-snug">
                      {entity.canonical_name}
                    </h3>
                    <ConfidenceBadge confidence={entity.confidence_score} />
                  </div>
                  <SourceBadge sourcePackage={entity.source_package} className="w-fit" />
                </Link>
              ))}
            </div>
          )}
        </section>
      </div>
    </ModuleShell>
  );
}
