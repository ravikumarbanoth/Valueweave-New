import ModuleShell from "@/components/platform/ModuleShell";
import AiSections from "./components/AiSections";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";

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
