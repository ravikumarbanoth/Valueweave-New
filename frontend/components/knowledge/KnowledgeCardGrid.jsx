// A grid of KnowledgeCards, plus the empty states that must not look alike.
//
// The states still mean different things internally — that distinction is real
// and worth keeping. What changed in the UX polish pass is who the sentences are
// written for. A grid on a district page told students to run
// `scripts/run_user_intelligence.sh`; it now tells them to complete their
// profile. Same condition, same `data-reason`, different reader.
//
// Operator detail moves to `data-operator-note`, where support and tests can
// reach it and a student cannot.
//
// PX Phase 4: this grid had the same dead-end shape as KnowledgeEmptyState —
// a title, a paragraph, and nowhere to go. It now renders the same next step,
// including for NOT_COMPUTED, which is the one state where the reader can
// actually fix it themselves and so is the one that most needed a button.
import Link from "next/link";
import { emptyStateCopy, normaliseReason } from "./KnowledgeEmptyState";

export default function KnowledgeCardGrid({
  children,
  status,
  note,
  dependency,
  action,
  emptyTitle = "More coming soon",
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

  // NOT_COMPUTED is the one state with no shared-knowledge equivalent: the
  // information exists, and we have not worked out this person's matches yet.
  // It is also the only state where the user genuinely can do something.
  const local = {
    NOT_COMPUTED: {
      title: "Tell us a little about yourself",
      body:
        "Add your skills and your district, and we will suggest opportunities, " +
        "courses and schemes that fit you.",
      nextStep: { href: "/onboarding", label: "Complete your profile" },
      operatorNote: "Per-user analysis has not run for this account.",
    },
  }[key];

  const copy = local || emptyStateCopy(key, { entityLabel: "results" });
  const title = key ? copy.title : emptyTitle;
  const tone =
    key === "NOT_COMPUTED" || key === "NOT_DEPLOYED" || key === "EMPTY"
      ? "border-amber-200 bg-amber-50"
      : "border-stone-200 bg-stone-50";

  return (
    <div
      data-testid={testId ? `${testId}-empty` : undefined}
      data-reason={key || undefined}
      data-operator-note={dependency || copy.operatorNote || undefined}
      className={`rounded-2xl border border-dashed ${tone} p-6 text-center`}
    >
      <p className="font-display font-bold text-sm text-ink">{title}</p>
      <p className="text-xs text-muted mt-1.5 leading-relaxed max-w-xl mx-auto">
        {note || copy.body}
      </p>
      {action || (
        <Link
          href={copy.nextStep.href}
          data-testid={testId ? `${testId}-next` : "empty-next"}
          className="inline-block text-xs font-display font-bold text-amber-700 mt-3 hover:text-amber-600"
        >
          {copy.nextStep.label} →
        </Link>
      )}
    </div>
  );
}
