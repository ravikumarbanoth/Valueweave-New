import ModuleDashboard from "@/components/platform/ModuleDashboard";

const cards = [
  { emoji: "📍", title: "AI District Advisor", description: "Future advisor for district context, local fit, and opportunity interpretation." },
  { emoji: "🏭", title: "AI Manufacturing Advisor", description: "Future advisor for product, machinery, factory, supplier, and production decisions." },
  { emoji: "🛠️", title: "AI Readiness Advisor", description: "Future advisor for skill gaps, learning paths, training, and mentor recommendations." },
  { emoji: "📈", title: "AI Scale Advisor", description: "Future advisor for quality, export, logistics, automation, and industrial scaling." },
];

export default function AiSections() {
  return (
    <ModuleDashboard
      primaryHref="/ai"
      primaryLabel="View AI Layer"
      roadmap={[
        "Keep AI dependent on trustworthy human-readable modules and structured platform knowledge.",
        "Prepare AI-readable relationships across districts, skills, manufacturing, network, and scaling resources.",
        "Introduce advisors only after content quality, permissions, and safety boundaries are ready.",
      ]}
      capabilities={["AI District Advisor", "AI Manufacturing Advisor", "AI Readiness Advisor", "AI Scale Advisor", "Knowledge Graph", "Recommendations"]}
      cards={cards}
    />
  );
}
