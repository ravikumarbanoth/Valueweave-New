import ModuleShell from "@/components/platform/ModuleShell";
import ReadinessSections from "./components/ReadinessSections";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";

export const metadata = buildBaseMetadata({
  title: "Industrial Readiness | ValueWeave",
  description: "Prepare for business and industry through skills, learning paths, certifications, mentors, and practical exposure.",
  alternates: { canonical: `${BASE_URL}/readiness` },
});

export default function ReadinessPage() {
  return (
    <ModuleShell
      badge="INDUSTRIAL READINESS"
      title="Prepare Before You Build"
      description="A future readiness layer for skills, training, mentors, internships, apprenticeships, and industrial exposure."
    >
      <ReadinessSections />
    </ModuleShell>
  );
}
