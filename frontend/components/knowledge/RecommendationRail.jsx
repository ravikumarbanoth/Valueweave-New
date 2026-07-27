// One horizontal rail of recommendations on the dashboard.
//
// Every rail shows WHY. That is the difference between a recommendation engine and
// a shuffle: `reason` comes straight from the rule that fired, so a user can
// disagree with it, and a support engineer can trace it to a CSV row.
import KnowledgeCard from "./KnowledgeCard";
import KnowledgeCardGrid from "./KnowledgeCardGrid";
import { hrefFor } from "@/lib/knowledge";

// Every recommendation must reach a detail page (Step 3, Priority 1).
//
// Graph-backed categories carry the `global_entity_id` in `item_id` — the engine
// emits `vw:governmentscheme:pmegp`, not an opaque key — so `hrefFor()` resolves
// them with no lookup. Editorial and Supabase-backed categories keep their own
// prefixed ids and their own routes.
const HREF_BUILDERS = {
  business_ideas: (r) =>
    r.item_id?.startsWith("idea:") ? `/ideas/${r.item_id.slice(5)}` : graphHref(r),
  government_schemes: graphHref,
  msmes: graphHref,
  industries: graphHref,
  markets: graphHref,
  courses: graphHref,
  collaborators: (r) =>
    r.item_id?.startsWith("user:") ? `/profile/${r.item_id.slice(5)}` : null,
  research: (r) =>
    r.item_id?.startsWith("article:") ? `/research/${r.item_id.slice(8)}` : null,
};

function graphHref(r) {
  if (!r?.item_id?.startsWith("vw:")) return null;
  return hrefFor({ global_entity_id: r.item_id, entity_type: r.item_type });
}

export default function RecommendationRail({
  title,
  subtitle,
  category,
  items = [],
  status,
  note,
  limit = 6,
  testId,
}) {
  const shown = (items || []).slice(0, limit);
  const build = HREF_BUILDERS[category] || (() => null);

  return (
    <section className="mb-6" data-testid={testId}>
      <div className="flex items-baseline justify-between gap-3 mb-3">
        <div>
          <h2 className="font-display font-extrabold text-lg text-ink">{title}</h2>
          {subtitle && <p className="text-xs text-muted mt-0.5">{subtitle}</p>}
        </div>
        {shown.length > 0 && (
          <span className="text-xs text-stone-400 tabular-nums shrink-0">
            {items.length} found
          </span>
        )}
      </div>

      <KnowledgeCardGrid status={status} note={note} testId={testId && `${testId}-grid`}>
        {shown.map((r) => {
          const prov = (r.supporting_entities || []).find(
            (e) => e.source_package || e.source_dataset
          );
          return (
            <KnowledgeCard
              key={`${r.category}-${r.item_id}`}
              testId={`rec-${r.category}`}
              title={r.item_label}
              type={r.item_type}
              reason={r.reason}
              confidence={r.confidence}
              matchScore={r.match_score}
              href={build(r)}
              provenance={
                prov && {
                  package: prov.source_package,
                  dataset: prov.source_dataset,
                  rowId: prov.source_row_id,
                }
              }
            />
          );
        })}
      </KnowledgeCardGrid>
    </section>
  );
}
