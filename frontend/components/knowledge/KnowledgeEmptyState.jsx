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
// The rule: say what they can do next, never why our infrastructure is unhappy.

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

export function emptyStateCopy(reason, { entityLabel = "information", query, dependency } = {}) {
  const key = normaliseReason(reason);

  const states = {
    // Our infrastructure, not their problem. NOT_DEPLOYED and EMPTY are
    // different to us and identical to them: the information is on its way.
    NOT_DEPLOYED: {
      title: "This information is being prepared",
      body:
        "We are still connecting this part of ValueWeave. Nothing is wrong with " +
        "your account, and nothing you did caused this. Try again shortly.",
      operatorNote:
        "Research database not connected in this environment — see the operations runbook.",
    },
    EMPTY: {
      title: "This information is being prepared",
      body:
        "Our researchers have gathered this and it is not published here yet. " +
        "Check back soon.",
      operatorNote: "Research database connected but empty — the data load has not run.",
    },
    NO_MATCH: {
      title: query ? `Nothing matches “${query}” yet` : `No ${entityLabel} to show yet`,
      body: query
        ? "We searched everything we have researched and found nothing for this. " +
          "Try a shorter word, or browse by category instead."
        : "We have not researched anything for this yet. It is a gap on our side, " +
          "not a mistake on yours.",
      operatorNote: null,
    },
    NOT_AVAILABLE_YET: {
      title: "Not available yet",
      body:
        "We have not built this part of ValueWeave. It is on our list, and it is " +
        "not something you are missing out on today.",
      operatorNote: null,
    },
    NO_DATA_SOURCE: {
      title: "We have not researched this yet",
      body:
        "Our team gathers information from official public sources, and we have " +
        "not covered this area yet. When we do, it will appear here.",
      operatorNote: null,
    },
  };

  const copy = states[key] || {
    title: `No ${entityLabel} to show`,
    body: "There is nothing here yet.",
    operatorNote: null,
  };

  // `dependency` used to be rendered. It is now an operator note: the caller may
  // still pass the precise missing dataset, and it stays out of the user's way.
  return { ...copy, key, operatorNote: dependency || copy.operatorNote };
}

/**
 * `action` is the way out. Every state that can offer one should — an empty
 * panel with nowhere to go is a dead end, and a dead end is what makes a site
 * feel broken even when it is behaving correctly.
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
      {action}
    </div>
  );
}
