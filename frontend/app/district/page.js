import { buildBaseMetadata, BASE_URL } from "@/lib/seo";
import { DISTRICTS } from "@/lib/districts-data";
import AppNavbar from "@/components/AppNavbar";
import DistrictIndexClient from "@/components/DistrictIndexClient";

export const metadata = buildBaseMetadata({
  title: "District Opportunity Profiles — Telangana & Andhra Pradesh | ValueWeave",
  description:
    "Explore business opportunities, emerging sectors, government schemes, and collaborator networks for every major district in Telangana and Andhra Pradesh.",
  alternates: { canonical: `${BASE_URL}/district` },
});

export default function DistrictIndexPage() {
  const telangana = DISTRICTS.filter((d) => d.state === "Telangana");
  const ap = DISTRICTS.filter((d) => d.state === "Andhra Pradesh");

  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <DistrictIndexClient telangana={telangana} ap={ap} />
    </div>
  );
}
