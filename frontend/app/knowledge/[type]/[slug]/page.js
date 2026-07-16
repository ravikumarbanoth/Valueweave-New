import { notFound } from "next/navigation";
import AppNavbar from "@/components/AppNavbar";
import { getAllKnowledgeItems, getKnowledgeItem, knowledgeLabels } from "@/lib/static-knowledge";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";

export function generateStaticParams() {
  return getAllKnowledgeItems().map((item) => ({ type: item.type, slug: item.slug }));
}

export function generateMetadata({ params }) {
  const item = getKnowledgeItem(params.type, params.slug);
  if (!item) return {};
  return buildBaseMetadata({
    title: `${item.name} | ValueWeave Knowledge Layer`,
    description: item.summary || item.description || item.purpose || item.overview || "ValueWeave static knowledge layer preview.",
    alternates: { canonical: `${BASE_URL}/knowledge/${params.type}/${params.slug}` },
  });
}

function valueToText(value) {
  if (Array.isArray(value)) return value.join(", ");
  if (value && typeof value === "object") return JSON.stringify(value);
  return value;
}

export default function KnowledgeDetailPage({ params }) {
  const item = getKnowledgeItem(params.type, params.slug);
  if (!item) notFound();

  const typeLabel = knowledgeLabels[params.type] || "Knowledge";
  const entries = Object.entries(item).filter(([key]) => !["slug", "name"].includes(key));

  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <main>
        <section className="relative overflow-hidden bg-ink px-4 sm:px-6 py-14">
          <div className="absolute -top-24 -right-24 w-80 h-80 rounded-full bg-amber-500/20 blur-3xl" />
          <div className="absolute -bottom-24 -left-24 w-96 h-96 rounded-full bg-teal-500/20 blur-3xl" />
          <div className="relative max-w-4xl mx-auto text-center">
            <span className="chip bg-amber-500/20 text-amber-300 border border-amber-500/30 mb-4">{typeLabel}</span>
            <h1 className="font-display font-extrabold tracking-tight text-3xl sm:text-4xl md:text-5xl text-white leading-tight mb-4">{item.name}</h1>
            <p className="text-white/65 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
              {item.summary || item.description || item.purpose || item.overview || "Static knowledge preview for the ValueWeave ecosystem."}
            </p>
          </div>
        </section>

        <section className="max-w-5xl mx-auto px-4 sm:px-6 py-12 pb-20">
          <div className="grid md:grid-cols-2 gap-4">
            {entries.map(([key, value]) => (
              <div key={key} className="card-base p-5">
                <p className="text-[11px] uppercase tracking-wider text-stone-400 font-display font-bold mb-2">{key.replace(/([A-Z])/g, " $1")}</p>
                {Array.isArray(value) ? (
                  <div className="flex flex-wrap gap-2">
                    {value.map((entry) => <span key={entry} className="chip bg-stone-50 text-stone-600 border border-stone-100">{entry}</span>)}
                  </div>
                ) : (
                  <p className="text-sm text-muted leading-relaxed">{valueToText(value)}</p>
                )}
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
