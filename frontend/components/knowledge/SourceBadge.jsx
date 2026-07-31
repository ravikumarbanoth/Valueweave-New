// Which area of our research a fact came from.
//
// Every item we show names where it came from — that is the platform's first
// promise and it stays. What changed is the wording: the chip used to read
// "Package006 · Skills & Training" and now reads "Skills & training research".
// A reader learns the same thing and is not handed a directory name.
//
// Deliberately a plain chip and not a link: this is provenance, not a
// destination. There is no browse-by-research-area page and inventing one would
// be a duplicate surface.
import { PACKAGE_LABELS } from "@/lib/knowledge";

export default function SourceBadge({ sourcePackage, className = "" }) {
  if (!sourcePackage) return null;
  const label = PACKAGE_LABELS[sourcePackage] || sourcePackage;
  return (
    <span
      data-testid="source-badge"
      data-source-package={sourcePackage}
      title={`Gathered by our ${label.toLowerCase()} research team from official public sources`}
      className={`chip text-[11px] whitespace-nowrap ${className}`}
    >
      {label} research
    </span>
  );
}
