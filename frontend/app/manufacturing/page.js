import ModuleShell from "@/components/platform/ModuleShell";
import ManufacturingSections from "./components/ManufacturingSections";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";

export const metadata = buildBaseMetadata({
  title: "Manufacturing | ValueWeave",
  description: "Explore the future manufacturing layer for products, machinery, raw materials, suppliers, production, and compliance.",
  alternates: { canonical: `${BASE_URL}/manufacturing` },
});

export default function ManufacturingPage() {
  return (
    <ModuleShell
      badge="MANUFACTURING"
      title="Build Real Products"
      description="A modular manufacturing foundation for future product discovery, factory planning, suppliers, production, and compliance workflows."
    >
      <ManufacturingSections />
    </ModuleShell>
  );
}
