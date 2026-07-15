import Link from "next/link";

export default function ModuleDashboard({ roadmap = [], capabilities = [], cards = [], primaryHref = "/", primaryLabel = "Open Module" }) {
  return (
    <div className="space-y-8">
      <div className="grid lg:grid-cols-[1.1fr_0.9fr] gap-5">
        <section className="card-base p-6">
          <div className="flex items-center justify-between gap-3 mb-5">
            <div>
              <span className="chip bg-amber-50 text-amber-700 border border-amber-100">ROADMAP</span>
              <h2 className="font-display font-extrabold text-2xl text-ink mt-3">Buildout Plan</h2>
            </div>
            <Link href={primaryHref} className="btn-secondary !py-2 !px-4 text-sm">{primaryLabel}</Link>
          </div>
          <div className="space-y-3">
            {roadmap.map((item, index) => (
              <div key={item} className="flex gap-3 rounded-xl bg-stone-50 border border-stone-100 p-3">
                <span className="w-7 h-7 rounded-full bg-white border border-stone-200 flex items-center justify-center text-xs font-display font-bold text-amber-700 shrink-0">
                  {index + 1}
                </span>
                <p className="text-sm text-muted leading-relaxed">{item}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="card-base p-6">
          <span className="chip bg-teal-50 text-teal-700 border border-teal-100">FUTURE CAPABILITIES</span>
          <h2 className="font-display font-extrabold text-2xl text-ink mt-3 mb-5">Coming Next</h2>
          <div className="flex flex-wrap gap-2">
            {capabilities.map((item) => (
              <span key={item} className="chip bg-white text-stone-600 border border-stone-200">
                {item}
              </span>
            ))}
          </div>
          <div className="mt-6 rounded-xl bg-amber-50 border border-amber-100 p-4">
            <p className="text-sm font-display font-bold text-amber-800">Coming Soon</p>
            <p className="text-sm text-amber-700 mt-1 leading-relaxed">This dashboard is intentionally prepared for future workflows without adding database tables, APIs, AI logic, or business rules yet.</p>
          </div>
        </section>
      </div>

      <section>
        <div className="flex items-end justify-between gap-3 mb-4">
          <div>
            <span className="chip bg-stone-100 text-stone-600 border border-stone-200">MODULE AREAS</span>
            <h2 className="font-display font-extrabold text-2xl text-ink mt-3">Expansion Cards</h2>
          </div>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {cards.map((card) => (
            <div key={card.title} className="card-base p-5 min-h-[165px] flex flex-col">
              <div className="flex items-center justify-between gap-2 mb-3">
                <span className="text-2xl" aria-hidden="true">{card.emoji}</span>
                <span className="chip bg-stone-50 text-stone-500 border border-stone-100 text-[10px]">Coming Soon</span>
              </div>
              <h3 className="font-display font-bold text-base text-ink mb-2">{card.title}</h3>
              <p className="text-sm text-muted leading-relaxed mt-auto">{card.description}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
