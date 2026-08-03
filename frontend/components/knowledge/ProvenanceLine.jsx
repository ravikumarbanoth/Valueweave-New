// Where a fact came from.
//
// WHAT THIS USED TO SHOW
// ----------------------
//     Package008_MSME · businesses.csv · B-014
//
// in a 10px monospace font, under every card on the site. Three internal
// identifiers — a repository directory, a filename and a row key — presented to
// a student as if they were a citation. Nobody outside this codebase can do
// anything with any of them.
//
// WHAT IT SHOWS NOW
//     From our small business research
//
// The identifiers are not deleted. They stay on the element as data attributes,
// so support can read them from an inspector and a bug report can quote them,
// and the full string is still the `title` for anyone who hovers. What a reader
// SEES is the one part that carries meaning: a person gathered this from a public
// source, and here is which team.
//
// The claim that matters — "this is researched, not invented" — is made by
// SourceBadge and ConfidenceBadge, which say it in words a reader can use.
import { PACKAGE_LABELS } from "@/lib/knowledge";

//: `srOnly` keeps the element and its data attributes and drops the visible
//: text — for the one caller that already shows the same fact as a chip.
export default function ProvenanceLine({ package: pkg, dataset, rowId, srOnly = false, className = "" }) {
  if (!pkg && !dataset && !rowId) return null;

  const label = PACKAGE_LABELS[pkg];
  const text = label
    ? `From our ${label.toLowerCase()} research`
    : "From our published research";

  return (
    <p
      data-testid="provenance-line"
      data-source-package={pkg || undefined}
      data-source-dataset={dataset || undefined}
      data-source-row={rowId || undefined}
      className={srOnly ? "sr-only" : `text-[10px] text-stone-400 truncate ${className}`}
      title={[pkg, dataset, rowId].filter(Boolean).join(" / ")}
    >
      {text}
    </p>
  );
}
