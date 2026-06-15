import { notFound } from "next/navigation";
import { getAllDistrictSlugs, getDistrictBySlug } from "@/lib/districts-data";
import { getAllArticles } from "@/lib/mdx";
import { buildDistrictMetadata, localBusinessJsonLd, breadcrumbJsonLd, BASE_URL } from "@/lib/seo";
import { getDistrictRelatedLinks } from "@/lib/internal-links";
import { DistrictProfile } from "@/components/district/DistrictProfile";
import AppNavbar from "@/components/AppNavbar";
import PageTracker from "@/components/PageTracker";
import RequestContentWidget from "@/components/RequestContentWidget";

export async function generateStaticParams() {
  return getAllDistrictSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }) {
  const district = getDistrictBySlug(params.slug);
  if (!district) return {};
  return buildDistrictMetadata(district);
}

export default function DistrictPage({ params }) {
  const district = getDistrictBySlug(params.slug);
  if (!district) notFound();

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
          __html: JSON.stringify([localBusinessJsonLd(district), breadcrumbJsonLd(breadcrumbs)]),
        }}
      />
      <DistrictProfile
        district={district}
        relatedLinks={relatedLinks}
        relatedArticles={relatedArticles}
      />
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
