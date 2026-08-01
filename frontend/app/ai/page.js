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
  title: "AI Intelligence Layer | ValueWeave",
  description: "Future AI intelligence layer for district, manufacturing, readiness, and scale advisory experiences.",
  alternates: { canonical: `${BASE_URL}/ai` },
});

export default function AiPage() {
  return (
    <ModuleShell
      badge="AI INTELLIGENCE"
      title="Future AI Intelligence Layer"
      description="Reserved architecture for AI-first guidance across districts, manufacturing, readiness, and scaling. No AI features are implemented yet."
    >
      <AiSections />
    </ModuleShell>
  );
}
