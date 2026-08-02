import Link from "next/link";
import SnapshotPanel from "@/components/geo/SnapshotPanel";

function Field({ label, value }) {
  if (!value || (Array.isArray(value) && value.length === 0)) return null;
  return (
    <div className="bg-stone-50 border border-stone-200 rounded-xl px-4 py-3">
      <p className="text-xs text-stone-400 uppercase tracking-wider font-semibold mb-1">{label}</p>
      <p className="text-sm text-ink leading-relaxed">{Array.isArray(value) ? value.join(", ") : value}</p>
    </div>
  );
}

// PX Phase 2. The panel used to be headed `${typeLabel} Snapshot`, which
// produced "Government Scheme Snapshot" and "Skill Snapshot" — the type name
// from the database, used as a title. It reads as a category label on a record
// rather than as a heading written for the person reading it, and it is the
// first thing on the page.
//
// One human heading per type, defaulting to "Quick overview" for anything not
// listed, so a new caller degrades to a sentence rather than to a type name.
const PANEL_TITLE = {
  "Government Scheme": "What this scheme offers",
  Skill: "What this work involves",
  Resource: "Quick overview",
  Roadmap: "Quick overview",
};

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
          <SnapshotPanel
            title={PANEL_TITLE[typeLabel] || "Quick overview"}
            items={{
              // "District Relevance" used to fall back to "Applicable where
              // admin maps this entity to districts." — a note to whoever
              // maintains the data, shown to whoever reads the page. There is
              // no honest user-facing sentence to put in its place when we do
              // not know the district, so the row is simply left out;
              // SnapshotPanel drops empty rows.
              "Key takeaways": entity.ai_summary || entity.summary || entity.description,
              "Who this is for": "Students, job seekers, small business owners and anyone building something locally.",
              "Money needed to start": entity.investment_needed || entity.investment_range || entity.estimated_cost || entity.cost_range || "Varies",
              "Where it applies": entity.state || entity.location,
              "What it could lead to": entity.future_demand || entity.description,
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
