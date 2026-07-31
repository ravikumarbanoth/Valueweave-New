// AI intelligence module — Platform v3.0, Step 4.
//
// Nothing on this page became live, and it would be easy to make it look as
// though something had. The platform does have a recommendation engine, and it
// is rule-based on purpose: `user_intelligence` fires deterministic rules over
// the knowledge graph and every recommendation carries the rule that produced it.
// Presenting that as an "AI advisor" would be the most misleading thing this
// step could do.
//
// So the four advisors keep their unavailable status, the two capabilities that
// DO exist are named as what they are, and the module points at them.
import ModuleDashboard from "@/components/platform/ModuleDashboard";
import { typeCounts } from "@/lib/knowledge";

const NO_MODEL =
  "No model, no inference and no prompt layer exists in this repository. The " +
  "recommendation engine that does exist is rule-based and deterministic by design.";

export default async function AiSections() {
  const counts = await typeCounts();
  const total = Object.values(counts).reduce((a, b) => a + b, 0);

  const cards = [
    {
      emoji: "🧠",
      title: "Rule-based recommendations",
      description:
        "Suggestions matched to your skills and district. Every one tells you why we suggested it and where the information came from.",
      status: "LIVE",
      href: "/dashboard",
    },
    {
      emoji: "🕸️",
      title: "Everything we have researched",
      description:
        "The structured layer any future advisor would read: entities, typed relationships and provenance on every edge.",
      ...(total > 0
        ? { status: "LIVE", href: "/knowledge", count: total }
        : {
            status: "NOT_AVAILABLE_YET",
            dependency: "This section is still being connected. Check back soon.",
          }),
    },
    {
      emoji: "📍",
      title: "AI district advisor",
      description: "Natural-language guidance on local fit and opportunity interpretation.",
      status: "NOT_AVAILABLE_YET",
      dependency: NO_MODEL,
    },
    {
      emoji: "🏭",
      title: "AI manufacturing advisor",
      description: "Natural-language guidance on product, machinery and production decisions.",
      status: "NOT_AVAILABLE_YET",
      dependency: NO_MODEL,
    },
  ];

  return (
    <ModuleDashboard
      primaryHref="/knowledge"
      primaryLabel="Open Knowledge Explorer"
      dependency={
        "We do not have an AI advisor yet. What works today is matching: we compare " +
        "your skills and district against what we have researched, and always show " +
        "you why. That is deliberate — you can check our reasoning."
      }
      roadmap={[
        "Keep AI dependent on trustworthy human-readable modules and structured platform knowledge.",
        "Connect districts, skills, businesses and schemes so guidance can draw on all of them at once.",
        "Introduce advisors only after content quality, permissions, and safety boundaries are ready.",
      ]}
      capabilities={[
        { label: "Everything we have researched", status: total ? "LIVE" : "NOT_AVAILABLE_YET", href: "/knowledge", count: total },
        { label: "Rule-based recommendations", status: "LIVE", href: "/dashboard" },
        { label: "AI district advisor", dependency: NO_MODEL },
        { label: "AI manufacturing advisor", dependency: NO_MODEL },
        { label: "AI readiness advisor", dependency: NO_MODEL },
        { label: "AI scale advisor", dependency: NO_MODEL },
      ]}
      cards={cards}
    />
  );
}
