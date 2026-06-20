import Link from "next/link";
import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-server";
import { getCombinedArticles } from "@/lib/research";
import { DISTRICTS } from "@/lib/districts-data";
import { IDEAS } from "@/lib/idea-library";
import { getKgEntities } from "@/lib/knowledge-graph";
import {
  CheckCircle,
  AlertCircle,
  XCircle,
  Bot,
  FileText,
  MapPin,
  Lightbulb,
  Briefcase,
  Wrench,
  Landmark,
  Package,
  Route,
  Network,
} from "lucide-react";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "GEO Audit | ValueWeave Admin",
  robots: { index: false, follow: false },
};

function statusIcon(ok, warn = false) {
  if (ok) return <CheckCircle size={14} className="text-green-500" />;
  if (warn) return <AlertCircle size={14} className="text-amber-500" />;
  return <XCircle size={14} className="text-red-500" />;
}

function hasFaq(entity) {
  return Array.isArray(entity.faq_json) && entity.faq_json.length > 0;
}

function hasMetadata(entity) {
  return !!(entity.meta_title && entity.meta_description);
}

function hasSummary(entity) {
  return !!(entity.summary || entity.ai_summary || entity.meta_description);
}

function kgPage(entity, type, href) {
  return {
    type,
    title: entity.name || entity.title || entity.district_name || entity.slug,
    href,
    schema: true,
    summary: hasSummary(entity),
    faq: hasFaq(entity),
    metadata: hasMetadata(entity),
  };
}

async function fetchGeoAudit() {
  const [articles, kgDistricts, skills, resources, schemes, roadmaps] = await Promise.all([
    getCombinedArticles(),
    getKgEntities("districts", { status: "published" }),
    getKgEntities("skills", { status: "published" }),
    getKgEntities("resources", { status: "published" }),
    getKgEntities("schemes", { status: "published" }),
    getKgEntities("roadmaps", { status: "published" }),
  ]);

  let opportunities = [];
  try {
    const sb = createClient();
    const { data } = await sb.from("opportunities").select("id,title,description,investment_range,district,category").limit(300);
    opportunities = data || [];
  } catch {
    opportunities = [];
  }

  const pages = [
    ...articles.map((a) => ({
      type: "Research",
      title: a.title,
      href: `/research/${a.slug}`,
      schema: true,
      summary: !!a.metaDescription,
      faq: (a.faq || []).length > 0,
      metadata: !!(a.metaTitle && a.metaDescription),
    })),
    ...DISTRICTS.map((d) => ({
      type: "District",
      title: d.name,
      href: `/district/${d.slug}`,
      schema: true,
      summary: !!d.profileSummary,
      faq: false,
      metadata: true,
    })),
    ...kgDistricts.map((d) => kgPage(d, "District CMS", `/district-opportunity-index?district=${d.slug}`)),
    ...IDEAS.map((i) => ({
      type: "Idea",
      title: i.title,
      href: `/ideas/${i.slug}`,
      schema: true,
      summary: !!i.short_description,
      faq: false,
      metadata: true,
    })),
    ...opportunities.map((o) => ({
      type: "Opportunity",
      title: o.title,
      href: `/opportunities/${o.id}`,
      schema: true,
      summary: !!o.description,
      faq: false,
      metadata: !!(o.title && o.description),
    })),
    ...skills.map((s) => kgPage(s, "Skill", `/skills/${s.slug}`)),
    ...resources.map((r) => kgPage(r, "Resource", `/resources/${r.slug}`)),
    ...schemes.map((s) => kgPage(s, "Scheme", `/schemes/${s.slug}`)),
    ...roadmaps.map((r) => kgPage(r, "Roadmap", `/roadmaps/${r.slug}`)),
  ];

  const total = pages.length || 1;
  const schemaCoverage = Math.round((pages.filter((p) => p.schema).length / total) * 100);
  const summaryCoverage = Math.round((pages.filter((p) => p.summary).length / total) * 100);
  const metadataCoverage = Math.round((pages.filter((p) => p.metadata).length / total) * 100);
  const faqCoverage = Math.round((pages.filter((p) => p.faq).length / total) * 100);
  const score = Math.round(schemaCoverage * 0.35 + summaryCoverage * 0.3 + metadataCoverage * 0.25 + faqCoverage * 0.1);

  return {
    score,
    pages,
    schemaCoverage,
    summaryCoverage,
    metadataCoverage,
    faqCoverage,
    missingMetadata: pages.filter((p) => !p.metadata),
    missingFaq: pages.filter((p) => !p.faq),
    missingSummaries: pages.filter((p) => !p.summary),
  };
}

