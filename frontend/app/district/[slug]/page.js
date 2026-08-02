import { notFound } from "next/navigation";
import { getAllDistrictSlugs, getDistrictBySlug } from "@/lib/districts-data";
import { getAllArticles } from "@/lib/mdx";
import { buildDistrictMetadata, localBusinessJsonLd, breadcrumbJsonLd, pageSummaryJsonLd, BASE_URL } from "@/lib/seo";
import { getDistrictRelatedLinks } from "@/lib/internal-links";
import { DistrictProfile } from "@/components/district/DistrictProfile";
import SnapshotPanel from "@/components/geo/SnapshotPanel";
import AppNavbar from "@/components/AppNavbar";
import PageTracker from "@/components/PageTracker";
import RequestContentWidget from "@/components/RequestContentWidget";
import DistrictIntelligencePanel from "@/components/knowledge/DistrictIntelligencePanel";
import { getDistrictKnowledge, resolveTerms } from "@/lib/knowledge";

// Phase 5 — researched knowledge for this district.
//
// Resolution goes through the Step 0 district crosswalk, which reaches 100%: all
// 14 editorial districts plus the idea-library variants map to a graph District,
// including the curated cases (Anantapur -> Ananthapuramu, Nellore -> Sri Potti
// Sriramulu Nellore, and Vijayawada -> NTR, which maps a city to its district).
async function loadDistrictKnowledge(districtName) {
  const { resolved } = await resolveTerms("district", [districtName]);
  const hit = resolved[0];
  if (!hit) {
    // See the note in app/districts/[slug]/page.js — same condition, same
    // reasoning. How we match a name to a district is not the reader's problem.
    return {
      grouped: {},
      status: "NO_DATA_SOURCE",
      note: `We are connecting local businesses, schemes and training to ${districtName} now. The profile above is still accurate — and the districts we have finished are worth a look.`,
    };
  }
  return { grouped: await getDistrictKnowledge(hit.global_entity_id), status: null, note: null };
}

// See app/ai/page.js for the full reasoning. Short version: this page reads the
// projection, the sync writes to it after the build, and without a revalidate the
// 14 prerendered district pages would be frozen at build time. They do refresh
// today, but only because the shared Footer's settings cache pulls every segment
// down to 60s. Declared here so it is this page's own behaviour and not a side
// effect of an unrelated component.
export const revalidate = 300;

export async function generateStaticParams() {
  return getAllDistrictSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }) {
  const district = getDistrictBySlug(params.slug);
  if (!district) return {};
  return buildDistrictMetadata(district);
}

export default async function DistrictPage({ params }) {
  const district = getDistrictBySlug(params.slug);
  if (!district) notFound();

  // Additive: the editorial profile below is unchanged. This returns an empty
  // grouping when the projection is absent, so the page renders identically
  // today and gains content once the sync has run — within one revalidate
  // window, not at the next deploy. That distinction is the whole reason for the
  // `export const revalidate` above.
  const knowledge = await loadDistrictKnowledge(district.name);

  const allArticles = getAllArticles();
  const relatedLinks = getDistrictRelatedLinks(district, allArticles);
  const relatedArticles = allArticles.filter((a) =>
    district.relatedArticleSlugs.includes(a.slug)
  );

  const breadcrumbs = [
    { name: "Home", url: BASE_URL },
    { name: "Districts", url: `${BASE_URL}/district` },
    { name: district.name, url: `${BASE_URL}/district/${district.slug}` },
  ];

  const summary = {
    "Key Takeaways": district.profileSummary,
    "Who should read this": `Entrepreneurs, students, MSMEs, and collaborators exploring business potential in ${district.name}.`,
    "Investment Range": "Varies by sector and business model",
    "District Relevance": `${district.name}, ${district.state}`,
    "Business Potential": `Use this page to evaluate priority sectors, schemes, demand signals, and collaborator opportunities in ${district.name}.`,
  };

  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <PageTracker
        pageType="district"
        slug={district.slug}
        title={district.name}
        district={district.name}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify([
            localBusinessJsonLd(district),
            breadcrumbJsonLd(breadcrumbs),
            pageSummaryJsonLd({
              url: `${BASE_URL}/district/${district.slug}`,
              title: `Business Opportunities in ${district.name}`,
              summary: district.profileSummary,
              about: district.name,
              keywords: [district.name, district.state, "district intelligence", "business opportunities"],
            }),
          ]),
        }}
      />
      <div className="max-w-5xl mx-auto px-4 pt-6">
        <SnapshotPanel title="District Snapshot" items={summary} />
      </div>
      <DistrictProfile
        district={district}
        relatedLinks={relatedLinks}
        relatedArticles={relatedArticles}
      />
      {/* ── Phase 5: researched knowledge, BELOW the editorial profile ──
          lib/districts-data.js narrative is better writing than anything the graph
          generates. The graph contributes sourced facts, clearly labelled as such,
          and neither replaces the other. */}
      <div className="max-w-5xl mx-auto px-4 pb-4">
        <DistrictIntelligencePanel
          testId="district-intelligence"
          districtName={district.name}
          grouped={knowledge.grouped}
          status={knowledge.status}
          note={knowledge.note}
        />
      </div>

      <div className="max-w-5xl mx-auto px-4 pb-10">
        <div className="flex items-center justify-between pt-6 border-t border-stone-200 mt-2">
          <p className="text-[13px] text-stone-400">Missing something about {district.name}?</p>
          <RequestContentWidget
            defaultType="district"
            district={district.name}
            prefillTitle={`${district.name} District Report`}
            buttonLabel="Request District Report"
            compact
          />
        </div>
      </div>
    </div>
  );
}
