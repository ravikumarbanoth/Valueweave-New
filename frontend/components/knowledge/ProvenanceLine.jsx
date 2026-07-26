// Where a knowledge row came from: package · dataset · row id.
//
// Not decoration. The platform's first principle is that an answer which cannot
// name its source is not an answer, and this is the component that keeps that
// promise on screen.
export default function ProvenanceLine({ package: pkg, dataset, rowId, className = "" }) {
  const parts = [pkg, dataset, rowId].filter(Boolean);
  if (parts.length === 0) return null;
  return (
    <p
      className={`text-[10px] text-stone-400 font-mono truncate ${className}`}
      title={`Sourced from ${parts.join(" / ")}`}
    >
      {parts.join(" · ")}
    </p>
  );
}
