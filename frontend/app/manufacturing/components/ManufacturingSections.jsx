import ModuleDashboard from "@/components/platform/ModuleDashboard";

const cards = [
  { emoji: "📦", title: "Product Discovery", description: "Future product opportunity surfaces for practical manufacturing ideas and demand signals." },
  { emoji: "🏗️", title: "Factory Planning", description: "Reserved planning area for space, layout, compliance, machinery, and setup sequence." },
  { emoji: "⚙️", title: "Machinery", description: "Future machinery catalogs connected to industries, products, suppliers, and investment bands." },
  { emoji: "🏭", title: "Production", description: "Planned operating guidance for repeatable production, quality, staffing, and throughput." },
];

export default function ManufacturingSections() {
  return (
    <ModuleDashboard
      primaryHref="/manufacturing"
      primaryLabel="Explore Manufacturing"
      roadmap={[
        "Organize product, machinery, supplier, raw material, and compliance knowledge into reusable modules.",
        "Connect manufacturing guides to district industries and readiness pathways.",
        "Prepare future operating dashboards without introducing production business logic yet.",
      ]}
      capabilities={["Product Discovery", "Manufacturing Guides", "Factory Planning", "Machinery", "Raw Materials", "Suppliers", "Production", "Compliance"]}
      cards={cards}
    />
  );
}
