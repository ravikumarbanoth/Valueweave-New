// A grid of KnowledgeCards, plus the three empty states that must not look alike.
//
// THIS IS THE COMPONENT THAT DECIDES WHETHER THE INTEGRATION FEELS BROKEN.
// "No data source exists", "nothing matched you" and "not analysed yet" render
// identically if you let them, and they mean completely different things:
//
//   NO_DATA_SOURCE  we have nothing to offer here, and we know why
//   NO_MATCHES      we looked and found nothing for you
//   NOT_COMPUTED    nobody has run the analysis
//
// A blank div reads as a bug. A sentence reads as honesty.
export default function KnowledgeCardGrid({
  children,
  status,
  note,
  emptyTitle = "Nothing here yet",
  columns = "sm:grid-cols-2 lg:grid-cols-3",
  testId,
}) {
  const items = Array.isArray(children) ? children.filter(Boolean) : children ? [children] : [];

  if (items.length > 0) {
    return (
      <div data-testid={testId} className={`grid gap-3 ${columns}`}>
        {items}
      </div>
    );
  }

  const copy = {
    NO_DATA_SOURCE: {
      title: "We don't have this data yet",
      tone: "border-stone-200 bg-stone-50",
    },
    NOT_COMPUTED: {
      title: "Not analysed yet",
      tone: "border-amber-200 bg-amber-50",
    },
    NOT_DEPLOYED: {
      title: "Not switched on for this deployment",
      tone: "border-stone-200 bg-stone-50",
    },
  }[status] || { title: emptyTitle, tone: "border-stone-200 bg-stone-50" };

  return (
    <div
      data-testid={testId ? `${testId}-empty` : undefined}
      className={`rounded-2xl border border-dashed ${copy.tone} p-6 text-center`}
    >
      <p className="font-display font-bold text-sm text-ink">{copy.title}</p>
      {note && <p className="text-xs text-muted mt-1.5 leading-relaxed max-w-xl mx-auto">{note}</p>}
    </div>
  );
}
