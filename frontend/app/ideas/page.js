"use client";
import { useMemo, useState } from "react";
import Link from "next/link";
import {
  IDEAS, SECTORS, BUCKETS, PRIORITY_DISTRICTS, INVESTMENT_RANGES, ALL_TAGS,
  formatINR, getSector, getInvestmentRange,
} from "@/lib/idea-library";
import AppNavbar from "@/components/AppNavbar";
import { Search, MapPin, Sparkles, SlidersHorizontal, X } from "lucide-react";

const BUCKET_COLOR = {
  "local-physical": "bg-amber-100 text-amber-800",
  "hybrid":         "bg-teal-100 text-teal-800",
  "digital":        "bg-blue-100 text-blue-800",
  "future":         "bg-violet-100 text-violet-800",
};

const SORTS = [
  { id: "default",      label: "Recommended" },
  { id: "invest-asc",   label: "Lowest investment" },
  { id: "invest-desc",  label: "Highest investment" },
  { id: "revenue-desc", label: "Highest revenue" },
  { id: "az",           label: "A–Z" },
];

export default function IdeasPage() {
  const [search, setSearch] = useState("");
  const [sector, setSector] = useState("");
  const [bucket, setBucket] = useState("");
  const [district, setDistrict] = useState("");
  const [invest, setInvest] = useState("");
  const [tag, setTag] = useState("");
  const [beginnerOnly, setBeginnerOnly] = useState(false);
  const [sort, setSort] = useState("default");
  const [moreOpen, setMoreOpen] = useState(false);

  const ideas = useMemo(() => {
    const matches = (i) => {
      if (sector && i.sector !== sector) return false;
      if (bucket && i.bucket !== bucket) return false;
      if (district && !i.district_fit.includes(district)) return false;
      if (invest) {
        const r = getInvestmentRange(i);
        if (!r || r.id !== invest) return false;
      }
      if (tag && !i.tags.includes(tag)) return false;
      if (beginnerOnly && !i.beginner_friendly) return false;
      if (search.trim()) {
        const s = search.toLowerCase();
        return (
          i.title.toLowerCase().includes(s) ||
          i.short_description.toLowerCase().includes(s) ||
          i.tags.some((t) => t.toLowerCase().includes(s)) ||
          i.skills_needed.some((k) => k.toLowerCase().includes(s))
        );
      }
      return true;
    };
    const out = IDEAS.filter(matches);
    const by = {
      "invest-asc":   (a, b) => a.investment_min - b.investment_min,
      "invest-desc":  (a, b) => b.investment_min - a.investment_min,
      "revenue-desc": (a, b) => b.monthly_revenue_max - a.monthly_revenue_max,
      "az":           (a, b) => a.title.localeCompare(b.title),
    };
    return by[sort] ? [...out].sort(by[sort]) : out;
  }, [search, sector, bucket, district, invest, tag, beginnerOnly, sort]);

  // Count ideas per investment range so empty ranges can be disabled.
  const investCounts = useMemo(() => {
    const c = {};
    for (const i of IDEAS) {
      const r = getInvestmentRange(i);
      if (r) c[r.id] = (c[r.id] || 0) + 1;
    }
    return c;
  }, []);

  const activeCount =
    (sector ? 1 : 0) + (bucket ? 1 : 0) + (district ? 1 : 0) +
    (invest ? 1 : 0) + (tag ? 1 : 0) + (beginnerOnly ? 1 : 0);

  const clearAll = () => {
    setSector(""); setBucket(""); setDistrict("");
    setInvest(""); setTag(""); setBeginnerOnly(false); setSearch("");
  };

  return (
    <div className="min-h-screen bg-cream pb-24 md:pb-16 font-body">
      <AppNavbar />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        <header className="mb-6">
          <span className="chip bg-amber-100 text-amber-700 mb-3">IDEA LIBRARY · BETA</span>
          <h1 data-testid="ideas-title" className="font-display font-extrabold text-3xl sm:text-4xl tracking-tight mb-2">
            Start something <span className="text-amber-500">real.</span>
          </h1>
          <p className="text-muted text-base max-w-2xl">
            A growing library of practical, Bharat-grounded business ideas. Pick one that fits your district, skills, and budget — then post it as an opportunity and find collaborators.
          </p>
        </header>

        {/* Filter panel — sticky under the navbar so it stays reachable while scrolling */}
        <div className="card-base p-3 sm:p-4 mb-5 sticky top-16 z-30 bg-cream/95 backdrop-blur-md">
          <div className="relative mb-3">
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400" />
            <input
              data-testid="ideas-search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search ideas by title, skill, or tag…"
              className="input-field !pl-10"
            />
          </div>

          {/* Execution type (bucket) */}
          <div className="flex gap-2 overflow-x-auto pb-1 mb-2">
            <FilterChip active={bucket === ""} onClick={() => setBucket("")} testid="ideas-bucket-all">🌐 All types</FilterChip>
            {BUCKETS.map((b) => (
              <FilterChip key={b.id} active={bucket === b.id} onClick={() => setBucket(b.id)} testid={`ideas-bucket-${b.id}`}>
                {b.emoji} {b.label}
              </FilterChip>
            ))}
          </div>

          {/* Sector */}
          <div className="flex gap-2 overflow-x-auto pb-1 mb-2">
            <FilterChip active={sector === ""} onClick={() => setSector("")} testid="ideas-sector-all">All sectors</FilterChip>
            {SECTORS.map((s) => (
              <FilterChip key={s.id} active={sector === s.id} onClick={() => setSector(s.id)} testid={`ideas-sector-${s.id}`}>
                {s.emoji} {s.label}
              </FilterChip>
            ))}
          </div>

          {/* District — Telangana + AP priority */}
          <div className="flex gap-2 overflow-x-auto pb-1 mb-2">
            <FilterChip active={district === ""} onClick={() => setDistrict("")} testid="ideas-district-all">
              <MapPin size={11} /> All districts
            </FilterChip>
            {PRIORITY_DISTRICTS.map((d) => (
              <FilterChip key={d} active={district === d} onClick={() => setDistrict(d)} testid={`ideas-district-${d}`}>
                {d}
              </FilterChip>
            ))}
          </div>

          {/* More filters: investment range + tags (collapsible to keep mobile light) */}
          <button
            data-testid="ideas-more-filters"
            onClick={() => setMoreOpen((o) => !o)}
            className="inline-flex items-center gap-1.5 text-xs font-display font-semibold text-stone-600 hover:text-ink mt-1"
          >
            <SlidersHorizontal size={13} /> {moreOpen ? "Fewer filters" : "More filters"}
            {!moreOpen && (invest || tag) && <span className="chip bg-amber-100 text-amber-700 ml-1">on</span>}
          </button>

          {moreOpen && (
            <div className="mt-3 pt-3 border-t border-stone-100 flex flex-col gap-3">
              <div>
                <div className="label-display !mb-1.5">Investment needed</div>
                <div className="flex gap-2 overflow-x-auto pb-1">
                  <FilterChip active={invest === ""} onClick={() => setInvest("")} testid="ideas-invest-all">Any budget</FilterChip>
                  {INVESTMENT_RANGES.map((r) => {
                    const count = investCounts[r.id] || 0;
                    return (
                      <FilterChip
                        key={r.id}
                        active={invest === r.id}
                        disabled={count === 0}
                        onClick={() => count > 0 && setInvest(r.id)}
                        testid={`ideas-invest-${r.id}`}
                      >
                        {r.label}{count > 0 && <span className="opacity-60"> · {count}</span>}
                      </FilterChip>
                    );
                  })}
                </div>
              </div>
              <div>
                <div className="label-display !mb-1.5">Tags</div>
                <div className="flex gap-2 flex-wrap">
                  <FilterChip active={tag === ""} onClick={() => setTag("")} testid="ideas-tag-all">All tags</FilterChip>
                  {ALL_TAGS.map((t) => (
                    <FilterChip key={t} active={tag === t} onClick={() => setTag(t)} testid={`ideas-tag-${t}`}>
                      {t}
                    </FilterChip>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Bottom row: beginner toggle · sort · clear */}
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 mt-3 pt-3 border-t border-stone-100">
            <label className="inline-flex items-center gap-2 text-xs cursor-pointer select-none">
              <input type="checkbox" data-testid="ideas-beginner-toggle" checked={beginnerOnly} onChange={(e) => setBeginnerOnly(e.target.checked)} className="accent-amber-500 w-4 h-4" />
              <span className="font-display font-semibold text-stone-600">Beginner friendly only</span>
            </label>

            <label className="inline-flex items-center gap-2 text-xs ml-auto">
              <span className="font-display font-semibold text-stone-600">Sort</span>
              <select
                data-testid="ideas-sort"
                value={sort}
                onChange={(e) => setSort(e.target.value)}
                className="rounded-lg border border-stone-200 bg-white px-2.5 py-1.5 text-xs font-display font-semibold text-ink outline-none focus:border-amber-500"
              >
                {SORTS.map((s) => <option key={s.id} value={s.id}>{s.label}</option>)}
              </select>
            </label>

            {activeCount > 0 && (
              <button data-testid="ideas-clear" onClick={clearAll} className="inline-flex items-center gap-1 text-xs font-display font-semibold text-amber-700 hover:text-amber-800">
                <X size={12} /> Clear all ({activeCount})
              </button>
            )}
          </div>
        </div>

        {/* Result count */}
        <div className="flex items-center justify-between mb-3">
          <p data-testid="ideas-count" className="text-xs font-display font-semibold text-muted">
            {ideas.length} {ideas.length === 1 ? "idea" : "ideas"}
            {activeCount > 0 ? " match your filters" : " to explore"}
          </p>
        </div>

        {ideas.length === 0 ? (
          <div data-testid="ideas-empty" className="card-base !border-dashed !border-2 p-12 text-center">
            <div className="text-5xl mb-3">🔍</div>
            <h3 className="font-display font-bold text-lg mb-2">No ideas match those filters</h3>
            <p className="text-muted text-sm mb-5">Try clearing a filter or widening your budget range.</p>
            <button onClick={clearAll} className="btn-secondary" data-testid="ideas-empty-clear">Clear all filters</button>
          </div>
        ) : (
          <div data-testid="ideas-list" className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {ideas.map((i) => <IdeaCard key={i.id} idea={i} />)}
          </div>
        )}

        <div className="mt-12 bg-gradient-to-r from-amber-50 to-teal-50 border border-amber-200 rounded-2xl p-6 text-center">
          <Sparkles className="inline-block text-amber-600 mb-2" size={22} />
          <h3 className="font-display font-bold text-lg mb-1">Have an idea that's not listed?</h3>
          <p className="text-sm text-muted mb-4 max-w-md mx-auto">Post it as an opportunity — other builders in your district can find and collaborate on it.</p>
          <Link href="/opportunities/new" data-testid="ideas-post-cta" className="btn-primary">Post your idea →</Link>
        </div>
      </main>
    </div>
  );
}

function FilterChip({ active, onClick, children, testid, disabled = false }) {
  return (
    <button
      data-testid={testid}
      onClick={onClick}
      disabled={disabled}
      aria-pressed={active}
      className={`shrink-0 inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-display font-semibold whitespace-nowrap transition-colors min-h-[32px] ${
        disabled
          ? "bg-stone-50 text-stone-300 cursor-not-allowed"
          : active
          ? "bg-ink text-white"
          : "bg-stone-100 text-stone-600 hover:bg-stone-200"
      }`}
    >
      {children}
    </button>
  );
}

function IdeaCard({ idea }) {
  const sector = getSector(idea.sector);
  return (
    <Link
      href={`/ideas/${idea.slug}`}
      data-testid={`idea-card-${idea.slug}`}
      className="card-base p-5 flex flex-col gap-3 hover:-translate-y-1 hover:shadow-lg hover:border-amber-400 transition-all"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="text-3xl">{idea.emoji}</div>
        <span className={`chip ${BUCKET_COLOR[idea.bucket] || "bg-stone-100 text-stone-700"}`}>{idea.bucket.replace("-", " ")}</span>
      </div>
      <h3 className="h-card line-clamp-2">{idea.title}</h3>
      <p className="text-sm text-muted leading-relaxed line-clamp-3">{idea.short_description}</p>
      <div className="flex flex-wrap gap-1.5">
        <span className="chip bg-amber-50 text-amber-700">{sector.emoji} {sector.label}</span>
        {idea.beginner_friendly && <span className="chip bg-teal-50 text-teal-700">Beginner friendly</span>}
        {idea.remote_possible && <span className="chip bg-blue-50 text-blue-700">Remote possible</span>}
      </div>
      <div className="flex items-center justify-between pt-3 border-t border-stone-100 text-xs">
        <span className="font-display font-bold text-ink">
          {formatINR(idea.investment_min)}–{formatINR(idea.investment_adv)}
        </span>
        <span className="text-muted">{idea.district_fit.slice(0, 2).join(" · ")}</span>
      </div>
    </Link>
  );
}
