import AdminShell from "@/components/admin/AdminShell";
import { getKnowledgeGraphStats } from "@/lib/knowledge-graph";
import { Database, MapPin, Wrench, Landmark, Package, Route, Network } from "lucide-react";

export const dynamic = "force-dynamic";
export const metadata = { title: "Knowledge Graph | ValueWeave Admin", robots: { index: false, follow: false } };

function Stat({ icon: Icon, label, value, color = "amber" }) {
  const cls = { amber: "bg-amber-50 text-amber-700", teal: "bg-teal-50 text-teal-700", blue: "bg-blue-50 text-blue-700", purple: "bg-purple-50 text-purple-700" }[color];
  return <div className="card-base p-5 flex items-center gap-4"><div className={`p-3 rounded-xl ${cls}`}><Icon size={20} /></div><div><p className="font-display font-extrabold text-2xl text-ink">{value}</p><p className="text-xs text-stone-500 uppercase tracking-wider">{label}</p></div></div>;
}

export default async function KnowledgeGraphPage() {
  const stats = await getKnowledgeGraphStats();
  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-8">
        <div>
          <span className="chip bg-blue-100 text-blue-700 border border-blue-200">KNOWLEDGE GRAPH</span>
          <h1 className="font-display font-extrabold text-3xl text-ink mt-2">Entrepreneurship Knowledge Graph</h1>
          <p className="text-stone-500 text-sm mt-1 max-w-2xl">Central view of entity counts and relationship coverage across districts, skills, opportunities, schemes, resources, and roadmaps.</p>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
          <Stat icon={MapPin} label="District Count" value={stats.districts} color="teal" />
          <Stat icon={Wrench} label="Skill Count" value={stats.skills} color="amber" />
          <Stat icon={Landmark} label="Scheme Count" value={stats.schemes} color="blue" />
          <Stat icon={Package} label="Resource Count" value={stats.resources} color="purple" />
          <Stat icon={Route} label="Roadmap Count" value={stats.roadmaps} color="teal" />
          <Stat icon={Network} label="Opportunity Links" value={stats.relationships} color="amber" />
        </div>
        <section className="card-base p-5">
          <h2 className="font-display font-bold text-lg text-ink mb-4 flex items-center gap-2"><Database size={16} /> Relationship Statistics</h2>
          {Object.keys(stats.relationshipTypes).length === 0 ? <p className="text-sm text-muted">No relationships created yet. Use /admin/opportunity-mapping as the first relationship editor.</p> : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {Object.entries(stats.relationshipTypes).map(([type, count]) => <div key={type} className="bg-stone-50 rounded-xl px-4 py-3"><p className="font-mono text-xs text-stone-500">{type}</p><p className="font-display font-extrabold text-xl text-ink">{count}</p></div>)}
            </div>
          )}
        </section>
      </div>
    </AdminShell>
  );
}
