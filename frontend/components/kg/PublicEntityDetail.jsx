import Link from "next/link";
import AiReadableSummary from "@/components/geo/AiReadableSummary";

function Field({ label, value }) {
  if (!value || (Array.isArray(value) && value.length === 0)) return null;
  return (
    <div className="bg-stone-50 border border-stone-200 rounded-xl px-4 py-3">
      <p className="text-xs text-stone-400 uppercase tracking-wider font-semibold mb-1">{label}</p>
      <p className="text-sm text-ink leading-relaxed">{Array.isArray(value) ? value.join(", ") : value}</p>
    </div>
  );
}

export default function PublicEntityDetail({ entity, typeLabel, backHref, backLabel, titleField = "name", fields = [] }) {
  const title = entity[titleField];
  return (
    <main className="min-h-screen bg-cream font-body pb-16">
      <section className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
        <Link href={backHref} className="text-sm font-display font-semibold text-muted hover:text-ink">← {backLabel}</Link>
        <article className="card-base p-6 md:p-8 mt-4">
          <span className="chip bg-amber-50 text-amber-700 mb-3">{typeLabel}</span>
          <h1 className="font-display font-extrabold text-3xl tracking-tight text-ink mb-3">{title}</h1>
          <p className="text-muted leading-relaxed mb-6">{entity.summary || entity.description || entity.meta_description}</p>
          <AiReadableSummary
            title={`AI-readable ${typeLabel.toLowerCase()} summary`}
            items={{
              "Key Takeaways": entity.ai_summary || entity.summary || entity.description,
              "Who should read this": "Entrepreneurs, students, MSMEs, collaborators, and local ecosystem builders.",
              "Investment Range": entity.investment_needed || entity.investment_range || entity.estimated_cost || entity.cost_range || "Varies",
              "District Relevance": entity.state || entity.location || "Applicable where admin maps this entity to districts.",
              "Business Potential": entity.future_demand || entity.description || "Use this entry with linked opportunities, skills, schemes, and resources.",
            }}
            faq={entity.faq_json || []}
          />
          <div className="grid sm:grid-cols-2 gap-3 mb-6">
            {fields.map((field) => <Field key={field.key} label={field.label} value={entity[field.key]} />)}
          </div>
          {entity.rich_text && <div className="md-preview" dangerouslySetInnerHTML={{ __html: entity.rich_text }} />}
        </article>
      </section>
    </main>
  );
}
