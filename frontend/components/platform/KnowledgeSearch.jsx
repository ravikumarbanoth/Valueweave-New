"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Search } from "lucide-react";
import { getAllKnowledgeItems } from "@/lib/static-knowledge";

export default function KnowledgeSearch() {
  const [query, setQuery] = useState("");
  const items = useMemo(() => getAllKnowledgeItems(), []);
  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items.slice(0, 8);
    return items.filter((item) => item.searchText.includes(q)).slice(0, 12);
  }, [items, query]);

  return (
    <section className="card-base p-5 sm:p-7">
      <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4 mb-5">
        <div>
          <span className="chip bg-teal-100 text-teal-700 border border-teal-200 mb-3">CLIENT-SIDE SEARCH</span>
          <h3 className="font-display font-extrabold text-2xl text-ink">Search the Knowledge Layer</h3>
          <p className="text-sm text-muted mt-2 max-w-2xl leading-relaxed">
            Search static districts, industries, products, skills, training pathways, manufacturing opportunities, and schemes. No backend or AI is used.
          </p>
        </div>
        <div className="relative w-full lg:w-80">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search Medak, PMEGP, packaging..."
            className="input-field !pl-10"
          />
        </div>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {results.map((item) => (
          <Link key={`${item.type}-${item.slug}`} href={item.href} className="rounded-2xl bg-stone-50 border border-stone-150 p-4 hover:border-amber-300 hover:bg-amber-50 transition-colors group">
            <span className="chip bg-white text-stone-500 border border-stone-200 text-[10px] mb-3">{item.typeLabel}</span>
            <h4 className="font-display font-bold text-sm text-ink group-hover:text-amber-700 transition-colors">{item.name}</h4>
            <p className="text-xs text-muted mt-2 line-clamp-3 leading-relaxed">
              {item.summary || item.description || item.purpose || item.overview}
            </p>
          </Link>
        ))}
      </div>
    </section>
  );
}
