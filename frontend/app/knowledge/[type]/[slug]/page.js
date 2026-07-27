// Knowledge detail — Platform v3.0, Step 3, Priorities 3, 4 and 5.
//
// ONE ROUTE, TWO NAMESPACES, NO DUPLICATION
// -----------------------------------------
// This route already existed, backed by lib/static-knowledge.js (7 plural types,
// 56 paths). Step 3 adds the knowledge graph under SINGULAR type slugs
// (`/knowledge/skill/welding`, `/knowledge/scheme/pmegp`). The two namespaces do
// not overlap, so the existing static pages keep working unchanged while every
// graph entity gains a detail page — rather than a second detail route the brief
// rules out.
//
// The graph branch serves Priority 3 (business), 4 (scheme) and 5 (skill) from one
// component, because they differ only in which attributes matter and which related
// types lead the page. Three near-identical pages would have drifted within a month.
import { notFound } from "next/navigation";
import Link from "next/link";
import AppNavbar from "@/components/AppNavbar";
import { getAllKnowledgeItems, getKnowledgeItem, knowledgeLabels } from "@/lib/static-knowledge";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";
import {
  TYPE_BY_URL,
  getEntityBySlug,
  getEntityDetail,
  getRelatedByType,
  hrefFor,
} from "@/lib/knowledge";
import EntityHeader from "@/components/knowledge/EntityHeader";
import AttributeGrid, { isPresent } from "@/components/knowledge/AttributeGrid";
import RelatedEntities, { RelatedSourceSummary } from "@/components/knowledge/RelatedEntities";
import KnowledgeEmptyState from "@/components/knowledge/KnowledgeEmptyState";

export const revalidate = 300;

// Only the static pages are pre-rendered. Graph entities are served on demand:
// pre-building 647 of them at deploy time would tie the build to a database that
// is not yet deployed.
export function generateStaticParams() {
  return getAllKnowledgeItems().map((item) => ({ type: item.type, slug: item.slug }));
}

export async function generateMetadata({ params }) {
  if (TYPE_BY_URL[params.type]) {
    const entity = await getEntityBySlug(params.type, params.slug);
    if (!entity) return {};
    return buildBaseMetadata({
      title: `${entity.canonical_name} | ValueWeave Knowledge`,
      description: `Researched ${entity.entity_type} from ${entity.source_package}, with its linked skills, schemes, districts and businesses.`,
      alternates: { canonical: `${BASE_URL}/knowledge/${params.type}/${params.slug}` },
    });
  }
  const item = getKnowledgeItem(params.type, params.slug);
  if (!item) return {};
  return buildBaseMetadata({
    title: `${item.name} | ValueWeave Knowledge Layer`,
    description: item.summary || item.description || item.purpose || item.overview || "",
    alternates: { canonical: `${BASE_URL}/knowledge/${params.type}/${params.slug}` },
  });
}

