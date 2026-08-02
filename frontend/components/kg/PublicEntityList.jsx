import Link from "next/link";

// `hrefFor` exists because one basePath stopped being enough. `/resources` is
// backed by three graph entity types — training providers, banks and
// institutions — which live at three different detail URLs, so the link has to
// be decided per row rather than per page. Pages that still have a single
// destination just pass basePath and nothing changes for them.
// PX Phase 4: the empty card was a title and a paragraph. `emptyHref` /
// `emptyLabel` give it somewhere to send the reader, and both default to the
// ranked business ideas, which are editorial and therefore still there on the
// days the researched projection is not.
export default function PublicEntityList({
  title, eyebrow, description, items, basePath, titleField = "name",
  emptyText, emptyTitle = "More coming soon", hrefFor,
  emptyHref = "/opportunity-radar",
  emptyLabel = "Browse business ideas",
}) {
  const linkTo = (item) => (hrefFor ? hrefFor(item) : `${basePath}/${item.slug}`);
  return (
    <main className="min-h-screen bg-cream font-body pb-16">
      <section className="bg-ink text-white px-4 sm:px-6 py-14">
        <div className="max-w-5xl mx-auto">
          <span className="chip bg-amber-500/20 text-amber-300 border border-amber-500/30 mb-4">{eyebrow}</span>
          <h1 className="font-display font-extrabold tracking-tight text-3xl sm:text-4xl md:text-5xl leading-tight mb-4">{title}</h1>
          <p className="text-white/65 max-w-2xl leading-relaxed">{description}</p>
        </div>
      </section>
      <section className="max-w-5xl mx-auto px-4 sm:px-6 py-10">
        {items.length === 0 ? (
          <div data-testid="entity-list-empty" className="card-base p-10 text-center">
            <h2 className="font-display font-bold text-xl text-ink mb-2">{emptyTitle}</h2>
            <p className="text-muted text-sm max-w-md mx-auto">{emptyText}</p>
            <Link href={emptyHref} data-testid="entity-list-empty-next"
                  className="btn-secondary text-sm mt-5 inline-flex">
              {emptyLabel} →
            </Link>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {items.map((item) => (
              <Link key={item.id} href={linkTo(item)} className="card-base p-5 hover:border-amber-400 hover:shadow-md hover:-translate-y-1 transition-all">
                <div className="flex items-center justify-between gap-2 mb-3">
                  <span className="chip bg-amber-50 text-amber-700">{item.category || item.type || item.state || "ValueWeave"}</span>
                  {item.future_demand && <span className="chip bg-teal-50 text-teal-700">{item.future_demand}</span>}
                </div>
                <h2 className="font-display font-bold text-lg text-ink mb-2 line-clamp-2">{item[titleField]}</h2>
                <p className="text-sm text-muted leading-relaxed line-clamp-3">{item.summary || item.description || item.meta_description || "Open this entry for details."}</p>
              </Link>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
