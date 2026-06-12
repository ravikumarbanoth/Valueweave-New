import { getCombinedArticles } from "@/lib/research";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";
import AppNavbar from "@/components/AppNavbar";
import { ResearchHubClient } from "./ResearchHubClient";

// ISR: newly published database articles appear within 2 minutes
// without a redeploy (and immediately on first request after expiry).
export const revalidate = 120;

export const metadata = buildBaseMetadata({
  title: "Research Hub — Business Opportunity Research for Bharat | ValueWeave",
  description:
    "In-depth research on local business opportunities, market analysis, investment guides, and district-level insights across Telangana and Andhra Pradesh.",
  alternates: { canonical: `${BASE_URL}/research` },
});

export default async function ResearchPage() {
  const articles = await getCombinedArticles();
  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <ResearchHubClient articles={articles} />
    </div>
  );
}
