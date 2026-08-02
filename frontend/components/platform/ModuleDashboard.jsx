// The shared module dashboard — Platform v3.0, Step 4.
//
// WHAT CHANGED
// ------------
// Every card on this dashboard used to carry a "Coming Soon" chip, and a fixed
// amber panel read "This dashboard is intentionally prepared for future workflows
// without adding database tables, APIs, AI logic, or business rules yet."
//
// That sentence was true when it was written and is not true now. Several of the
// capabilities these dashboards list — training providers, certifications,
// machinery, export destinations, business opportunities — are researched, synced
// and reachable. They were labelled "Coming Soon" purely because nobody had wired
// the card to the projection.
//
// A card now declares its own status. LIVE cards link into the knowledge base and
// show how many records back them; the rest name the dependency that is actually
// missing. Same component, same layout, five modules unchanged in structure.
//
// `capabilities` accepts either a plain string (unavailable, no explanation
// beyond the section heading) or `{ label, status, href, count, dependency }`.
// Strings are kept so a caller that has not been reviewed yet still renders.
import Link from "next/link";
import CapabilityCard, { CapabilityChip } from "@/components/knowledge/CapabilityStatus";

function normalise(capability) {
  if (typeof capability === "string") return { label: capability, status: "NOT_AVAILABLE_YET" };
  return { status: "NOT_AVAILABLE_YET", ...capability };
}

export default function ModuleDashboard({
  roadmap = [],
  capabilities = [],
  cards = [],
  primaryHref = "/",
  primaryLabel = "Open Module",
  // What the whole module is waiting on, when its unavailable parts share a
  // cause. Rendered in place of the old "Coming Soon" panel.
  dependency,
  testId = "module-dashboard",
}) {
  const caps = capabilities.map(normalise);
  const liveCaps = caps.filter((c) => c.status === "LIVE" && c.href);

  return (
    <div className="space-y-8" data-testid={testId}>
      <div className="grid lg:grid-cols-[1.1fr_0.9fr] gap-5">
        <section className="card-base p-6">
          {/* `flex-wrap`: the heading went from "Buildout Plan" to a sentence,
              and on a 390px screen a two-word heading and a five-word heading
              do not lay out the same way. Without wrapping, the heading broke
              across two lines while the button stayed pinned beside it and
              squeezed. The button now drops below on narrow screens instead. */}
          <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
            <div>
              <span className="chip bg-amber-50 text-amber-700 border border-amber-100">WHAT IS NEXT</span>
              <h2 className="font-display font-extrabold text-2xl text-ink mt-3">Where this is going</h2>
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
          <span className="chip bg-teal-50 text-teal-700 border border-teal-100">WHAT YOU CAN USE</span>
          <h2 className="font-display font-extrabold text-2xl text-ink mt-3 mb-2">
            What works today
          </h2>
          <p className="text-xs text-muted mb-5 leading-relaxed">
            {liveCaps.length > 0
              ? `${liveCaps.length} of these ${caps.length} are ready to open right now.`
              : "None of these is ready to open yet."}
          </p>

          <div className="flex flex-wrap gap-2" data-testid="module-capabilities">
            {caps.map((cap) =>
              cap.status === "LIVE" && cap.href ? (
                <Link
                  key={cap.label}
                  href={cap.href}
                  data-testid="module-capability"
                  data-status="LIVE"
                  className="chip bg-teal-50 text-teal-700 border border-teal-200 hover:border-teal-400 transition-colors"
                >
                  {cap.label}
                  {cap.count !== undefined && cap.count !== null && (
                    <span className="tabular-nums ml-1 text-teal-600/70">{cap.count}</span>
                  )}
                  <span className="ml-1">→</span>
                </Link>
              ) : (
                <span
                  key={cap.label}
                  data-testid="module-capability"
                  data-status={cap.status}
                  title={cap.dependency || undefined}
                  className="chip bg-white text-stone-500 border border-stone-200"
                >
                  {cap.label}
                </span>
              )
            )}
          </div>

          {dependency && (
            <div className="mt-6 rounded-xl bg-stone-50 border border-stone-200 p-4"
                 data-testid="module-dependency">
              <div className="flex items-center gap-2 mb-1.5">
                <CapabilityChip status="NOT_AVAILABLE_YET" />
              </div>
              <p className="text-sm text-muted leading-relaxed">{dependency}</p>
            </div>
          )}
        </section>
      </div>

      <section>
        <div className="flex items-end justify-between gap-3 mb-4">
          <div>
            <span className="chip bg-stone-100 text-stone-600 border border-stone-200">EXPLORE</span>
            <h2 className="font-display font-extrabold text-2xl text-ink mt-3">Areas we cover here</h2>
          </div>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {cards.map((card) => (
            <CapabilityCard
              key={card.title}
              testId="module-card"
              emoji={card.emoji}
              title={card.title}
              description={card.description}
              status={card.status || "NOT_AVAILABLE_YET"}
              dependency={card.dependency}
              href={card.href}
              count={card.count}
            />
          ))}
        </div>
      </section>
    </div>
  );
}
