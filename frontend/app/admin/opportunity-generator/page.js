import AdminShell from "@/components/admin/AdminShell";
import GeneratorClient from "./GeneratorClient";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "Opportunity Generator | ValueWeave Admin",
  robots: { index: false, follow: false },
};

export default function OpportunityGeneratorPage() {
  return (
    <AdminShell>
      <div className="p-6 max-w-4xl space-y-6">
        <div>
          <span className="chip bg-amber-100 text-amber-700 border border-amber-200">BULK GENERATOR</span>
          <h1 className="font-display font-extrabold text-2xl text-ink mt-2">Opportunity Generator</h1>
          <p className="text-stone-500 text-sm mt-1">
            Bulk-generate SEO-optimized opportunity records with templated descriptions, skill requirements, and collaborator roles. Preview before publishing.
          </p>
        </div>
        <GeneratorClient />
      </div>
    </AdminShell>
  );
}
