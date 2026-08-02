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

// PX Phase 2: this sentence said "no model, no inference and no prompt layer
// exists in this repository", which is precise, true, and readable only by
// someone who already knows what those three things are. The honesty was the
// point and it survives — stated as what we do instead of what we lack.
const NO_MODEL =
  "We have not built an AI advisor. What suggests things to you today follows " +
  "fixed rules we wrote by hand, and it always tells you which rule it used.";

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
        "Districts, skills, courses, schemes and business ideas — each one linked to the others, and each one saying where the information came from.",
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
        "Any advice we ever give will be built on research you can open and check for yourself.",
        "Connect districts, skills, businesses and schemes so guidance can draw on all of them at once.",
        "Add an advisor only once we are confident it will not mislead anyone about their money or their career.",
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
