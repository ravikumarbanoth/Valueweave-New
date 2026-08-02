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
        "We have not researched who sells automation equipment, or what it costs to " +
        "upgrade. Each business idea does say how much of the work a machine could " +
        "do — but that describes the work, not the machine.",
    },
  ];

  return (
    <ModuleDashboard
      primaryHref="/knowledge?type=export"
      primaryLabel="Browse export destinations"
      dependency={
        "We have not researched quality systems, business software, transport or " +
        "energy yet. The parts of growing a business we have researched — export " +
        "destinations, places to sell, and where the money comes from — are open above."
      }
      roadmap={[
        "Lay out the steps from selling locally to competing with the best manufacturers.",
        "Research what a growing business actually needs: quality, transport, energy, software, exports and automation.",
        "Connect mature businesses back into the ecosystem as mentors, suppliers, and local anchors.",
      ]}
      capabilities={[
        { label: "Export destinations", status: counts.ExportCountry ? "LIVE" : "NOT_AVAILABLE_YET", href: "/knowledge?type=export", count: counts.ExportCountry },
        { label: "Market channels", status: counts.Market ? "LIVE" : "NOT_AVAILABLE_YET", href: "/knowledge?type=market", count: counts.Market },
        { label: "Capital sources", status: counts.FinancialInstitution ? "LIVE" : "NOT_AVAILABLE_YET", href: "/knowledge?type=bank", count: counts.FinancialInstitution },
        { label: "Automation", dependency: "We have not researched automation suppliers or what upgrading costs." },
        { label: "Robotics", dependency: "We have not researched robotics yet." },
        { label: "ERP", dependency: "We have not researched business software yet." },
        { label: "Quality", dependency: "We list certifications you can earn, but not quality systems for a business." },
        { label: "Logistics", dependency: "We have not researched transport companies, routes or freight costs." },
        { label: "Energy", dependency: "We have not researched electricity tariffs or solar capacity." },
      ]}
      cards={cards}
    />
  );
}
