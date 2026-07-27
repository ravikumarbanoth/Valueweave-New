// Which package a knowledge item came from.
//
// The brief requires every displayed knowledge item to name its source package.
// This is that, and it is deliberately a plain chip rather than a link: the
// package is provenance, not a destination — there is no package browse page and
// inventing one would be a duplicate surface.
import { PACKAGE_LABELS } from "@/lib/knowledge";

export default function SourceBadge({ sourcePackage, className = "" }) {
  if (!sourcePackage) return null;
  const label = PACKAGE_LABELS[sourcePackage] || sourcePackage;
  return (
    <span
      data-testid="source-badge"
      title={`Researched and released in ${sourcePackage}`}
      className={`chip text-[11px] whitespace-nowrap ${className}`}
    >
      {label}
    </span>
  );
}
