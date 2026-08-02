// Knowledge Explorer — Platform v3.0, Step 3, Priority 2.
//
// The browse surface for everything Packages001–008 researched. It is a NEW route
// (`/knowledge` had only `[type]/[slug]` before) rather than a second search page:
// KnowledgeSearch stays the way you find a known thing, this is how you browse a
// domain you do not yet know the vocabulary for.
//
// Server component. One `typeCounts()` query for the index, one `listEntities()`
// for a browse page. Cached for five minutes because the projection changes only
// when a package is released.
import Link from "next/link";
import AppNavbar from "@/components/AppNavbar";
import {
  listEntities,
  typeCounts,
  knowledgeAvailable,
  hrefFor,
  URL_BY_TYPE,
  TYPE_BY_URL,
  PACKAGE_LABELS,
} from "@/lib/knowledge";
import SourceBadge from "@/components/knowledge/SourceBadge";
import ConfidenceBadge from "@/components/knowledge/ConfidenceBadge";
import KnowledgePagination from "@/components/knowledge/KnowledgePagination";
import KnowledgeEmptyState from "@/components/knowledge/KnowledgeEmptyState";
import TrustPanel from "@/components/knowledge/TrustPanel";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";

export const revalidate = 300;

export const metadata = buildBaseMetadata({
  title: "Knowledge Explorer | ValueWeave",
  description:
    "Find districts, industries, business ideas, skills, government schemes and " +
    "farming information across Telangana and Andhra Pradesh — all checked against " +
    "official public sources.",
  alternates: { canonical: `${BASE_URL}/knowledge` },
});

const PAGE_SIZE = 24;

//: The browse taxonomy — Step 4.
//:
//: This was grouped by "the package that owns each type", with a SourceBadge on
//: every section heading. Three of those headings were wrong, because three types
//: span packages: Industry is 25 rows from Package004, 20 from Package005 and 33
//: from Package008; Machinery is 16 from Package005 and 53 from Package008;
//: FinancialInstitution is 12 from Package007 and 9 from Package008. Labelling
//: the section with one package told the reader something false about two thirds
//: of what was in it.
//:
//: Grouping is by domain now, and provenance stays where it is accurate: on each
//: entity's own card, which carries the package that actually produced that row.
//: `packages` lists every contributor so the section can still say where its
//: content came from without pretending to a single owner.
//:
//: Step 4 also added five types that had no route in at all — ExportCountry,
//: Soil, ClimateZone, State and Country, 50 entities between them.
const SECTIONS = [
  {
    domain: "Places",
    packages: ["Package001_Geography"],
    types: [["District", "Districts"], ["State", "States"], ["Country", "Countries"]],
  },
  {
    domain: "Business and industry",
    packages: ["Package004_Industries", "Package008_MSME", "Package005_Agriculture"],
    types: [
      ["Industry", "Industries"],
      ["BusinessOpportunity", "Business opportunities"],
      ["MSME", "MSMEs"],
    ],
  },
  {
    domain: "Skills and training",
    packages: ["Package006_Skills_and_Training"],
    types: [
      ["Skill", "Skills"],
      ["Certification", "Certifications"],
      ["TrainingProvider", "Training providers"],
    ],
  },
  {
    domain: "Agriculture and land",
    packages: ["Package005_Agriculture"],
    types: [["Crop", "Crops"], ["Soil", "Soil types"], ["ClimateZone", "Climate zones"]],
  },
  {
    domain: "Support and capital",
    packages: ["Package007_Government_Schemes", "Package008_MSME"],
    types: [
      ["GovernmentScheme", "Government schemes"],
      ["FinancialInstitution", "Financial institutions"],
    ],
  },
  {
    domain: "Inputs and markets",
    packages: ["Package008_MSME", "Package005_Agriculture", "Package001_Geography"],
    types: [
      ["Machinery", "Machinery"],
      ["RawMaterial", "Raw materials"],
      ["Market", "Market channels"],
      ["ExportCountry", "Export destinations"],
    ],
  },
  {
    domain: "Education",
    packages: ["Package002_Education"],
    types: [["Institution", "Institutions"]],
  },
];

export default async function KnowledgeExplorerPage({ searchParams }) {
  const urlType = searchParams?.type || "";
  const entityType = TYPE_BY_URL[urlType] || "";
  const q = (searchParams?.q || "").slice(0, 80);
  const page = Math.max(1, parseInt(searchParams?.page || "1", 10) || 1);

  const availability = await knowledgeAvailable();

  return (
    <>
      <AppNavbar />
      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 flex flex-col gap-6">
        <div>
          <p className="text-[11px] uppercase tracking-widest text-muted">Explore</p>
          <h1 className="font-display font-bold text-2xl sm:text-3xl text-ink">
            {entityType ? BROWSE_LABEL(entityType) : "What would you like to explore?"}
          </h1>
          <p className="text-sm text-muted mt-1 max-w-2xl">
            Districts to build in, businesses you could start, skills worth learning,
            government schemes you may qualify for and crops that grow well here —
            across Telangana and Andhra Pradesh. Everything here was checked against
            an official public source.
          </p>
        </div>

        <SearchBar q={q} urlType={urlType} />

        {!availability.available ? (
          <KnowledgeEmptyState reason={availability.reason} entityLabel="knowledge" />
        ) : entityType ? (
          <BrowseType entityType={entityType} urlType={urlType} q={q} page={page} />
        ) : (
          <TypeIndex q={q} />
        )}
      </main>
    </>
  );
}

