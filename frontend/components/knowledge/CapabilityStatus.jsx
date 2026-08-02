// The chip that replaced "Coming Soon" — Platform v3.0, Step 4.
//
// WHY "COMING SOON" HAD TO GO
// ---------------------------
// It made a promise the repository could not keep and gave the reader nothing to
// act on. Worse, it was applied uniformly: the same chip sat on capabilities that
// were fully researched and merely unwired, and on capabilities with no data
// source anywhere in Packages 001–008. A user could not tell which was which, and
// neither could we.
//
// Every capability now declares one of three honest states and names what it
// depends on:
//
//   LIVE                backed by the knowledge platform, and linked to it
//   NOT_AVAILABLE_YET   not built; the dependency says what would have to be
//   NO_DATA_SOURCE      no package covers it at all — the deepest kind of gap
//
// `dependency` is required for the two unavailable states. A capability that
// cannot say what it is waiting for is a capability nobody has thought about.
//
// PX PHASE 2 — THE THREE STATE NAMES ARE OURS, NOT THEIRS
// -------------------------------------------------------
// The keys above are the vocabulary the codebase reasons in and they stay. What
// a person READS is now written for a person: "No Data Source" is a sentence
// about our pipeline, and a student reading it on the mentors card learns only
// that something they do not understand is missing. "Not researched yet" says
// the same thing about the world instead of about us — and it is the truth.
//
// "Depends on:" had the same problem in miniature. It is a build-plan word. The
// reader is not waiting on a dependency; they are asking why the thing is not
// there.
import Link from "next/link";

const STATES = {
  LIVE: {
    label: "Ready now",
    chip: "bg-teal-50 text-teal-700 border-teal-200",
  },
  NOT_AVAILABLE_YET: {
    label: "Coming later",
    chip: "bg-stone-50 text-stone-500 border-stone-200",
  },
  NO_DATA_SOURCE: {
    label: "Not researched yet",
    chip: "bg-stone-50 text-stone-400 border-stone-200",
  },
};

export function CapabilityChip({ status = "NOT_AVAILABLE_YET", className = "" }) {
  const s = STATES[status] || STATES.NOT_AVAILABLE_YET;
  return (
    <span
      data-testid="capability-chip"
      data-status={status}
      className={`chip border ${s.chip} text-[10px] ${className}`}
    >
      {s.label}
    </span>
  );
}

/**
 * One capability card: what it is, whether it works, and what it waits on.
 *
 * A LIVE capability must pass `href` — the whole point of declaring it live is
 * that the user can go there. One that cannot be reached is not live.
 */
export default function CapabilityCard({
  emoji,
  title,
  description,
  status = "NOT_AVAILABLE_YET",
  dependency,
  href,
  count,
  testId = "capability-card",
}) {
  const live = status === "LIVE" && href;

  const body = (
    <>
      <div className="flex items-center justify-between gap-2 mb-3">
        {emoji && <span className="text-2xl" aria-hidden="true">{emoji}</span>}
        <CapabilityChip status={live ? "LIVE" : status} className="ml-auto" />
      </div>
      <h3 className="font-display font-bold text-base text-ink mb-2 leading-snug">
        {title}
        {live && count !== undefined && count !== null && (
          <span className="text-stone-400 font-normal tabular-nums ml-1.5">{count}</span>
        )}
      </h3>
      {description && (
        <p className="text-sm text-muted leading-relaxed">{description}</p>
      )}
      {!live && dependency && (
        <p className="text-[10px] text-stone-400 mt-auto pt-3 leading-relaxed">
          <span className="font-display font-bold text-stone-500">Why not yet: </span>
          {dependency}
        </p>
      )}
      {live && (
        <p className="text-[13px] font-display font-bold text-amber-700 mt-auto pt-3">
          Open →
        </p>
      )}
    </>
  );

  const shell = "card-base p-5 min-h-[175px] flex flex-col";

  if (!live) {
    return (
      <div data-testid={testId} data-status={status} className={`${shell} opacity-95`}>
        {body}
      </div>
    );
  }
  return (
    <Link
      data-testid={testId}
      data-status="LIVE"
      href={href}
      className={`${shell} hover:border-amber-300 hover:shadow-md transition-all group`}
    >
      {body}
    </Link>
  );
}
