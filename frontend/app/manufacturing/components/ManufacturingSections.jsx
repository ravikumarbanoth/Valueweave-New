// Manufacturing module — Platform v3.0, Step 4.
//
// "Product Discovery" and "Machinery" were both marked "Coming Soon" while
// Package004 held 45 researched business opportunities and Packages 005 and 008
// together held 69 machinery records. Those two cards are now the module.
//
// Factory planning, production and compliance stay unavailable. They are not
// missing wiring — no package holds a layout, a throughput model or a compliance
// checklist, and inventing one would be exactly the fabrication this platform
// refuses everywhere else.
import ModuleDashboard from "@/components/platform/ModuleDashboard";
import { typeCounts } from "@/lib/knowledge";

export default async function ManufacturingSections() {
  const counts = await typeCounts();
  const live = (type, href, label, description) =>
    (counts[type] || 0) > 0
      ? { status: "LIVE", href, count: counts[type], description }
      : {
          status: "NOT_AVAILABLE_YET",
          dependency: `We have researched ${label.toLowerCase()} — this section is still being connected. Check back soon.`,
          description,
        };

  const cards = [
    {
      emoji: "📦",
      title: "Product discovery",
      ...live(
        "BusinessOpportunity",
        "/knowledge?type=business",
        "Business opportunities",
        "Researched opportunities with investment range, working capital, employment, difficulty and risk."
      ),
    },
    {
      emoji: "⚙️",
      title: "Machinery",
      ...live(
        "Machinery",
        "/knowledge?type=machinery",
        "Machinery records",
        "Equipment used by the businesses and farms we have researched, with what each one is for."
      ),
    },
    {
      emoji: "🧱",
      title: "Raw materials",
      ...live(
        "RawMaterial",
        "/knowledge?type=material",
        "Raw materials",
        "Inputs the researched businesses consume, linked back to those businesses."
      ),
    },
    {
      emoji: "🏗️",
      title: "Factory planning",
      description: "Space, layout, compliance sequence, and setup order.",
      status: "NO_DATA_SOURCE",
      dependency:
        "Factory layouts, land requirements and the order to get licences in are being " +
        "researched now. Each business idea already tells you the money needed to " +
        "start.",
    },
  ];

  return (
    <ModuleDashboard
      primaryHref="/knowledge?type=business"
      primaryLabel="Browse opportunities"
      dependency={
        "Production planning, supplier search and licence tracking are on the way. " +
        "Everything they will work on is already here: business ideas, machinery, " +
        "raw materials and places to sell."
      }
      roadmap={[
        "Gather what a manufacturer needs in one place: products, machinery, suppliers, raw materials and licences.",
        "Connect manufacturing guides to district industries and readiness pathways.",
        "Build day-to-day tools for running a unit, once we are sure the underlying research is right.",
      ]}
      capabilities={[
        { label: "Business opportunities", status: counts.BusinessOpportunity ? "LIVE" : "NOT_AVAILABLE_YET", href: "/knowledge?type=business", count: counts.BusinessOpportunity },
        { label: "Machinery", status: counts.Machinery ? "LIVE" : "NOT_AVAILABLE_YET", href: "/knowledge?type=machinery", count: counts.Machinery },
        { label: "Raw materials", status: counts.RawMaterial ? "LIVE" : "NOT_AVAILABLE_YET", href: "/knowledge?type=material", count: counts.RawMaterial },
        { label: "Market channels", status: counts.Market ? "LIVE" : "NOT_AVAILABLE_YET", href: "/knowledge?type=market", count: counts.Market },
        { label: "MSMEs", status: counts.MSME ? "LIVE" : "NOT_AVAILABLE_YET", href: "/knowledge?type=msme", count: counts.MSME },
        { label: "Suppliers", dependency: "Raw materials are researched; the firms that supply them are not." },
        { label: "Factory planning", dependency: "Factory layouts and land requirements are being researched now." },
        { label: "Production", dependency: "Output rates, staffing and quality checks are being researched now." },
        { label: "Compliance", dependency: "Licences and inspections are being researched now." },
      ]}
      cards={cards}
    />
  );
}
