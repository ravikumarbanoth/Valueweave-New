import Link from "next/link";

function Field({ label, value }) {
  if (!value) return null;
  return (
    <div className="bg-stone-50 border border-stone-200 rounded-xl px-4 py-3">
      <p className="text-xs text-stone-400 uppercase tracking-wider font-semibold mb-1">{label}</p>
      <p className="text-sm text-ink leading-relaxed break-words">{value}</p>
    </div>
  );
}

export default function SchemeSupportDetail({ record }) {
  return (
    <main className="min-h-screen bg-cream font-body pb-16">
      <section className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
        <Link
          href="/schemes"
          className="inline-flex items-center min-h-[44px] text-sm font-display font-semibold text-muted hover:text-ink"
        >
          ← Back to schemes and resources
        </Link>
        <article className="card-base p-6 md:p-8 mt-4">
          <div className="flex flex-wrap gap-2 mb-4">
            <span className="chip bg-amber-50 text-amber-700">{record.display_category}</span>
            <span className="chip bg-teal-50 text-teal-700">{record.record_kind}</span>
          </div>
          <h1 className="font-display font-extrabold text-2xl sm:text-3xl tracking-tight text-ink mb-3 break-words">
            {record.name}
          </h1>
          <p className="text-muted leading-relaxed mb-6">
            {record.description ||
              "A detailed summary is not yet included in this directory entry. Please check the official portal or relevant department for current programme details."}
          </p>

          <div className="grid sm:grid-cols-2 gap-3 mb-6">
            <Field label="Category" value={record.display_category} />
            <Field label="Resource type" value={record.record_kind} />
            <Field label="Organisation type" value={record.organisation_type} />
            <Field label="Acronym / Short name" value={record.acronym} />
          </div>

          {record.supplemental_notes && (
            <div className="mb-5 rounded-xl border border-stone-200 bg-white px-4 py-3">
              <p className="text-xs text-stone-400 uppercase tracking-wider font-semibold mb-1">Additional notes</p>
              <p className="text-sm text-ink leading-relaxed">{record.supplemental_notes}</p>
            </div>
          )}

          <div className="space-y-3">
            {record.official_website ? (
              <a
                href={record.official_website}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary inline-flex items-center min-h-[44px] text-sm"
              >
                Visit official website →
              </a>
            ) : (
              <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
                Official website link is not listed for this entry yet. Please verify the official portal through the relevant ministry, department, or nodal agency before applying.
              </div>
            )}
            <p className="text-xs text-muted leading-relaxed">
              Always verify current eligibility criteria, benefit amounts, deadlines, and application steps on the official portal before applying.
            </p>
          </div>
        </article>
      </section>
    </main>
  );
}
