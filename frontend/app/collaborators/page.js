import { getCollaborators } from "@/lib/collab";
import { buildBaseMetadata, breadcrumbJsonLd, BASE_URL } from "@/lib/seo";
import AppNavbar from "@/components/AppNavbar";
import CollaboratorsClient from "@/components/CollaboratorsClient";

export const revalidate = 120;

export const metadata = buildBaseMetadata({
  title: "Find Collaborators & Co-founders — Telangana & Andhra Pradesh | ValueWeave",
  description:
    "Browse builders, innovators, and partners open to collaborate across Telangana and Andhra Pradesh districts — matched by archetype, founder role, sector, and budget.",
  alternates: { canonical: `${BASE_URL}/collaborators` },
});

export default async function CollaboratorsPage() {
  const collaborators = await getCollaborators({ limit: 48 });
  const breadcrumbs = [
    { name: "Home", url: BASE_URL },
    { name: "Collaborators", url: `${BASE_URL}/collaborators` },
  ];

  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd(breadcrumbs)) }} />
      <CollaboratorsClient collaborators={collaborators} />
    </div>
  );
}