// ─── Per-type attribute maps ────────────────────────────────────────────────
// Column names come from knowledge_sync/config.py TABLE_SPECS. A column that is
// empty or holds a sentinel is skipped by AttributeGrid rather than rendered.
const ATTRIBUTES = {
  BusinessOpportunity: [
    ["investment_range", "Investment range"],
    ["minimum_investment", "Minimum investment"],
    ["working_capital_need", "Working capital"],
    ["employment_generation", "Employment generated"],
    ["difficulty", "Difficulty"],
    ["risk_level", "Risk level"],
    ["technology_level", "Technology level"],
    ["ai_readiness", "AI readiness"],
    ["profitability_outlook", "Profitability outlook"],
    ["udyam_classification", "Udyam classification"],
    ["ideal_target_audience", "Best suited to"],
  ],
  GovernmentScheme: [
    ["ministry", "Ministry"],
    ["department", "Department"],
    ["government_level", "Level"],
    ["launch_year", "Launched"],
    ["financial_assistance", "Financial assistance"],
    ["subsidy_component", "Subsidy"],
    ["loan_support", "Loan support"],
    ["coverage", "Coverage"],
    ["application_mode", "How to apply"],
    ["status", "Status"],
  ],
  Skill: [
    ["difficulty_level", "Difficulty"],
    ["nsqf_level", "NSQF level"],
    ["learning_duration", "Typical duration"],
    ["demand_level", "Demand"],
    ["automation_risk", "Automation risk"],
    ["ai_augmentation_level", "AI augmentation"],
    ["future_demand", "Future demand"],
    ["self_employment_score", "Self-employment score"],
    ["startup_opportunity", "Startup opportunity"],
  ],
  District: [
    ["district_headquarters", "Headquarters"],
    ["population", "Population"],
    ["area_sq_km", "Area (km²)"],
    ["density_per_sq_km", "Density / km²"],
    ["literacy_rate_pct", "Literacy"],
    ["urban_pct", "Urban share"],
    ["mandal_count", "Mandals"],
    ["sex_ratio", "Sex ratio"],
  ],
  Industry: [
    ["category_group", "Group"],
    ["capital_intensity", "Capital intensity"],
    ["skill_intensity", "Skill intensity"],
    ["typical_udyam_class", "Typical Udyam class"],
    ["nic_section_hint", "NIC section"],
  ],
  Crop: [
    ["season", "Season"],
    ["duration_days", "Duration (days)"],
    ["water_requirement_mm", "Water requirement (mm)"],
    ["soil_type_preferred", "Preferred soil"],
    ["rainfall_mm", "Rainfall (mm)"],
    ["avg_yield_tons_per_ha", "Average yield (t/ha)"],
    ["major_districts", "Major districts"],
  ],
  MSME: [
    ["udyam_classification", "Udyam classification"],
    ["investment_range", "Investment range"],
    ["employment_generation", "Employment generated"],
    ["risk_level", "Risk level"],
    ["profitability_outlook", "Profitability outlook"],
  ],
};

// Which related types lead the page, per the brief's per-priority lists.
const LEAD_RELATED = {
  BusinessOpportunity: ["Skill", "Certification", "GovernmentScheme", "Industry", "Market", "District", "MSME"],
  GovernmentScheme: ["BusinessOpportunity", "MSME", "Skill", "District", "Crop", "FinancialInstitution"],
  Skill: ["TrainingProvider", "Certification", "BusinessOpportunity", "Industry", "GovernmentScheme", "MSME"],
  District: ["Industry", "BusinessOpportunity", "MSME", "Institution", "GovernmentScheme", "Crop"],
};

const DESCRIPTION_KEYS = ["description", "objective", "benefit_summary", "scientific_name"];

export default async function KnowledgeDetailPage({ params }) {
  if (TYPE_BY_URL[params.type]) return <GraphDetail params={params} />;

  const item = getKnowledgeItem(params.type, params.slug);
  if (!item) notFound();
  return <StaticDetail item={item} type={params.type} />;
}

// ─── Graph-backed detail ────────────────────────────────────────────────────
async function GraphDetail({ params }) {
  const entity = await getEntityBySlug(params.type, params.slug);

  if (!entity) {
    return (
      <>
        <AppNavbar />
        <main className="max-w-4xl mx-auto px-4 sm:px-6 py-10 flex flex-col gap-4">
          <Link href="/knowledge" className="text-[12px] text-muted hover:text-ink w-fit">
            ← Knowledge Explorer
          </Link>
          <KnowledgeEmptyState reason="SCHEMA_UNREACHABLE" entityLabel="record" />
        </main>
      </>
    );
  }

  const [detail, related] = await Promise.all([
    getEntityDetail(entity),
    getRelatedByType(entity.global_entity_id),
  ]);

  const fields = ATTRIBUTES[entity.entity_type] || [];
  const lead = LEAD_RELATED[entity.entity_type];
  const description = DESCRIPTION_KEYS.map((k) => detail?.[k]).find(isPresent);
  const portal = detail?.official_portal;

  return (
    <>
      <AppNavbar />
      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-8 flex flex-col gap-7">
        <EntityHeader entity={entity} detail={detail} />

        {description && (
          <p data-testid="entity-description" className="text-[15px] text-ink leading-relaxed">
            {description}
          </p>
        )}

        {fields.length > 0 && detail && (
          <section className="card-base p-5" data-testid="entity-attributes">
            <h2 className="font-display font-bold text-ink mb-4">Details</h2>
            <AttributeGrid fields={fields} row={detail} />
          </section>
        )}

        {isPresent(portal) && String(portal).startsWith("http") && (
          <a href={portal} target="_blank" rel="noopener noreferrer"
             data-testid="entity-portal" className="btn-primary w-fit">
            Apply on the official portal ↗
          </a>
        )}

        <section data-testid="entity-related" className="card-base p-5 flex flex-col gap-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="font-display font-bold text-ink">Connected knowledge</h2>
            <RelatedSourceSummary grouped={related} />
          </div>
          <RelatedEntities
            grouped={related}
            only={lead}
            emptyText={
              "Nothing in the knowledge graph links to this record yet. That is a gap in " +
              "our relationship coverage, not a statement that no connection exists."
            }
          />
          {lead && <RelatedEntities grouped={related} exclude={lead} max={8} />}
        </section>

        <NextSteps entity={entity} related={related} />
      </main>
    </>
  );
}

