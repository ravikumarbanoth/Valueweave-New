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
import KnowledgeCardGrid from "@/components/knowledge/KnowledgeCardGrid";

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
      description: `${entity.canonical_name} — what it involves, and the skills, government schemes, districts and businesses connected to it.`,
      alternates: { canonical: `${BASE_URL}/knowledge/${params.type}/${params.slug}` },
    });
  }
  const item = getKnowledgeItem(params.type, params.slug);
  if (!item) return {};
  return buildBaseMetadata({
    title: `${item.name} | ValueWeave`,
    description: item.summary || item.description || item.purpose || item.overview || "",
    alternates: { canonical: `${BASE_URL}/knowledge/${params.type}/${params.slug}` },
  });
}

// ─── Per-type attribute maps ────────────────────────────────────────────────
// Column names come from knowledge_sync/config.py TABLE_SPECS. A column that is
// empty or holds a sentinel is skipped by AttributeGrid rather than rendered.
const ATTRIBUTES = {
  BusinessOpportunity: [
    ["category_name", "Category"],
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
    ["category_name", "Category"],
    ["short_name", "Also known as"],
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
    ["category_name", "Category"],
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
    ["category_name", "Category"],
    ["season", "Season"],
    ["duration_days", "Duration (days)"],
    ["water_requirement_mm", "Water requirement (mm)"],
    ["soil_type_preferred", "Preferred soil"],
    ["rainfall_mm", "Rainfall (mm)"],
    ["avg_yield_tons_per_ha", "Average yield (t/ha)"],
    ["major_districts", "Major districts"],
  ],
  MSME: [
    ["category_name", "Category"],
    ["udyam_classification", "Udyam classification"],
    ["investment_range", "Investment range"],
    ["employment_generation", "Employment generated"],
    ["risk_level", "Risk level"],
    ["profitability_outlook", "Profitability outlook"],
  ],
};

// Which related types lead the page, per the brief's per-priority lists.
//
// Step 4 widened three of these. A business needs its training providers, raw
// materials and machinery to answer "what would I have to arrange?", and a crop
// needs its soil and climate — all of which the graph held and none of which the
// page surfaced above the fold.
const LEAD_RELATED = {
  BusinessOpportunity: [
    "Skill", "Certification", "TrainingProvider", "GovernmentScheme", "Industry",
    "Market", "District", "MSME", "RawMaterial", "Machinery",
  ],
  GovernmentScheme: ["BusinessOpportunity", "MSME", "Skill", "District", "Crop", "FinancialInstitution"],
  Skill: ["TrainingProvider", "Certification", "BusinessOpportunity", "Industry", "GovernmentScheme", "MSME"],
  District: ["Industry", "BusinessOpportunity", "MSME", "Institution", "GovernmentScheme", "Crop", "TrainingProvider", "Market"],
  Crop: ["District", "Soil", "ClimateZone", "Machinery", "Industry", "GovernmentScheme"],
  MSME: ["Skill", "Industry", "GovernmentScheme", "District", "Market", "RawMaterial"],
  Industry: ["BusinessOpportunity", "MSME", "Skill", "District", "GovernmentScheme"],
};

// ─── Sections the brief asks for that have no source ────────────────────────
//
// Step 4's rule is that a requested section either shows live data or says
// exactly what is missing. These three are asked for by name in the brief and
// cannot be answered from the projection. Rendering them blank, or quietly
// omitting them, would both read as "this entity has none" — which is false.
//
// Every one of them names a file that exists in Git, because that is the real
// state of affairs: the research was done, and `knowledge_sync` does not project
// it. That is a backend scope item, not a frontend gap, and saying so is more
// useful than a shrug.
const UNAVAILABLE_SECTIONS = {
  GovernmentScheme: [
    {
      title: "Who can apply",
      note:
        "We have not published eligibility rules for our schemes yet. Our team has " +
        "gathered them and we are still checking them line by line — getting this " +
        "wrong could cost you an application, so we would rather show nothing than " +
        "show a guess. Use the official portal link above in the meantime.",
    },
    {
      title: "Documents and how to apply",
      note:
        "We have not published the document checklist or step-by-step process yet. " +
        "The official portal link above is the reliable route today.",
    },
  ],
  Skill: [
    {
      title: "What to learn first",
      note:
        "We know how hard each skill is and how long it takes, but not yet what " +
        "order to learn them in. We are working on it — an ordering we guessed at " +
        "would waste your time rather than save it.",
    },
  ],
  BusinessOpportunity: [
    {
      title: "Step-by-step setup",
      note:
        "We have not published a setup checklist for this yet. The investment " +
        "range, working capital and difficulty above are researched; the licences " +
        "and sequence are not.",
    },
  ],
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
              "We have not connected anything to this yet. It is a gap in our research, " +
              "not a sign that nothing is related."
            }
          />
          {lead && <RelatedEntities grouped={related} exclude={lead} max={8} />}
        </section>

        <UnavailableSections entityType={entity.entity_type} />

        <NextSteps entity={entity} related={related} />
      </main>
    </>
  );
}

// The sections a user is entitled to expect and we cannot fill. Naming them is
// the difference between an incomplete page and a dishonest one.
function UnavailableSections({ entityType }) {
  const sections = UNAVAILABLE_SECTIONS[entityType];
  if (!sections) return null;
  return (
    <section data-testid="entity-unavailable" className="flex flex-col gap-3">
      {sections.map((s) => (
        <div key={s.title}>
          <h3 className="label-display">{s.title}</h3>
          <KnowledgeCardGrid
            status="NO_DATA_SOURCE"
            note={s.note}
            testId={`unavailable-${s.title.split(" ")[0].toLowerCase()}`}
          />
        </div>
      ))}
    </section>
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

// ─── Static detail — preserved for URL stability, demoted in the UI ─────────
//
// Step 4 removed every link into these 56 pages: the homepage featured cards and
// the search results both read the projection now. The routes still resolve
// because they are indexed URLs and breaking them to make a point about data
// quality would be a worse trade than leaving them reachable.
//
// What changed is the framing. A page reached from a search engine now opens
// with a banner saying it is editorial, unsourced, and superseded — and links to
// the researched equivalent. Silently serving 2023 hand-written JSON as if it
// were the knowledge base is the exact confusion this step exists to end.
const STATIC_TYPE_HINT = {
  districts: "district",
  industries: "industry",
  skills: "skill",
  schemes: "scheme",
  manufacturing: "business",
  training: "provider",
  products: null,
};

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
          <div
            data-testid="static-superseded-notice"
            className="rounded-2xl border border-dashed border-amber-200 bg-amber-50 p-5 mb-8"
          >
            <p className="font-display font-bold text-sm text-ink">
              An early preview, since replaced by better information
            </p>
            <p className="text-xs text-muted mt-1.5 leading-relaxed max-w-2xl">
              This was written early on, before our research team had covered this
              area. We now have far more on the same subject, checked against official
              public sources. This page is kept only so older links still work.
            </p>
            <div className="flex flex-wrap gap-2 mt-4">
              {STATIC_TYPE_HINT[type] && (
                <Link href={`/knowledge?type=${STATIC_TYPE_HINT[type]}`} className="btn-primary text-sm">
                  Researched {typeLabel.toLowerCase()}s →
                </Link>
              )}
              <Link
                href={`/knowledge?q=${encodeURIComponent(item.name || "")}`}
                className="btn-secondary text-sm"
              >
                Search for “{item.name}” →
              </Link>
            </div>
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
