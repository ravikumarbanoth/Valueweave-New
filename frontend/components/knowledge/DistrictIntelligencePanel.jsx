// Researched knowledge for one district, grouped by entity type.
//
// Sits BELOW the existing editorial district profile, never replacing it.
// lib/districts-data.js narrative is better writing than anything the graph can
// generate; the graph contributes sourced facts. Layer A owns the story, the
// knowledge platform owns the figures, and the labels say which is which.
//
// Coverage is uneven and the panel admits it: GENERATES_EMPLOYMENT holds 32 edges
// across 61 districts, so most districts show institutions and industries but few
// businesses. Rendering an empty section without explanation would read as "this
// district has no economy".
import KnowledgeCard from "./KnowledgeCard";
import KnowledgeCardGrid from "./KnowledgeCardGrid";
import TrustPanel from "./TrustPanel";
import Link from "next/link";
import { hrefFor } from "@/lib/knowledge";

const SECTIONS = [
  { type: "Industry", label: "Industries" },
  { type: "MSME", label: "MSMEs" },
  { type: "BusinessOpportunity", label: "Business opportunities" },
  { type: "GovernmentScheme", label: "Government schemes" },
  { type: "Institution", label: "Institutions" },
  { type: "Market", label: "Markets" },
  { type: "TrainingProvider", label: "Training providers" },
  { type: "Crop", label: "Agriculture" },
];

export default function DistrictIntelligencePanel({ districtName, grouped = {}, status, note, testId }) {
  const populated = SECTIONS.filter((s) => (grouped[s.type] || []).length > 0);
  const total = Object.values(grouped).reduce((n, rows) => n + rows.length, 0);

  return (
    <section data-testid={testId} className="card-base p-5 sm:p-7">
      <div className="mb-4">
        <span className="chip bg-teal-100 text-teal-700 border border-teal-200 mb-3">
          WHAT&apos;S HERE
        </span>
        <h2 className="font-display font-extrabold text-2xl text-ink">
          Opportunities in {districtName}
        </h2>
        <p className="text-sm text-muted mt-2 max-w-2xl leading-relaxed">
          Industries operating here, businesses you could start, schemes you may
          qualify for, places to train and crops that grow well. Each one links to
          the full details and names the source it came from.
        </p>
      </div>

      {total === 0 ? (
        <KnowledgeCardGrid
          status={status || "NO_DATA_SOURCE"}
          note={
            note ||
            `We are connecting our research to ${districtName} now. Plenty is already mapped in the districts around it — and you can also start from what you want to do rather than where you are.`
          }
          testId={testId && `${testId}-empty`}
        />
      ) : (
        <>
          <div data-testid="district-knowledge-depth"
               className="flex flex-wrap items-center justify-between gap-2 mb-4 text-[12px] text-muted">
            <span>
              <strong className="text-ink tabular-nums">{total}</strong>{" "}
              {total === 1 ? "thing" : "things"} to explore in {districtName}, across{" "}
              {populated.length} {populated.length === 1 ? "category" : "categories"}
            </span>
            <Link href="/district-opportunity-index" className="underline hover:text-ink">
              Compare districts →
            </Link>
          </div>
          <TrustPanel hasUnverified className="mb-5" />
          {populated.map((section) => {
            const rows = grouped[section.type] || [];
            return (
              <div key={section.type} className="mb-5 last:mb-0">
                <h3 className="label-display flex items-center gap-1.5">
                  {section.label}
                  <span className="text-stone-400 tabular-nums font-normal">{rows.length}</span>
                </h3>
                <KnowledgeCardGrid columns="sm:grid-cols-2 lg:grid-cols-3">
                  {rows.slice(0, 6).map((row) => (
                    <KnowledgeCard
                      key={row.global_entity_id}
                      testId={`district-${section.type}`}
                      title={row.canonical_name}
                      type={row._via ? row._via.replace(/_/g, " ").toLowerCase() : section.type}
                      confidence={row.confidence_score}
                      provenance={{
                        package: row.source_package,
                        rowId: row.package_local_id,
                      }}
                      href={hrefFor(row)}
                    />
                  ))}
                </KnowledgeCardGrid>
              </div>
            );
          })}
        </>
      )}
    </section>
  );
}
