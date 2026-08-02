// Related graph entities, grouped by type, every one a link.
//
// This component is what makes the graph feel like a graph: from a business you
// reach its skills, from a skill its schemes, from a scheme its districts. The
// relationship type is shown on each chip because "why is this here?" is the
// first question a connected view raises.
import Link from "next/link";
import { hrefFor } from "@/lib/knowledge";
import SourceBadge from "./SourceBadge";

//: Exported so the detail page can name the category in its empty state
//: with the same words the populated state uses.
export const TYPE_LABELS = {
  District: "Districts",
  Industry: "Industries",
  BusinessOpportunity: "Business opportunities",
  MSME: "MSMEs",
  Skill: "Skills",
  GovernmentScheme: "Government schemes",
  Crop: "Crops",
  Certification: "Certifications",
  TrainingProvider: "Training providers",
  Institution: "Institutions",
  Machinery: "Machinery",
  Market: "Markets",
  FinancialInstitution: "Financial institutions",
  RawMaterial: "Raw materials",
  ExportCountry: "Export destinations",
  Soil: "Soil types",
  ClimateZone: "Climate zones",
  State: "States",
  Country: "Countries",
};

const VIA = (rel) => String(rel || "").toLowerCase().replace(/_/g, " ");

export default function RelatedEntities({
  grouped, only, exclude = [], emptyText, emptyHref, emptyLabel, max = 12,
}) {
  const types = Object.keys(grouped || {})
    .filter((t) => (only ? only.includes(t) : true))
    .filter((t) => !exclude.includes(t))
    .sort((a, b) => (grouped[b].length - grouped[a].length) || a.localeCompare(b));

  // PX Phase 4. This was one italic sentence — "We have not connected anything
  // to this yet. It is a gap in our research, not a sign that nothing is
  // related." — sitting under a heading that promises the reader where to go
  // next. It was the most literal dead end on the site: the section whose whole
  // job is onward navigation, rendering a paragraph about our coverage.
  //
  // A person who reads "nothing is linked to Welding yet" does not want an
  // explanation. They want the other welding-adjacent things we do hold, so the
  // caller passes the category and the empty state opens it.
  if (types.length === 0) {
    if (!emptyText) return null;
    return (
      <div data-testid="related-empty" className="flex flex-col items-start gap-2">
        <p className="text-sm text-muted">{emptyText}</p>
        {emptyHref && (
          <Link
            href={emptyHref}
            data-testid="related-empty-next"
            className="text-sm font-display font-bold text-amber-700 hover:text-amber-600"
          >
            {emptyLabel || "Browse everything we have researched"} →
          </Link>
        )}
      </div>
    );
  }

  return (
    <div data-testid="related-entities" className="flex flex-col gap-5">
      {types.map((type) => (
        <section key={type}>
          <h3 className="text-[11px] uppercase tracking-widest text-muted mb-2">
            {TYPE_LABELS[type] || type}{" "}
            <span className="text-stone-400">({grouped[type].length})</span>
          </h3>
          <div className="flex flex-wrap gap-2">
            {grouped[type].slice(0, max).map((e) => (
              <Link
                key={e.global_entity_id}
                href={hrefFor(e)}
                data-testid="related-link"
                title={`${e.canonical_name} — linked by ${VIA(e._via)}`}
                className="chip hover:bg-stone-100 transition-colors"
              >
                {e.canonical_name}
                <span className="ml-1.5 text-[10px] text-stone-400">{VIA(e._via)}</span>
              </Link>
            ))}
            {grouped[type].length > max && (
              <span className="chip text-stone-400">+{grouped[type].length - max} more</span>
            )}
          </div>
        </section>
      ))}
    </div>
  );
}

export function RelatedSourceSummary({ grouped }) {
  const packages = [
    ...new Set(
      Object.values(grouped || {}).flat().map((e) => e.source_package).filter(Boolean)
    ),
  ].sort();
  if (packages.length === 0) return null;
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <span className="text-[11px] text-muted">Researched by:</span>
      {packages.map((p) => <SourceBadge key={p} sourcePackage={p} />)}
    </div>
  );
}
