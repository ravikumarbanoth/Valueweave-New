// The five empty states, named — Platform v3.0, Step 4.
//
// An empty knowledge surface has five distinct causes and they mean opposite
// things. Collapsing them into one blank panel is the single easiest way for this
// platform to mislead the person using it:
//
//   NOT_DEPLOYED        the backend exists, this environment has not deployed it
//   EMPTY               the schema is deployed but nothing has been synced into it
//   NO_MATCH            we looked, and the answer about the world is "nothing"
//   NOT_AVAILABLE_YET   the capability is not built — a roadmap item, not a bug
//   NO_DATA_SOURCE      no knowledge source exists for this at all
//
// The first two are our deployment problem. The third is a real answer. The last
// two are honest admissions of scope. A user who cannot tell them apart cannot
// tell whether to wait, to look elsewhere, or to stop trusting the platform.
//
// `dependency` is what has to be true for the state to change. Every state that
// is our fault names one, because "not available yet" without a reason is the
// "Coming Soon" chip this step exists to remove.

//: SCHEMA_UNREACHABLE is what lib/knowledge.js `knowledgeAvailable()` returns.
//: It is the same condition as NOT_DEPLOYED, named from the client's point of
//: view rather than the operator's. Aliased rather than renamed so existing
//: callers keep working.
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

export function emptyStateCopy(reason, { entityLabel = "knowledge", query, dependency } = {}) {
  const key = normaliseReason(reason);

  const states = {
    NOT_DEPLOYED: {
      title: "Not switched on for this deployment",
      body:
        "The knowledge schema has not been deployed to this environment. Nothing is " +
        "wrong with your account, and no data is missing — it simply has not been " +
        "projected here yet.",
      dependency:
        "Run the migrations, expose the `knowledge` schema, then " +
        "`scripts/run_sync.sh`. See docs/FIRST_DEPLOYMENT_CHECKLIST.md steps 5–10.",
    },
    EMPTY: {
      title: "Nothing has been synced yet",
      body:
        "The schema exists but holds no rows. 1,812 researched records are waiting " +
        "in Git for the projection to run.",
      dependency: "`scripts/run_sync.sh` has not been run against this database.",
    },
    NO_MATCH: {
      title: query ? `No ${entityLabel} matches “${query}”` : `No ${entityLabel} found`,
      body: query
        ? "We searched the researched knowledge base and found nothing. That is a gap " +
          "in our data, not a mistake in your query."
        : "We looked and there is nothing here. That is an answer about our coverage, " +
          "not an error.",
      dependency: null,
    },
    NOT_AVAILABLE_YET: {
      title: "Not available yet",
      body: "This capability is not built. It is on the roadmap, not in the product.",
      dependency: null,
    },
    NO_DATA_SOURCE: {
      title: "No knowledge source for this yet",
      body:
        "Nothing in Packages 001–008 covers this. It is not a sync gap or a " +
        "deployment gap — the research has not been collected.",
      dependency: null,
    },
  };

  const copy = states[key] || {
    title: `No ${entityLabel} available`,
    body: "Nothing to show here yet.",
    dependency: null,
  };

  // A caller-supplied dependency always wins: it knows the specific missing
  // dataset, and the generic text only knows the category of problem.
  return { ...copy, key, dependency: dependency || copy.dependency };
}

export default function KnowledgeEmptyState({
  reason,
  entityLabel = "knowledge",
  query,
  dependency,
  note,
}) {
  const copy = emptyStateCopy(reason, { entityLabel, query, dependency });

  return (
    <div
      data-testid="knowledge-empty"
      data-reason={copy.key}
      className="card-base p-8 text-center flex flex-col gap-1.5"
    >
      <p className="font-display font-bold text-ink">{copy.title}</p>
      <p className="text-sm text-muted max-w-md mx-auto">{note || copy.body}</p>
      {copy.dependency && (
        <p
          data-testid="knowledge-empty-dependency"
          className="text-[11px] text-stone-400 max-w-md mx-auto mt-1.5 leading-relaxed"
        >
          <span className="font-display font-bold text-stone-500">Depends on: </span>
          {copy.dependency}
        </p>
      )}
    </div>
  );
}
