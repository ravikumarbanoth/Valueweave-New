import ModuleShell from "@/components/platform/ModuleShell";
import NetworkSections from "./components/NetworkSections";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";

export const metadata = buildBaseMetadata({
  title: "Network | ValueWeave",
  description: "Find co-founders, experts, mentors, investors, institutions, and communities through ValueWeave's collaboration layer.",
  alternates: { canonical: `${BASE_URL}/network` },
});

export default function NetworkPage() {
  return (
    <ModuleShell
      badge="COLLABORATION"
      title="Build With the Right People"
      description="The network module organizes ValueWeave's collaboration features and leaves clear room for future co-founder, mentor, investor, institution, and community workflows."
    >
      <NetworkSections />
    </ModuleShell>
  );
}
