"use client";

import { useMemo, useState } from "react";
import Link from "next/link";

const SEARCH_FIELDS = [
  "name",
  "source_name",
  "acronym",
  "description",
  "supplemental_notes",
  "display_category",
  "record_kind",
  "organisation_type",
];

function includesQuery(record, query) {
  if (!query) return true;
  const haystack = SEARCH_FIELDS.map((field) => record[field] || "").join(" ").toLowerCase();
  return haystack.includes(query.toLowerCase());
}

export default function SchemeSupportDirectory({ records, categories, metadata, graphItems = [] }) {
  const [activeCategory, setActiveCategory] = useState("All");
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    return records.filter((record) => {
      const inCategory = activeCategory === "All" || record.display_category === activeCategory;
      return inCategory && includesQuery(record, query.trim());
    });
  }, [records, activeCategory, query]);

  return (
    <main className="min-h-screen bg-cream font-body pb-16">
      <section className="bg-ink text-white px-4 sm:px-6 py-14">
        <div className="max-w-5xl mx-auto">
          <span className="chip bg-amber-500/20 text-amber-300 border border-amber-500/30 mb-4">SCHEMES</span>
          <h1 className="font-display font-extrabold tracking-tight text-3xl sm:text-4xl md:text-5xl leading-tight mb-4">
            Schemes and Support Resources
          </h1>
          <p className="text-white/65 max-w-2xl leading-relaxed">
            Browse government schemes, training centres, entrepreneurship support, awareness portals, and grievance resources across India and Telangana.
          </p>
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        <div className="card-base p-4 md:p-5 mb-5">
          <label htmlFor="scheme-support-search" className="text-sm font-display font-semibold text-ink">
            Search by name, acronym, category, description, or notes
          </label>
          <input
            id="scheme-support-search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Try PMMY, RSETI, grievance, digital literacy..."
            className="mt-2 w-full rounded-xl border border-stone-200 bg-white px-4 py-3 text-sm text-ink outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-200"
            data-testid="scheme-support-search"
          />
          <div className="mt-4 flex flex-wrap gap-2" data-testid="scheme-support-filters">
            {["All", ...categories].map((category) => (
              <button
                key={category}
                type="button"
                onClick={() => setActiveCategory(category)}
                className={`chip border transition-colors min-h-[44px] ${
                  activeCategory === category
                    ? "bg-ink text-white border-ink"
                    : "bg-white text-muted border-stone-200 hover:border-amber-400 hover:text-ink"
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        <div className="mb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 text-sm text-muted">
          <p data-testid="scheme-support-count">
            Showing {filtered.length} of {metadata.recordCount} schemes and support resources
          </p>
          <p>Verify current eligibility and terms on the official portal before applying.</p>
        </div>

        {filtered.length === 0 ? (
          <div className="card-base p-10 text-center">
            <h2 className="font-display font-bold text-xl text-ink mb-2">No matching resources</h2>
            <p className="text-muted text-sm max-w-md mx-auto">Try a full name, acronym, category, or a broader keyword.</p>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((record) => (
              <Link
                key={record.resource_id}
                href={`/schemes/${record.slug}`}
                className="card-base p-5 hover:border-amber-400 hover:shadow-md hover:-translate-y-1 transition-all"
              >
                <div className="flex flex-wrap items-center gap-2 mb-3">
                  <span className="chip bg-amber-50 text-amber-700">{record.display_category}</span>
                  <span className="chip bg-teal-50 text-teal-700">{record.record_kind}</span>
                </div>
                <h2 className="font-display font-bold text-lg text-ink mb-2 line-clamp-2 break-words">{record.name}</h2>
                {record.acronym && record.acronym !== record.name && (
                  <p className="text-xs font-semibold uppercase tracking-wide text-muted mb-2">{record.acronym}</p>
                )}
                <p className="text-sm text-muted leading-relaxed line-clamp-3">
                  {record.description || "Summary details are not listed in this directory entry yet. Check the official portal for programme information."}
                </p>
                {!record.official_website && (
                  <p className="mt-3 text-xs text-stone-500">Official portal link not listed yet</p>
                )}
              </Link>
            ))}
          </div>
        )}

        {graphItems.length > 0 && (
          <div className="mt-12">
            <div className="mb-4">
              <h2 className="font-display font-bold text-2xl text-ink">Additional Government Schemes</h2>
              <p className="text-sm text-muted mt-1">
                Explore detailed guides for central and state government schemes across agriculture, education, livelihoods, and social welfare.
              </p>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {graphItems.map((item) => (
                <Link
                  key={item.id}
                  href={item.href}
                  className="card-base p-5 hover:border-amber-400 hover:shadow-md hover:-translate-y-1 transition-all"
                >
                  <span className="chip bg-amber-50 text-amber-700 mb-3">Government scheme</span>
                  <h3 className="font-display font-bold text-lg text-ink mb-2 line-clamp-2">{item.name}</h3>
                  <p className="text-sm text-muted leading-relaxed line-clamp-3">
                    {item.summary || item.description || item.meta_description || "Open this scheme guide for eligibility and benefit details."}
                  </p>
                </Link>
              ))}
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
