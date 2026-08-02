// The five empty states, written for the person reading them.
//
// WHAT CHANGED, AND WHY
// ---------------------
// Step 4 gave every empty state a named cause and a dependency, so that an
// operator could tell a deployment gap from a research gap. That was right, and
// it was aimed at entirely the wrong audience. A first-year student looking for
// a course in Warangal was being told:
//
//     "The knowledge schema has not been deployed to this environment.
//      Depends on: Run the migrations, expose the `knowledge` schema, then
//      `scripts/run_sync.sh`. See docs/FIRST_DEPLOYMENT_CHECKLIST.md steps 5–10."
//
// Every word of that is true and none of it is theirs. It tells them the site is
// broken in a way they cannot fix, in vocabulary that makes them feel the
// problem is theirs for not understanding it.
//
// The distinction is worth keeping — it is genuinely useful — so it moved rather
// than went. `reason` still carries the same five names, `data-reason` still
// exposes them in the DOM for support and for tests, and `operatorNote` still
// holds the runbook sentence. What a user READS is now written for a user.
//
// PX PHASE 4 — A SENTENCE IS NOT AN ANSWER
// ----------------------------------------
// The rewrite above fixed the vocabulary and left the shape: a dead end that
// apologised politely. Every one of the twelve call sites rendered a paragraph
// and stopped. The `action` prop existed and exactly one caller in the codebase
// ever passed it.
//
// The test now is: if a mentor were sitting with this student, what would they
// say NEXT? Not "we have not researched that" — they would say "not my area,
// but go and talk to so-and-so", and they would point. So every state carries a
// destination, the destination is rendered whether or not the caller thought
// about it, and a caller that wants a better one passes `action`.
//
// Choosing those destinations needs one piece of care. NOT_DEPLOYED and EMPTY
// mean the researched projection is unreachable, so they must not point at
// /knowledge — that is the surface that just failed. They point at the editorial
// pages, which are static and work regardless: ranked business ideas and the
// fourteen written district profiles.
//
// The rule: say what they can do next, never why our infrastructure is unhappy.
import Link from "next/link";

//: SCHEMA_UNREACHABLE is what lib/knowledge.js `knowledgeAvailable()` returns —
//: the same condition as NOT_DEPLOYED, named from the client's point of view.
const ALIASES = { SCHEMA_UNREACHABLE: "NOT_DEPLOYED", NO_MATCHES: "NO_MATCH" };

export const EMPTY_STATES = [
  "NOT_DEPLOYED",
  "EMPTY",
  "NO_MATCH",
  "NOT_AVAILABLE_YET",
  "NO_DATA_SOURCE",
];

export function normaliseReason(reason) {
  const key = String(reason || "").toUpperCase();
  return ALIASES[key] || key;
}

//: Where each state sends the reader. `/opportunity-radar` and `/districts` are
//: built from lib/radar-data.js and lib/districts-data.js, so they still have
//: something to show on the exact days the researched projection does not.
//: Short enough to sit on one line in a pill button at 390px. The first draft
//: read "See business ideas ranked for your area", which wrapped to two lines
//: inside the button on every phone.
const RADAR = { href: "/opportunity-radar", label: "Browse business ideas" };
const EXPLORE = { href: "/knowledge", label: "Browse our research" };

export function emptyStateCopy(reason, { entityLabel = "information", query, dependency } = {}) {
  const key = normaliseReason(reason);

  const states = {
    // Our infrastructure, not their problem. NOT_DEPLOYED and EMPTY are
    // different to us and identical to them: more is on the way, and there is
    // something worth reading in the meantime.
    NOT_DEPLOYED: {
      title: "More is on the way",
      body:
        "We are adding districts, skills, schemes and business ideas all the time. " +
        "Here is something you can look at right now.",
      nextStep: RADAR,
      operatorNote:
        "Research database not connected in this environment — see the operations runbook.",
    },
    EMPTY: {
      title: "More is on the way",
      body:
        "Our researchers have gathered this and it is not published here yet. " +
        "In the meantime, here is where most people start.",
      nextStep: RADAR,
      operatorNote: "Research database connected but empty — the data load has not run.",
    },
    NO_MATCH: {
      title: query ? `No match for “${query}” yet` : `More ${entityLabel} coming soon`,
      body: query
        ? "Try a shorter word or a different spelling. We add new opportunities " +
          "every few weeks, so it is worth looking again."
        : `New ${entityLabel} are added as our research grows. Have a look at what ` +
          "is already here.",
      nextStep: EXPLORE,
      operatorNote: null,
    },
    NOT_AVAILABLE_YET: {
      title: "Coming soon",
      body:
        "We are building this part of ValueWeave. Plenty is ready today, and this " +
        "will join it.",
      nextStep: EXPLORE,
      operatorNote: null,
    },
    NO_DATA_SOURCE: {
      title: "Coming soon",
      body:
        "Our team is researching this area now. New industries and opportunities " +
        "are added regularly.",
      nextStep: EXPLORE,
      operatorNote: null,
    },
  };

  const copy = states[key] || {
    title: `More ${entityLabel} coming soon`,
    body: "New entries are added as our research grows.",
    nextStep: EXPLORE,
    operatorNote: null,
  };

  // `dependency` used to be rendered. It is now an operator note: the caller may
  // still pass the precise missing dataset, and it stays out of the user's way.
  return { ...copy, key, operatorNote: dependency || copy.operatorNote };
}

/**
 * `action` is the way out, and there is always one.
 *
 * A caller that knows a better destination than the default should pass
 * `action` — a search box that just failed can offer the query it would have
 * worked for, a district page can offer the district next door. A caller that
 * passes nothing still gets a link, because the alternative is a panel with
 * nowhere to go, and a dead end is what makes a site feel broken even when it
 * is behaving correctly.
 */
export default function KnowledgeEmptyState({
  reason,
  entityLabel = "information",
  query,
  dependency,
  note,
  action,
}) {
  const copy = emptyStateCopy(reason, { entityLabel, query, dependency });

  return (
    <div
      data-testid="knowledge-empty"
      data-reason={copy.key}
      // Kept in the DOM, never on the screen: support can read it from the
      // element inspector, and tests can assert on it, without a student ever
      // meeting the word "schema".
      data-operator-note={copy.operatorNote || undefined}
      className="card-base p-8 text-center flex flex-col items-center gap-1.5"
    >
      <p className="font-display font-bold text-ink">{copy.title}</p>
      <p className="text-sm text-muted max-w-md mx-auto">{note || copy.body}</p>
      {action || (
        <Link
          href={copy.nextStep.href}
          data-testid="knowledge-empty-next"
          className="btn-secondary text-sm mt-3"
        >
          {copy.nextStep.label} →
        </Link>
      )}
    </div>
  );
}