function Stat({ icon: Icon, label, value, accent = "amber" }) {
  const color = {
    amber: "bg-amber-50 text-amber-700",
    teal: "bg-teal-50 text-teal-700",
    blue: "bg-blue-50 text-blue-700",
    green: "bg-green-50 text-green-700",
  }[accent];
  return (
    <div className="card-base p-4 flex items-center gap-3">
      <div className={`p-2 rounded-lg ${color}`}><Icon size={16} /></div>
      <div>
        <p className="font-display font-extrabold text-2xl text-ink">{value}</p>
        <p className="text-[11px] text-stone-500 uppercase tracking-wider">{label}</p>
      </div>
    </div>
  );
}

function MissingList({ title, items }) {
  return (
    <section className="card-base p-5">
      <h2 className="font-display font-bold text-base text-ink mb-3">{title}</h2>
      {items.length === 0 ? (
        <p className="text-sm text-teal-700 bg-teal-50 rounded-xl px-3 py-2">No gaps found.</p>
      ) : (
        <div className="space-y-2 max-h-72 overflow-y-auto">
          {items.slice(0, 30).map((item) => (
            <Link key={`${item.type}-${item.href}`} href={item.href} className="flex items-center justify-between gap-3 text-sm px-3 py-2 rounded-xl bg-stone-50 hover:bg-amber-50">
              <span className="truncate">{item.title}</span>
              <span className="chip bg-white text-stone-500 border border-stone-200 shrink-0">{item.type}</span>
            </Link>
          ))}
          {items.length > 30 && <p className="text-xs text-stone-400">+ {items.length - 30} more</p>}
        </div>
      )}
    </section>
  );
}

const SCHEMA_TYPES = [
  { type: "Research", icon: FileText },
  { type: "District", icon: MapPin },
  { type: "District CMS", icon: Network },
  { type: "Idea", icon: Lightbulb },
  { type: "Opportunity", icon: Briefcase },
  { type: "Skill", icon: Wrench },
  { type: "Resource", icon: Package },
  { type: "Scheme", icon: Landmark },
  { type: "Roadmap", icon: Route },
];

export default async function GeoAuditPage() {
  const d = await fetchGeoAudit();
  const scoreColor = d.score >= 80 ? "text-green-600 bg-green-50 border-green-200" : d.score >= 60 ? "text-amber-600 bg-amber-50 border-amber-200" : "text-red-600 bg-red-50 border-red-200";

  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
          <div>
            <span className="chip bg-blue-100 text-blue-700 border border-blue-200">GEO AUDIT</span>
            <h1 className="font-display font-extrabold text-3xl text-ink mt-2">Generative Engine Readiness</h1>
            <p className="text-stone-500 text-sm mt-1 max-w-2xl">Schema, summaries, FAQ coverage, and AI-readable metadata across public content.</p>
          </div>
          <div className={`w-28 h-28 rounded-full border-4 flex flex-col items-center justify-center ${scoreColor}`}>
            <span className="font-display font-extrabold text-3xl">{d.score}</span>
            <span className="text-[10px] font-bold uppercase tracking-wider">GEO Score</span>
          </div>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <Stat icon={Bot} label="Schema Coverage" value={`${d.schemaCoverage}%`} accent="blue" />
          <Stat icon={FileText} label="Summary Coverage" value={`${d.summaryCoverage}%`} accent="amber" />
          <Stat icon={CheckCircle} label="Metadata Coverage" value={`${d.metadataCoverage}%`} accent="green" />
          <Stat icon={AlertCircle} label="FAQ Coverage" value={`${d.faqCoverage}%`} accent="teal" />
        </div>

        <section className="card-base p-5">
          <h2 className="font-display font-bold text-base text-ink mb-4">Schema Coverage By Page Type</h2>
          <div className="grid sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {SCHEMA_TYPES.map(({ type, icon: Icon }) => {
              const pages = d.pages.filter((p) => p.type === type);
              const ok = pages.length > 0 && pages.every((p) => p.schema && p.summary);
              return (
                <div key={type} className="bg-stone-50 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <Icon size={16} className="text-amber-600" />
                    {statusIcon(ok, !ok && pages.length > 0)}
                  </div>
                  <p className="font-display font-bold text-sm text-ink">{type}</p>
                  <p className="text-xs text-stone-500">{pages.length} pages checked</p>
                </div>
              );
            })}
          </div>
        </section>

        <div className="grid lg:grid-cols-3 gap-5">
          <MissingList title="Pages Missing Metadata" items={d.missingMetadata} />
          <MissingList title="Pages Missing FAQ" items={d.missingFaq} />
          <MissingList title="Pages Missing Summaries" items={d.missingSummaries} />
        </div>
      </div>
    </AdminShell>
  );
}
