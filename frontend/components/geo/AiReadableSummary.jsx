export default function AiReadableSummary({ title = "AI-readable summary", items = {}, faq = [] }) {
  const rows = Object.entries(items).filter(([, value]) => {
    if (Array.isArray(value)) return value.length > 0;
    return value != null && String(value).trim() !== "";
  });

  if (rows.length === 0 && (!faq || faq.length === 0)) return null;

  return (
    <section data-ai-readable="true" className="card-base p-5 mb-6 bg-amber-50/60 border-amber-200">
      <p className="label-display text-amber-700">{title}</p>
      <dl className="grid sm:grid-cols-2 gap-3 text-sm">
        {rows.map(([label, value]) => (
          <div key={label}>
            <dt className="font-display font-bold text-ink text-xs uppercase tracking-wider">{label}</dt>
            <dd className="text-muted mt-1 leading-relaxed">
              {Array.isArray(value) ? value.join(", ") : String(value)}
            </dd>
          </div>
        ))}
      </dl>
      {faq?.length > 0 && (
        <div data-ai-faq="true" className="mt-4 pt-4 border-t border-amber-200/70">
          <p className="font-display font-bold text-xs uppercase tracking-wider text-ink mb-2">FAQ</p>
          <div className="space-y-2">
            {faq.slice(0, 4).map((item, index) => (
              <div key={index} className="text-sm">
                <p className="font-semibold text-ink">{item.question}</p>
                <p className="text-muted leading-relaxed">{item.answer}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
