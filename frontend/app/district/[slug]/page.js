import { notFound } from "next/navigation";
import { getAllDistrictSlugs, getDistrictBySlug } from "@/lib/districts-data";
import { getAllArticles } from "@/lib/mdx";
import { buildDistrictMetadata, localBusinessJsonLd, breadcrumbJsonLd, BASE_URL } from "@/lib/seo";
import { getDistrictRelatedLinks } from "@/lib/internal-links";
import { DistrictProfile } from "@/components/district/DistrictProfile";
import AppNavbar from "@/components/AppNavbar";

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
    </div>
  );
}
