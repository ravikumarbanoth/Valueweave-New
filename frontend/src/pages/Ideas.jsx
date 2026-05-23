import React from "react";
import { useSearchParams } from "react-router-dom";
import { Search, X, SlidersHorizontal } from "lucide-react";
import { fetchIdeas, fetchIdeaFilters } from "@/lib/api";
import IdeaCard from "@/components/IdeaCard";

export default function Ideas() {
  const [params, setParams] = useSearchParams();
  const [ideas, setIdeas] = React.useState([]);
  const [filters, setFilters] = React.useState({ sectors: [], execution_types: [], ideal_for: [], investment_buckets: [] });
  const [loading, setLoading] = React.useState(true);
  const [showFilters, setShowFilters] = React.useState(false);

  const sector = params.get("sector") || "";
  const execution_type = params.get("execution_type") || "";
  const ideal_for = params.get("ideal_for") || "";
  const investment_bucket = params.get("investment_bucket") || "";
  const beginner = params.get("beginner") === "1";
  const q = params.get("q") || "";

  React.useEffect(() => {
    fetchIdeaFilters().then(setFilters).catch(() => {});
  }, []);

  React.useEffect(() => {
    setLoading(true);
    const queryParams = {};
    if (sector) queryParams.sector = sector;
    if (execution_type) queryParams.execution_type = execution_type;
    if (ideal_for) queryParams.ideal_for = ideal_for;
    if (investment_bucket) queryParams.investment_bucket = investment_bucket;
    if (beginner) queryParams.beginner_friendly = true;
    if (q) queryParams.q = q;
    fetchIdeas(queryParams).then((d) => { setIdeas(d); setLoading(false); }).catch(() => setLoading(false));
  }, [sector, execution_type, ideal_for, investment_bucket, beginner, q]);

  const updateParam = (key, value) => {
    const next = new URLSearchParams(params);
    if (!value) next.delete(key); else next.set(key, value);
    setParams(next, { replace: true });
  };
  const clearAll = () => setParams({}, { replace: true });
  const activeCount = [sector, execution_type, ideal_for, investment_bucket].filter(Boolean).length + (beginner ? 1 : 0);

  return (
    <div data-testid="ideas-page" className="vw-container py-8 md:py-12">
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-8">
        <div>
          <div className="vw-section-label mb-2">Idea Library</div>
          <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight leading-tight" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
            Find an idea you can actually build.
          </h1>
          <p className="text-muted-foreground mt-2 max-w-2xl">
            29+ Bharat-grounded businesses with investment tiers, team roles, district fit and government scheme eligibility.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              defaultValue={q}
              onChange={(e) => updateParam("q", e.target.value)}
              placeholder="Search ideas, sectors..."
              data-testid="ideas-search-input"
              className="pl-9 pr-3 py-2.5 rounded-full border border-border bg-card text-sm w-full md:w-64 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
            />
          </div>
          <button
            onClick={() => setShowFilters((v) => !v)}
            className="md:hidden vw-btn-outline py-2.5 px-4 text-sm"
            data-testid="ideas-filters-toggle"
          >
            <SlidersHorizontal className="h-4 w-4" />
            {activeCount > 0 && <span className="vw-chip bg-primary text-primary-foreground px-2 py-0">{activeCount}</span>}
          </button>
        </div>
      </div>

      {/* Filter chips bar */}
      <div className={`mb-6 ${showFilters ? "block" : "hidden md:block"}`} data-testid="ideas-filter-bar">
        <div className="flex gap-2 overflow-x-auto scrollbar-hide py-1">
          <FilterGroup label="Sector" testid="idea-filter-sector"
            value={sector} options={filters.sectors} onChange={(v) => updateParam("sector", v)} />
          <FilterGroup label="Execution" testid="idea-filter-execution"
            value={execution_type} options={filters.execution_types} onChange={(v) => updateParam("execution_type", v)} />
          <FilterGroup label="Ideal For" testid="idea-filter-ideal-for"
            value={ideal_for} options={filters.ideal_for} onChange={(v) => updateParam("ideal_for", v)} />
          <FilterGroup label="Investment" testid="idea-filter-investment"
            value={investment_bucket}
            options={filters.investment_buckets?.map((b) => b.key) || []}
            labelMap={Object.fromEntries((filters.investment_buckets || []).map((b) => [b.key, b.label]))}
            onChange={(v) => updateParam("investment_bucket", v)} />
          <button
            onClick={() => updateParam("beginner", beginner ? "" : "1")}
            data-testid="idea-filter-beginner"
            className={`whitespace-nowrap px-4 py-2 rounded-full text-sm font-semibold border transition-colors ${
              beginner ? "bg-primary text-white border-primary" : "bg-card border-border hover:border-primary/40"
            }`}
          >
            Beginner-friendly
          </button>
          {activeCount > 0 && (
            <button onClick={clearAll} data-testid="ideas-clear-filters" className="whitespace-nowrap px-4 py-2 rounded-full text-sm font-semibold text-muted-foreground hover:text-foreground">
              <X className="inline h-4 w-4 -mt-0.5" /> Clear all
            </button>
          )}
        </div>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[0,1,2,3,4,5].map((i) => <div key={i} className="vw-card p-7 h-64 animate-pulse bg-muted/40" />)}
        </div>
      ) : ideas.length === 0 ? (
        <EmptyState onClear={clearAll} />
      ) : (
        <>
          <div className="text-sm text-muted-foreground mb-4" data-testid="ideas-count-label">
            Showing <span className="font-semibold text-foreground">{ideas.length}</span> {ideas.length === 1 ? "idea" : "ideas"}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="ideas-grid">
            {ideas.map((idea) => <IdeaCard key={idea.slug} idea={idea} />)}
          </div>
        </>
      )}
    </div>
  );
}

function FilterGroup({ label, value, options, labelMap, onChange, testid }) {
  return (
    <div className="flex items-center gap-2 whitespace-nowrap" data-testid={testid}>
      <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground hidden md:inline">{label}:</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="px-3 py-2 rounded-full text-sm font-semibold border border-border bg-card hover:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/30"
        data-testid={`${testid}-select`}
      >
        <option value="">All {label.toLowerCase()}</option>
        {options.map((o) => <option key={o} value={o}>{labelMap?.[o] || o}</option>)}
      </select>
    </div>
  );
}

function EmptyState({ onClear }) {
  return (
    <div className="py-20 text-center max-w-md mx-auto" data-testid="ideas-empty-state">
      <img
        src="https://static.prod-images.emergentagent.com/jobs/9893adf9-2474-40a4-9829-2cf309a21e6b/images/92dfef1cdf5afcbea678066391cb02b1c8c84691c68aca8ad7d14b770d43cf05.png"
        alt="No ideas found"
        className="mx-auto h-40 w-40 object-contain mb-6"
      />
      <h3 className="text-xl font-bold mb-2" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
        No ideas match these filters
      </h3>
      <p className="text-muted-foreground mb-6">Try removing a filter or searching for a different keyword.</p>
      <button onClick={onClear} className="vw-btn-primary" data-testid="ideas-empty-clear-btn">Clear filters</button>
    </div>
  );
}
