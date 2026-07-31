// Industrial scaling module — Platform v3.0, Step 4.
//
// One card here turned out to be live all along. Package001_Geography holds 29
// ExportCountry entities — the destinations researched businesses already sell
// to — and until Step 4 no route in the application could reach them: they were
// missing from `TYPE_BY_URL`, so `hrefFor()` sent them to a search box.
//
// Automation, robotics and quality remain unavailable. Business rows carry
// `automation_level` and `ai_readiness` as attributes, which is a property of a
// business, not an automation catalogue — the difference matters and the
// dependency text says so rather than stretching the data to fit the card.
import ModuleDashboard from "@/components/platform/ModuleDashboard";
import { typeCounts } from "@/lib/knowledge";

export default async function ScaleSections() {
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
      emoji: "🌍",
      title: "Export destinations",
      ...live(
        "ExportCountry",
        "/knowledge?type=export",
        "Export destinations",
        "Countries and regions researched businesses already export to, linked back to those businesses."
      ),
    },
    {
      emoji: "🛒",
      title: "Market channels",
      ...live(
        "Market",
        "/knowledge?type=market",
        "Market channels",
        "Where researched businesses sell — marketplaces, mandis, institutional buyers."
      ),
    },
    {
      emoji: "🏦",
      title: "Capital sources",
      ...live(
        "FinancialInstitution",
        "/knowledge?type=bank",
        "Financial institutions",
        "Banks, NBFCs and the kinds of investor that fund businesses like these."
      ),
    },
    {
      emoji: "🤖",
      title: "Automation & robotics",
      description: "Upgrade paths from manual operation to automated production.",
      status: "NO_DATA_SOURCE",
      dependency:
        "No package holds automation vendors or upgrade paths. Business rows carry " +
        "an `automation_level` and `ai_readiness` rating, which describes a business " +
        "rather than the equipment that would change it.",
    },
  ];

  return (
    <ModuleDashboard
      primaryHref="/knowledge?type=export"
      primaryLabel="Browse export destinations"
      dependency={
        "Quality systems, ERP, logistics and energy have no source data in any " +
        "package. The parts of scaling that are researched — export destinations, " +
        "market channels and capital sources — are browsable above."
      }
      roadmap={[
        "Define the operating maturity ladder from local production to competitive manufacturing.",
        "Map scale resources to quality, logistics, energy, ERP, export, automation, and robotics needs.",
        "Connect mature businesses back into the ecosystem as mentors, suppliers, and local anchors.",
      ]}
      capabilities={[
        { label: "Export destinations", status: counts.ExportCountry ? "LIVE" : "NOT_AVAILABLE_YET", href: "/knowledge?type=export", count: counts.ExportCountry },
        { label: "Market channels", status: counts.Market ? "LIVE" : "NOT_AVAILABLE_YET", href: "/knowledge?type=market", count: counts.Market },
        { label: "Capital sources", status: counts.FinancialInstitution ? "LIVE" : "NOT_AVAILABLE_YET", href: "/knowledge?type=bank", count: counts.FinancialInstitution },
        { label: "Automation", dependency: "No automation vendor or upgrade-path data in any package." },
        { label: "Robotics", dependency: "No robotics data in any package." },
        { label: "ERP", dependency: "No software or systems data in any package." },
        { label: "Quality", dependency: "We list certifications you can earn, but not quality systems for a business." },
        { label: "Logistics", dependency: "No carrier, route or freight data in any package." },
        { label: "Energy", dependency: "No tariff or renewable-capacity data in any package." },
      ]}
      cards={cards}
    />
  );
}
