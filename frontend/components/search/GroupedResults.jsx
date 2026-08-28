// Results, arranged the way a person reads them.
//
// WHAT THIS REPLACED
// ------------------
// One flat grid of up to twenty-four cards, districts and skills and schemes
// and business ideas interleaved by score. Every card looked the same, so the
// only way to find the scheme in the list was to read all of it — and the
// reader had to hold "which of these is a place and which is a thing I could
// learn" in their head while doing it.
//
// The information was there. The shape was a table dump.
//
// SECTIONS ARE ORDERED BY THEIR BEST RESULT, NOT BY A FIXED LIST
// --------------------------------------------------------------
// "Medak" must lead with Places and "PMEGP" with Government support, and no
// static order is right for both. See groupResults in lib/search/universal.js;
// the fixed order only breaks ties.
import Link from "next/link";
import ConfidenceBadge from "@/components/knowledge/ConfidenceBadge";

//: A research article is not a knowledge row and should not be dressed as one.
//: It has no confidence score — the idea does not apply to an essay — and it
//: has a reading time and a summary, which no entity does.
function isArticle(row) {
  return row.entity_type === "ResearchArticle";
}

export default function GroupedResults({ groups, total, query, resolved, analysis }) {
  return (
    <div className="flex flex-col gap-6" data-testid="search-results">
      <div className="flex flex-col gap-2">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <p className="text-[13px] text-muted" data-testid="search-count">
            {total} {total === 1 ? "result" : "results"} for “{query}”
          </p>
          {/* A Telugu speaker who typed "పాడి పరిశ్రమ" and sees English cards
              has no way to tell whether we understood them or guessed. This is
              the difference between a search engine and a slot machine. */}
          {resolved && (
            <p className="text-[12px] text-stone-500" data-testid="search-resolved">
              Understood as <span className="font-display font-bold text-ink">{resolved}</span>
            </p>
          )}
        </div>
        {analysis?.intent && analysis.intent !== "unknown" && (
          <div className="text-[12px] text-stone-500" data-testid="search-intent">
            Detected intent: <span className="font-display font-bold text-ink">{analysis.intentLabel}</span>.
            {analysis.gaps?.length > 0 && (
              <span> We have no {analysis.gaps.join(" and ")} for this query yet.</span>
            )}
          </div>
        )}
      </div>

      {groups.map((group) => (
        <section key={group.id} data-testid="search-group" data-group={group.id}>
          <div className="flex items-baseline justify-between gap-3 mb-2">
            <h2 className="font-display font-bold text-ink text-[15px]">{group.label}</h2>
            {group.total > group.items.length && (
              <span className="text-[11px] text-muted">
                showing {group.items.length} of {group.total}
              </span>
            )}
          </div>

          <ul className="grid gap-3 sm:grid-cols-2" data-testid="search-list">
            {group.items.map((row) => (
              <li key={row.global_entity_id}>
                <Link
                  href={row._href || "/knowledge"}
                  data-testid="search-item"
                  data-entity-type={row.entity_type}
                  className="card-base p-4 flex flex-col gap-2 h-full hover:border-stone-300 transition-colors"
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-display font-bold text-ink text-[15px] leading-snug">
                      {row.canonical_name}
                    </span>
                    {isArticle(row)
                      ? <span className="chip bg-teal-50 text-teal-700 border border-teal-200 shrink-0">
                          Read
                        </span>
                      : <ConfidenceBadge confidence={row.confidence_score} />}
                  </div>

                  {isArticle(row) && row._summary && (
                    <p className="text-[12px] text-muted line-clamp-2">{row._summary}</p>
                  )}

                  {/* Why a result that does not contain the typed word is
                      here. Without this, "electrician" returning "Power
                      Distribution Technician" looks like a bug rather than
                      the point of the whole vocabulary layer. */}
                  {row._via && (
                    <p className="text-[11px] text-stone-400" data-testid="search-via">
                      matched “{row._via}”
                    </p>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}
