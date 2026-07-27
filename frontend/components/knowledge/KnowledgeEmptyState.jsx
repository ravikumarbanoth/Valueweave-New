// The three empty states, named.
//
// An empty knowledge surface has three distinct causes and they mean opposite
// things. NOT_DEPLOYED is our deployment gap, EMPTY is a sync that has not run,
// NO_MATCH is a real answer about the world. Collapsing them into one blank panel
// is the single easiest way for this platform to mislead the person using it.
export default function KnowledgeEmptyState({ reason, entityLabel = "knowledge", query }) {
  const copy = {
    SCHEMA_UNREACHABLE: {
      title: "Knowledge base not connected yet",
      body:
        "The knowledge schema has not been deployed to this environment. Nothing is " +
        "wrong with your account — see docs/DEPLOYMENT_CHECKLIST.md §4.",
    },
    EMPTY: {
      title: "Knowledge base is empty",
      body:
        "The schema exists but no data has been synced into it yet. 1,812 researched " +
        "rows are waiting in Git.",
    },
    NO_MATCH: {
      title: query ? `No ${entityLabel} matches “${query}”` : `No ${entityLabel} yet`,
      body: query
        ? "We searched the researched knowledge base and found nothing. That is a gap in our data, not in your query."
        : "Nothing has been researched for this yet.",
    },
  }[reason] || {
    title: `No ${entityLabel} available`,
    body: "Nothing to show here yet.",
  };

  return (
    <div data-testid="knowledge-empty" data-reason={reason}
         className="card-base p-8 text-center flex flex-col gap-1.5">
      <p className="font-display font-bold text-ink">{copy.title}</p>
      <p className="text-sm text-muted max-w-md mx-auto">{copy.body}</p>
    </div>
  );
}
