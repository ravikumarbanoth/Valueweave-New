// A grid of KnowledgeCards, plus the empty states that must not look alike.
//
// THIS IS THE COMPONENT THAT DECIDES WHETHER THE INTEGRATION FEELS BROKEN.
// "No data source exists", "nothing matched you" and "not analysed yet" render
// identically if you let them, and they mean completely different things.
//
// A blank div reads as a bug. A sentence reads as honesty. A sentence that names
// what has to happen next reads as a plan.
//
// Step 4 aligned the vocabulary with KnowledgeEmptyState so the same five names
// mean the same five things everywhere in the app — plus NOT_COMPUTED, which is
// specific to per-user intelligence and has no equivalent for shared knowledge.
import { emptyStateCopy, normaliseReason } from "./KnowledgeEmptyState";

export default function KnowledgeCardGrid({
  children,
  status,
  note,
  dependency,
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

  const key = normaliseReason(status);

  // NOT_COMPUTED is the one state with no shared-knowledge equivalent: the data
  // source exists and is deployed, but the engine has not run for THIS user.
  const local = {
    NOT_COMPUTED: {
      title: "Not analysed yet",
      dependency:
        "`scripts/run_user_intelligence.sh --from-db --apply` has not processed " +
        "your profile.",
    },
  }[key];

  const copy = local || emptyStateCopy(key, { entityLabel: "records" });
  const title = key ? copy.title : emptyTitle;
  const tone =
    key === "NOT_COMPUTED" || key === "NOT_DEPLOYED" || key === "EMPTY"
      ? "border-amber-200 bg-amber-50"
      : "border-stone-200 bg-stone-50";
  const depends = dependency || copy.dependency;

  return (
    <div
      data-testid={testId ? `${testId}-empty` : undefined}
      data-reason={key || undefined}
      className={`rounded-2xl border border-dashed ${tone} p-6 text-center`}
    >
      <p className="font-display font-bold text-sm text-ink">{title}</p>
      {note && <p className="text-xs text-muted mt-1.5 leading-relaxed max-w-xl mx-auto">{note}</p>}
      {depends && (
        <p className="text-[10px] text-stone-400 mt-2 leading-relaxed max-w-xl mx-auto">
          <span className="font-display font-bold text-stone-500">Depends on: </span>
          {depends}
        </p>
      )}
    </div>
  );
}
