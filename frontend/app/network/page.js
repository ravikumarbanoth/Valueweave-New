import ModuleShell from "@/components/platform/ModuleShell";
import NetworkSections from "./components/NetworkSections";
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
