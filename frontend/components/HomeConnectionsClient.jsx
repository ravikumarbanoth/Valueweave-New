"use client";
// Renders the trails HomeConnections read from the graph. Entity names are data
// and stay as written; the relationship words and headings follow the
// language switcher.
import Link from "next/link";
import { Sprout, Sun, Scissors, Stethoscope, ArrowRight } from "lucide-react";
import { useLanguage } from "@/lib/language";

const THEME = {
  food:     { icon: Sprout,      label: "Food & farming" },
  energy:   { icon: Sun,         label: "Clean energy" },
  heritage: { icon: Scissors,    label: "Traditional crafts" },
  health:   { icon: Stethoscope, label: "Healthcare" },
};

// Plain words for each edge, read as "<anchor> … <this> <target>".
const RELATION = {
  REQUIRES_SKILL:      "needs the skill",
  SUPPORTED_BY_SCHEME: "supported by",
  PART_OF:             "part of",
  PROCESSES:           "processes",
  USES_RAW_MATERIAL:   "uses",
  USES_MACHINERY:      "works with",
  SUPPORTED_BY_BANK:   "financed by",
  SELLS_TO:            "sells to",
  EXPORTS_TO:          "exports to",
  RELATED_TO:          "grows in",
};

const TYPE = {
  Skill: "Skill", GovernmentScheme: "Scheme", Industry: "Industry", Crop: "Crop",
  MSME: "Business", BusinessOpportunity: "Business idea", Machinery: "Equipment",
  RawMaterial: "Material", FinancialInstitution: "Lender", Market: "Market",
  ExportCountry: "Export market", Soil: "Soil", ClimateZone: "Climate",
};

export default function HomeConnectionsClient({ trails }) {
  const { t } = useLanguage();

  return (
    <section data-testid="home-connections" className="py-20 sm:py-24 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <span className="chip bg-amber-100 text-amber-700 mb-4">{t("connections.chip", "HOW IT CONNECTS")}</span>
          <h2 className="font-display font-extrabold text-3xl sm:text-4xl md:text-5xl tracking-tight leading-tight text-ink">
            {t("connections.title", "Follow a connection")}
          </h2>
          <p className="mt-4 text-muted max-w-2xl mx-auto text-base sm:text-lg leading-relaxed">
            {t("connections.subtitle", "Start from a business and see the skills, schemes and industries it is linked to in what we have researched. Every step opens.")}
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-5">
          {trails.map((trail) => {
            const theme = THEME[trail.theme] || THEME.food;
            const Icon = theme.icon;
            return (
              <article key={trail.anchor.href} data-testid="home-connection-trail" className="card-base p-5 sm:p-6">
                <div className="flex items-center gap-2 mb-4">
                  <span className="w-8 h-8 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
                    <Icon size={16} aria-hidden="true" />
                  </span>
                  <span className="text-[11px] font-display font-bold tracking-wider uppercase text-amber-700">
                    {t(`connections.theme_${trail.theme}`, theme.label)}
                  </span>
                </div>

                {/* The trail: the starting point, then each linked thing hanging
                    off one line with a node at every step. */}
                <ol className="relative">
                  <span aria-hidden="true" className="absolute left-[11px] top-3 bottom-3 w-px bg-gradient-to-b from-amber-400 to-amber-200" />
                  <li className="relative pl-9 pb-3">
                    <span aria-hidden="true" className="absolute left-[5px] top-1.5 w-[13px] h-[13px] rounded-full bg-amber-500 ring-4 ring-amber-100" />
                    <Link href={trail.anchor.href} data-testid="home-connection-anchor" className="group inline-flex flex-col min-h-[44px] justify-center">
                      <span className="text-[11px] text-muted">{t(`connections.type_${trail.anchor.type}`, TYPE[trail.anchor.type] || trail.anchor.type)}</span>
                      <span className="font-display font-bold text-base sm:text-lg text-ink leading-snug group-hover:text-amber-700 transition-colors">
                        {trail.anchor.name}
                      </span>
                    </Link>
                  </li>
                  {trail.links.map((link) => (
                    <li key={link.href} className="relative pl-9 py-1">
                      <span aria-hidden="true" className="absolute left-[7px] top-1/2 -translate-y-1/2 w-[9px] h-[9px] rounded-full bg-white border-2 border-amber-400" />
                      <Link href={link.href} data-testid="home-connection-link" className="group flex items-center justify-between gap-3 min-h-[44px] rounded-xl px-3 py-2 -mx-1 hover:bg-amber-50 transition-colors">
                        <span className="min-w-0">
                          <span className="block text-[11px] text-muted">
                            {t(`connections.rel_${link.relationship}`, RELATION[link.relationship] || "linked to")}
                            {" · "}
                            {t(`connections.type_${link.type}`, TYPE[link.type] || link.type)}
                          </span>
                          <span className="block text-sm font-semibold text-ink leading-snug group-hover:text-amber-700 transition-colors">
                            {link.name}
                          </span>
                        </span>
                        <ArrowRight size={14} aria-hidden="true" className="shrink-0 text-stone-300 group-hover:text-amber-500 transition-colors" />
                      </Link>
                    </li>
                  ))}
                </ol>
              </article>
            );
          })}
        </div>

        <p className="mt-6 text-center text-xs text-muted max-w-xl mx-auto leading-relaxed">
          {t("connections.note", "Every link above comes from ValueWeave's own research. We show only the connections our research has found.")}
        </p>
      </div>
    </section>
  );
}