// The brief's navigation loop, made explicit: every detail page offers the next
// hop rather than leaving the user to find one.
function NextSteps({ entity, related }) {
  const first = (type) => (related?.[type] || [])[0];
  const suggestions = [
    ["Skill", "Explore a required skill"],
    ["GovernmentScheme", "See a supporting scheme"],
    ["District", "Open a district"],
    ["BusinessOpportunity", "See a related business"],
  ]
    .map(([type, label]) => [first(type), label])
    .filter(([e]) => e && e.entity_type !== entity.entity_type);

  if (suggestions.length === 0) return null;
  return (
    <nav data-testid="next-steps" className="flex flex-wrap gap-2 pb-4">
      {suggestions.slice(0, 3).map(([e, label]) => (
        <Link key={e.global_entity_id} href={hrefFor(e)} className="btn-secondary text-sm">
          {label}: {e.canonical_name} →
        </Link>
      ))}
      <Link href="/knowledge" className="btn-secondary text-sm">Browse all knowledge →</Link>
    </nav>
  );
}

// ─── Static detail (unchanged behaviour, preserved) ─────────────────────────
function valueToText(value) {
  if (Array.isArray(value)) return value.join(", ");
  if (value && typeof value === "object") return JSON.stringify(value);
  return value;
}

function StaticDetail({ item, type }) {
  const typeLabel = knowledgeLabels[type] || "Knowledge";
  const entries = Object.entries(item).filter(([key]) => !["slug", "name"].includes(key));
  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <main>
        <section className="relative overflow-hidden bg-ink px-4 sm:px-6 py-14">
          <div className="absolute -top-24 -right-24 w-80 h-80 rounded-full bg-amber-500/20 blur-3xl" />
          <div className="absolute -bottom-24 -left-24 w-96 h-96 rounded-full bg-teal-500/20 blur-3xl" />
          <div className="relative max-w-4xl mx-auto text-center">
            <span className="chip bg-amber-500/20 text-amber-300 border border-amber-500/30 mb-4">{typeLabel}</span>
            <h1 className="font-display font-extrabold tracking-tight text-3xl sm:text-4xl md:text-5xl text-white leading-tight mb-4">{item.name}</h1>
            <p className="text-white/65 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
              {item.summary || item.description || item.purpose || item.overview || "Static knowledge preview for the ValueWeave ecosystem."}
            </p>
          </div>
        </section>

        <section className="max-w-5xl mx-auto px-4 sm:px-6 py-12 pb-20">
          <div className="flex justify-center mb-8">
            <Link href="/knowledge" className="btn-secondary text-sm">
              Browse the researched knowledge base →
            </Link>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            {entries.map(([key, value]) => (
              <div key={key} className="card-base p-5">
                <p className="text-[11px] uppercase tracking-wider text-stone-400 font-display font-bold mb-2">{key.replace(/([A-Z])/g, " $1")}</p>
                {Array.isArray(value) ? (
                  <div className="flex flex-wrap gap-2">
                    {value.map((entry) => <span key={entry} className="chip bg-stone-50 text-stone-600 border border-stone-100">{entry}</span>)}
                  </div>
                ) : (
                  <p className="text-sm text-muted leading-relaxed">{valueToText(value)}</p>
                )}
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
