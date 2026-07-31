// Skills a group has, skills it needs, and skills we have no data on.
//
// The third column is the one that matters. Roughly 50 skills that users are
// actively invited to claim have no researched counterpart in the knowledge base
// (see governance/vocabulary — Step 0). Dropping them would silently say "this
// person has no skills"; showing them says "we have not collected data on theirs",
// which is the truth and is also the collection backlog.
export default function SkillGapPanel({ have = [], need = [], noData = [], title = "Skill coverage", testId }) {
  const nothing = have.length === 0 && need.length === 0 && noData.length === 0;

  return (
    <section data-testid={testId} className="card-base p-5">
      <h3 className="font-display font-extrabold text-base text-ink mb-3">{title}</h3>

      {nothing ? (
        <p className="text-xs text-muted">
          No skills recorded yet on either side, so there is no gap to compute.
        </p>
      ) : (
        <div className="grid sm:grid-cols-3 gap-4">
          <Column
            label="Covered"
            tone="bg-teal-50 text-teal-700 border-teal-200"
            items={have}
            empty="Nothing covered yet."
          />
          <Column
            label="Still needed"
            tone="bg-amber-50 text-amber-700 border-amber-200"
            items={need}
            empty="Nothing outstanding."
          />
          <Column
            label="Not gathered yet"
            tone="bg-stone-100 text-stone-500 border-stone-200"
            items={noData}
            empty="All skills resolved."
            hint="Real skills the knowledge base has not collected yet — not a judgement on the person."
          />
        </div>
      )}
    </section>
  );
}

function Column({ label, tone, items, empty, hint }) {
  return (
    <div>
      <h4 className="label-display flex items-center gap-1.5">
        {label}
        <span className="text-stone-400 tabular-nums font-normal">{items.length}</span>
      </h4>
      {items.length === 0 ? (
        <p className="text-xs text-stone-400">{empty}</p>
      ) : (
        <div className="flex flex-wrap gap-1.5">
          {items.map((s) => (
            <span key={s} className={`chip border ${tone} text-[11px]`}>
              {s}
            </span>
          ))}
        </div>
      )}
      {hint && items.length > 0 && (
        <p className="text-[10px] text-stone-400 mt-2 leading-relaxed">{hint}</p>
      )}
    </div>
  );
}
