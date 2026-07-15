import ModuleShell from "@/components/platform/ModuleShell";
import ScaleSections from "./components/ScaleSections";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";

export const metadata = buildBaseMetadata({
  title: "Scale | ValueWeave",
  description: "Plan future growth through automation, quality, ERP, export, logistics, energy, and industrial resources.",
  alternates: { canonical: `${BASE_URL}/scale` },
});

export default function ScalePage() {
  return (
    <ModuleShell
      badge="INDUSTRIAL SCALING"
      title="Scale What Works"
      description="A future expansion layer for businesses ready to improve operations, quality, logistics, exports, and industrial efficiency."
    >
      <ScaleSections />
    </ModuleShell>
  );
}
