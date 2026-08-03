// The masthead every knowledge detail page shares: name, type, confidence,
// provenance, source package.
//
// One component so the four detail surfaces (business, scheme, skill, district)
// cannot drift into four different ideas of how a knowledge claim is presented.
import Link from "next/link";
import ConfidenceBadge from "./ConfidenceBadge";
import ProvenanceLine from "./ProvenanceLine";
import SourceBadge from "./SourceBadge";

const TYPE_LABEL = {
  District: "District",
  Industry: "Industry",
  BusinessOpportunity: "Business opportunity",
  MSME: "MSME",
  Skill: "Skill",
  GovernmentScheme: "Government scheme",
  Crop: "Crop",
  Certification: "Certification",
  TrainingProvider: "Training provider",
  Institution: "Institution",
};

// PX Phase 8. Two changes from reading this header as a 17-year-old would.
//
// The back link said "← Knowledge Explorer". That is the name of a product
// area, and a student who arrived from a search result has never seen it —
// they cannot tell whether it goes back to their results, to a category, or
// somewhere new.
//
// And the source was stated twice, three lines apart: a "Skills & training
// research" chip, then "From our skills & training research" underneath it.
// Saying it once is provenance; saying it twice reads as a rendering fault
// and pushes the actual content further down the phone.
export default function EntityHeader({
  entity,
  detail,
  backHref = "/knowledge",
  backLabel = "Back to everything we have researched",
}) {
  if (!entity) return null;
  const unverified = String(entity.verification_status || "").includes("NEEDS_REVIEW");
  return (
    <header
      data-testid="entity-header"
      data-verification-status={unverified ? "NEEDS_REVIEW" : "VERIFIED"}
      className="flex flex-col gap-3"
    >
      <Link href={backHref} className="text-[12px] text-muted hover:text-ink w-fit">
        ← {backLabel}
      </Link>

      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-[11px] uppercase tracking-widest text-muted">
            {TYPE_LABEL[entity.entity_type] || entity.entity_type}
          </p>
          <h1 className="font-display font-bold text-2xl sm:text-3xl text-ink break-words">
            {entity.canonical_name}
          </h1>
        </div>
        <ConfidenceBadge confidence={entity.confidence_score} />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <SourceBadge sourcePackage={entity.source_package} />
        {detail?.category_name && <span className="chip">{detail.category_name}</span>}
      </div>

      {/* The visible half of this duplicated the SourceBadge above. The
          identifiers it carries are still wanted — support quotes them and
          tests assert on them — so the element stays and only its text goes:
          `data-source-package`, `data-source-dataset`, `data-source-row` and
          the hover title are all unchanged. */}
      <ProvenanceLine
        package={entity.source_package}
        dataset={detail?.data_source}
        rowId={entity.package_local_id}
        srOnly
      />

      {detail?.source_url && String(detail.source_url).startsWith("http") && (
        <a
          href={detail.source_url}
          target="_blank"
          rel="noopener noreferrer"
          data-testid="entity-source-link"
          className="text-[12px] text-muted underline hover:text-ink w-fit"
        >
          Official source ↗
        </a>
      )}

      {/* PX PHASE 3 — THE AMBER PANEL IS GONE FROM THE MASTHEAD
          ------------------------------------------------------
          It read: "This record has not yet been reviewed by a person. It was
          collected from a public source and machine-validated. Treat it as a
          starting point." — in alert amber, directly under the title, before
          the reader had learned a single fact about the thing they came for.

          The disclosure was worth making and the position was not: an alert
          above the content tells a student the page is unsafe, which is not
          what it meant. It now appears once per page as TrustPanel, after the
          facts, where "check the official site before you apply" is advice
          instead of a warning. `data-verification-status` keeps the machine
          answer here for support and for tests. */}
    </header>
  );
}