function BROWSE_LABEL(entityType) {
  for (const s of SECTIONS) {
    const hit = s.types.find(([t]) => t === entityType);
    if (hit) return hit[1];
  }
  return entityType;
}

function SearchBar({ q, urlType }) {
  return (
    <form action="/knowledge" method="get" data-testid="knowledge-explorer-search"
          className="flex flex-wrap gap-2">
      {urlType && <input type="hidden" name="type" value={urlType} />}
      <input
        name="q"
        defaultValue={q}
        placeholder="Try a district, a skill, or a business idea…"
        aria-label="Search"
        className="input-field flex-1 min-w-[200px]"
      />
      <button type="submit" className="btn-primary">Search</button>
      {(q || urlType) && (
        <Link href="/knowledge" className="btn-secondary">Clear</Link>
      )}
    </form>
  );
}

async function TypeIndex({ q }) {
  const counts = await typeCounts();
  const total = Object.values(counts).reduce((a, b) => a + b, 0);

  return (
    <div className="flex flex-col gap-6">
      <TrustPanel hasUnverified={total > 0} />

      {SECTIONS.map((section) => {
        const live = section.types.filter(([t]) => (counts[t] || 0) > 0);
        if (live.length === 0) return null;
        return (
          <section key={section.domain} data-testid="explorer-section">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <h2 className="font-display font-bold text-ink text-[15px]">{section.domain}</h2>
              {section.packages.map((p) => (
                <SourceBadge key={p} sourcePackage={p} />
              ))}
            </div>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {live.map(([type, label]) => (
                <Link
                  key={type}
                  href={`/knowledge?type=${URL_BY_TYPE[type]}${q ? `&q=${encodeURIComponent(q)}` : ""}`}
                  data-testid="explorer-type-link"
                  className="card-base p-4 hover:border-stone-300 transition-colors"
                >
                  <p className="font-display font-bold text-ink">{label}</p>
                  <p className="text-sm text-muted">{counts[type]} to explore</p>
                </Link>
              ))}
            </div>
          </section>
        );
      })}

      {total === 0 && <KnowledgeEmptyState reason="EMPTY" entityLabel="knowledge" />}
    </div>
  );
}

async function BrowseType({ entityType, urlType, q, page }) {
  const { rows, total } = await listEntities(entityType, { page, pageSize: PAGE_SIZE, q });

  if (rows.length === 0) {
    return (
      <>
        <Link href="/knowledge" className="text-[12px] text-muted hover:text-ink w-fit">
          ← All knowledge
        </Link>
        <KnowledgeEmptyState reason="NO_MATCH" entityLabel={BROWSE_LABEL(entityType).toLowerCase()} query={q} />
      </>
    );
  }

  const unverified = rows.filter((r) => String(r.verification_status || "").includes("NEEDS_REVIEW")).length;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between gap-3">
        <Link href="/knowledge" className="text-[12px] text-muted hover:text-ink">← All knowledge</Link>
        <p className="text-[12px] text-muted" data-testid="browse-count">
          {total} {total === 1 ? "result" : "results"}
          {q ? ` matching “${q}”` : ""}
        </p>
      </div>

      <TrustPanel hasUnverified={unverified > 0} />

      <ul data-testid="browse-list" className="grid gap-3 sm:grid-cols-2">
        {rows.map((e) => (
          <li key={e.global_entity_id}>
            <Link href={hrefFor(e)} data-testid="browse-item"
                  className="card-base p-4 flex flex-col gap-2 h-full hover:border-stone-300 transition-colors">
              <div className="flex items-start justify-between gap-2">
                <span className="font-display font-bold text-ink text-[15px] leading-snug">
                  {e.canonical_name}
                </span>
                <ConfidenceBadge confidence={e.confidence_score} />
              </div>
              <SourceBadge sourcePackage={e.source_package} className="w-fit" />
            </Link>
          </li>
        ))}
      </ul>

      <KnowledgePagination
        page={page}
        pageSize={PAGE_SIZE}
        total={total}
        hrefFor={(p) =>
          `/knowledge?type=${urlType}${q ? `&q=${encodeURIComponent(q)}` : ""}&page=${p}`}
      />
    </div>
  );
}
