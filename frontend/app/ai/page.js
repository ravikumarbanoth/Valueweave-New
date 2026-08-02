import ModuleShell from "@/components/platform/ModuleShell";
import AiSections from "./components/AiSections";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";

// This page reads the researched projection, so it must not be frozen at build
// time — the sync writes to the database long after the build, and a fully static
// page would keep showing "being prepared" until the next deploy.
//
// It already refreshed, but only by accident: the shared Footer calls
// getPlatformSettings(), an unstable_cache with revalidate 60, and Next takes the
// LOWEST revalidate in a segment. Every page in the app therefore inherited 60s
// from a component that has nothing to do with knowledge. Declaring it here makes
// the behaviour this page's own. 60 still wins while the footer does that; if the
// footer ever stops, this page keeps refreshing instead of silently freezing.
export const revalidate = 300;

export const metadata = buildBaseMetadata({
  title: "AI Guidance | ValueWeave",
  description: "How ValueWeave suggests things to you today, and what AI guidance we plan to add for districts, manufacturing, readiness and growing a business.",
  alternates: { canonical: `${BASE_URL}/ai` },
});

export default function AiPage() {
  return (
    <ModuleShell
      badge="AI GUIDANCE"
      title="How ValueWeave guides you"
      // PX Phase 2: was "Reserved architecture for AI-first guidance". A student
      // does not know what reserved architecture is, and the sentence made a
      // page about honesty sound like a design document.
      description="We do not have an AI advisor yet. Today we match what we have researched against your skills and your district, and we always show you why."
    >
      <AiSections />
    </ModuleShell>
  );
}
