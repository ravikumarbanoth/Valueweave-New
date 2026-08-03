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
} from "@/lib/knowledge";
import { searchGrouped, guidance } from "@/lib/search/universal.js";
import { resolveQuery, describeResolution } from "@/lib/search-vocabulary.js";
import SourceBadge from "@/components/knowledge/SourceBadge";
import ConfidenceBadge from "@/components/knowledge/ConfidenceBadge";
import KnowledgePagination from "@/components/knowledge/KnowledgePagination";
import KnowledgeEmptyState from "@/components/knowledge/KnowledgeEmptyState";
import TrustPanel from "@/components/knowledge/TrustPanel";
import LiveSearch from "@/components/search/LiveSearch";
import GroupedResults from "@/components/search/GroupedResults";
import NoResultsGuide from "@/components/search/NoResultsGuide";
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

//: Fewer than this and the page offers guidance as well as results. Not zero:
//: a single row is a coverage gap wearing the costume of an answer.
const THIN_RESULTS = 3;

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
  //: Two characters is `searchKnowledge`'s own floor — below it the ranker
  //: returns nothing, so treating one character as a search would render an
  //: empty result page for someone who is still typing.
  const searching = q.trim().length >= 2;
  const page = Math.max(1, parseInt(searchParams?.page || "1", 10) || 1);

  const availability = await knowledgeAvailable();

  return (
    <>
      <AppNavbar />
      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 flex flex-col gap-6">
        {/* PX Phase 8. The heading did not know a search had happened. Someone
            who typed "Electrician" and pressed Search landed on a page headed
            "What would you like to explore?" above a paragraph inviting them to
            explore — which is what a page looks like when it has ignored you,
            and is exactly what this route did until the search fix. Even now
            that the results are correct, the heading argues with them.

            The invitation is right for someone who arrived with no query and
            wrong for someone who arrived with one. */}
        <div>
          <p className="text-[11px] uppercase tracking-widest text-muted">
            {searching ? "Search results" : "Explore"}
          </p>
          <h1 className="font-display font-bold text-2xl sm:text-3xl text-ink">
            {searching
              ? `“${q}”`
              : entityType
                ? BROWSE_LABEL(entityType)
                : "What would you like to explore?"}
          </h1>
          {!searching && (
            <p className="text-sm text-muted mt-1 max-w-2xl">
              Districts to build in, businesses you could start, skills worth learning,
              government schemes you may qualify for and crops that grow well here —
              across Telangana and Andhra Pradesh. Everything here was checked against
              an official public source.
            </p>
          )}
        </div>

        <SearchBar q={q} urlType={urlType} searching={searching} />

        {/* PRODUCTION BUG, FIXED HERE — SEARCH NEVER RAN
            ------------------------------------------------
            This branch used to read:

                : entityType ? <BrowseType … q={q} …/>
                : <TypeIndex q={q} />

            and neither of those searched. `TypeIndex` ACCEPTED `q` and used
            it for exactly one thing: appending it to the category links. So
            /knowledge?q=electrician — the URL the homepage search box sends
            you to — rendered the category grid, identical to /knowledge with
            no query at all. No results, no "nothing found", no sign the query
            had been received.

            `BrowseType` did search, in the sense that `listEntities` ran
            `ilike '%q%'` on the name. Measured on the real 647 entities that
            gave "electrician" 2 rows, "PMEGP" the margin-money subsidy but
            not the scheme, "AI" 46 rows of which most matched the letters a-i
            inside Painting and Millet, and "electrican" nothing at all.

            `searchKnowledge` — typo tolerance, acronyms, the ranking ladder —
            existed the whole time and had exactly one caller: the client
            component further down the homepage. This page never imported it.

            A query now goes to that one engine whether or not a type filter
            is set. `listEntities` has lost its `q` parameter entirely, so
            there is no second search path left to drift. */}
        {!availability.available ? (
          <KnowledgeEmptyState reason={availability.reason} entityLabel="knowledge" />
        ) : searching ? (
          <SearchResults q={q} entityType={entityType} urlType={urlType} />
        ) : entityType ? (
          <BrowseType entityType={entityType} urlType={urlType} page={page} />
        ) : (
          <TypeIndex />
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

// The plain form became a live one. It is the same control — a box, a Search
// button, and a URL you can share — with a list under it after two characters,
// so trying a second word costs a keystroke instead of a page load.
//
// The type filter is dropped from the box on purpose. A live suggestion
// restricted to one category, on a page whose whole point is that you should
// not have to know the category, is the database asking the question again.
// The filter still applies to the RESULTS below; see SearchResults.
function SearchBar({ q, urlType, searching }) {
  return (
    <div className="flex flex-col gap-2" data-testid="knowledge-explorer-search">
      <LiveSearch
        initialQuery={q}
        size="compact"
        testId="explorer-search"
        label="Search everything we have researched"
        hiddenLabel
        placeholder="A district, a skill, a scheme, a business idea…"
      />
      {(searching || urlType) && (
        <Link href="/knowledge" className="text-[12px] text-muted hover:text-ink w-fit">
          Clear
        </Link>
      )}
    </div>
  );
}

async function TypeIndex() {
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
                  href={`/knowledge?type=${URL_BY_TYPE[type]}`}
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

/**
 * One query, one engine — now over everything, not only the graph.
 *
 * `searchGrouped` is the same ladder in lib/knowledge-search.js (exact,
 * prefix, word, contains, vocabulary expansion, fuzzy, with a floor on
 * substring matching) applied to the union of every source in
 * lib/search/registry.js: the 647 researched entities AND the research
 * articles, which until now the search box could not see at all.
 *
 * Two things changed about what a reader gets:
 *
 *   grouped     nine labelled sections in best-result order, instead of one
 *               flat grid mixing districts, skills, schemes and articles and
 *               asking the reader to sort it.
 *
 *   guided      when nothing matches, `guidance` runs instead of a sentence —
 *               a correction, related rows that actually exist, the terms that
 *               would have worked, and a one-tap request. Never a dead end.
 */
async function SearchResults({ q, entityType, urlType }) {
  const scopeLabel = entityType ? BROWSE_LABEL(entityType).toLowerCase() : "";

  // The type filter is applied AFTER grouping is computed, because a filtered
  // search that finds nothing should still be able to say "there are eleven of
  // these if you drop the filter" — which is the useful thing to say and was
  // impossible when the filter was pushed into the query.
  const { rows, groups } = await searchGrouped(q, { limit: 60, perGroup: 8 });
  const visible = entityType ? rows.filter((r) => r.entity_type === entityType) : rows;

  if (visible.length === 0) {
    const help = await guidance(q);
    return (
      <div className="flex flex-col gap-4">
        <NoResultsGuide guidance={help} query={q} scopeLabel={scopeLabel} />
        {entityType && rows.length > 0 && (
          <Link href={`/knowledge?q=${encodeURIComponent(q)}`}
                data-testid="search-drop-filter"
                className="text-sm font-display font-bold text-amber-700 hover:text-amber-600 w-fit">
            {rows.length} {rows.length === 1 ? "result" : "results"} outside {scopeLabel} — search everything →
          </Link>
        )}
      </div>
    );
  }

  const shown = entityType
    ? [{ id: entityType, label: BROWSE_LABEL(entityType), total: visible.length,
         items: visible.slice(0, 24), best: visible[0]._score }]
    : groups;

  // One result is not "found it", it is "we barely cover this". "Dairy" is the
  // standing example: the graph holds a single dairy-adjacent row, and a page
  // showing only that row tells the reader we have a dairy section when we do
  // not. Below the threshold the guidance renders underneath the results, so
  // the answer is honest AND the reader still has somewhere to go.
  const thin = visible.length < THIN_RESULTS;
  const help = thin
    ? await guidance(q, { exclude: visible.map((r) => r.global_entity_id) })
    : null;

  return (
    <div className="flex flex-col gap-6">
      <Link href="/knowledge" className="text-[12px] text-muted hover:text-ink w-fit">
        ← All knowledge
      </Link>
      <GroupedResults
        groups={shown}
        total={visible.length}
        query={q}
        resolved={describeResolution(resolveQuery(q))}
      />
      {help && (
        <div className="border-t border-stone-200 pt-6" data-testid="thin-results">
          <p className="text-sm text-muted mb-4">
            That is all we have researched on this so far. Here is what is nearby.
          </p>
          <NoResultsGuide guidance={help} query={q} scopeLabel={scopeLabel} mode="thin" />
        </div>
      )}
    </div>
  );
}

async function BrowseType({ entityType, urlType, page }) {
  const { rows, total } = await listEntities(entityType, { page, pageSize: PAGE_SIZE });

  if (rows.length === 0) {
    return (
      <>
        <Link href="/knowledge" className="text-[12px] text-muted hover:text-ink w-fit">
          ← All knowledge
        </Link>
        <KnowledgeEmptyState reason="NO_MATCH" entityLabel={BROWSE_LABEL(entityType).toLowerCase()} />
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
          `/knowledge?type=${urlType}&page=${p}`}
      />
    </div>
  );
}
