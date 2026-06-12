import { getAllArticles } from "@/lib/mdx";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";
import AppNavbar from "@/components/AppNavbar";
import { ResearchHubClient } from "./ResearchHubClient";

export const metadata = buildBaseMetadata({
  title: "Research Hub — Business Opportunity Research for Bharat | ValueWeave",
  description:
    "In-depth research on local business opportunities, market analysis, investment guides, and district-level insights across Telangana and Andhra Pradesh.",
  alternates: { canonical: `${BASE_URL}/research` },
});

export default function ResearchPage() {
  const articles = getAllArticles();
  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <ResearchHubClient articles={articles} />
    </div>
  );
}
