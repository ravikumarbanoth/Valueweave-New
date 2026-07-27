// Key/value display for a detail row from one of the projected knowledge tables.
//
// Skips empty cells and both sentinels. `PENDING_VERIFICATION` means the platform
// looked and could not confirm — rendering the literal string to a user would read
// as a data-quality bug rather than the honest gap it is, so the field is omitted
// and counted in the caller's "not yet verified" line instead.
const SENTINELS = new Set(["PENDING_VERIFICATION", "PENDING_GEOCODING"]);

export function isPresent(value) {
  const v = String(value ?? "").trim();
  return v.length > 0 && !SENTINELS.has(v);
}

export default function AttributeGrid({ fields = [], row, columns = 2 }) {
  if (!row) return null;
  const shown = fields.filter(([key]) => isPresent(row[key]));
  if (shown.length === 0) return null;
  return (
    <dl
      data-testid="attribute-grid"
      className={`grid gap-x-6 gap-y-3 ${columns === 3 ? "sm:grid-cols-3" : "sm:grid-cols-2"}`}
    >
      {shown.map(([key, label]) => (
        <div key={key} className="min-w-0">
          <dt className="text-[11px] uppercase tracking-widest text-muted">{label}</dt>
          <dd className="text-sm text-ink break-words">{String(row[key])}</dd>
        </div>
      ))}
    </dl>
  );
}
