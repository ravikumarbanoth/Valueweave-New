import ModuleDashboard from "@/components/platform/ModuleDashboard";

const cards = [
  { emoji: "🤖", title: "Automation", description: "Future automation guidance for repeatable operations and reduced manual dependency." },
  { emoji: "🦾", title: "Robotics", description: "Reserved layer for robotics resources, providers, and industrial upgrade paths." },
  { emoji: "✅", title: "Quality", description: "Planned quality systems, standards, documentation, and continuous improvement playbooks." },
  { emoji: "🌍", title: "Export", description: "Future export readiness resources, logistics, compliance, and market expansion guidance." },
];

export default function ScaleSections() {
  return (
    <ModuleDashboard
      primaryHref="/scale"
      primaryLabel="Scale Business"
      roadmap={[
        "Define the operating maturity ladder from local production to competitive manufacturing.",
        "Map scale resources to quality, logistics, energy, ERP, export, automation, and robotics needs.",
        "Connect mature businesses back into the ecosystem as mentors, suppliers, and local anchors.",
      ]}
      capabilities={["Automation", "Robotics", "ERP", "Quality", "Export", "Logistics", "Energy", "Industrial Resources"]}
      cards={cards}
    />
  );
}
