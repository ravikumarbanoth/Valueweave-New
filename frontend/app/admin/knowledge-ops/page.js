// Knowledge operations — the one screen that answers "how is the platform?".
//
// WHY THIS PAGE EXISTS WHEN THERE ARE ALREADY THIRTY ADMIN PAGES
// ---------------------------------------------------------------
// Not one of them looks at the knowledge platform. Every table the other
// twenty-nine read is `public.*` application data — opportunities, page_views,
// search_events, research_articles, profiles. The Graph Dashboard reads
// lib/knowledge-graph.js, which is the older public.kg_* CMS tables.
//
// So there was no admin view of: the 647 entities, the eight packages, the
// vocabulary crosswalk, the sync manifest, the collection queue, the source
// registry, or the stewardship ledger. The operational half of ValueWeave was
// invisible from the admin panel it is operated from.
//
// WHY IT READS A COMMITTED FILE AND NOT THE DATABASE
// --------------------------------------------------
// Everything on this page is computed from artifacts already in Git —
// graph_summary, validation_summary, crosswalk_summary, the sync manifest, the
// collection state. `python3 -m ops.cli snapshot --write` composes them into
// lib/ops/snapshot.json and this page imports it.
//
// Three consequences, all of them the point:
//
//   the numbers are reproducible.   Anyone can run the same command and get the
//                                   same figures. A dashboard whose numbers
//                                   cannot be checked is a dashboard nobody
//                                   trusts the third time it surprises them.
//   it needs no query.              No RLS policy, no service role, no new
//                                   table, no migration. This milestone adds
//                                   nothing to the database at all.
//   staleness is visible.           The snapshot carries the moment it was
//                                   generated, and the page says so out loud.
//                                   `ops.cli snapshot --check` fails CI when
//                                   the committed copy has drifted.
//
// The live half — what people searched for — is deliberately NOT in the
// snapshot. It comes from `search_events` at request time, because it changes
// by the hour and because it is the one thing here that is about readers
// rather than about us.
import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-server";
import snapshot from "@/lib/ops/snapshot.json";
import {
  Activity, AlertTriangle, Database, GitBranch, Network, Rss, Search, ShieldCheck,
} from "lucide-react";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Knowledge Operations | ValueWeave Admin",
  robots: { index: false, follow: false },
};

const TONE = {
  healthy: "bg-teal-50 text-teal-700 border-teal-200",
  degraded: "bg-amber-50 text-amber-700 border-amber-200",
  critical: "bg-red-50 text-red-700 border-red-200",
  unknown: "bg-stone-50 text-stone-500 border-stone-200",
};

const SEVERITY = {
  CRITICAL: "bg-red-50 text-red-700 border-red-200",
  WARN: "bg-amber-50 text-amber-700 border-amber-200",
  OK: "bg-teal-50 text-teal-700 border-teal-200",
  UNKNOWN: "bg-stone-50 text-stone-500 border-stone-200",
};

/** Searches, live. Fails to an empty list — this page must render without it. */
async function liveDemand() {
  try {
    const supabase = createClient();
    const since = new Date(Date.now() - 7 * 86400000).toISOString();
    const { data } = await supabase
      .from("search_events")
      .select("query,results_count")
      .gte("created_at", since)
      .limit(5000);
    if (!data?.length) return null;

    const all = new Map();
    const zero = new Map();
    for (const row of data) {
      const q = String(row.query || "").trim().toLowerCase();
      if (!q) continue;
      all.set(q, (all.get(q) || 0) + 1);
      if (!row.results_count) zero.set(q, (zero.get(q) || 0) + 1);
    }
    const rank = (m) => [...m.entries()].sort((a, b) => b[1] - a[1]).slice(0, 10);
    return {
      total: data.length,
      unique: all.size,
      zeroTotal: [...zero.values()].reduce((a, b) => a + b, 0),
      top: rank(all),
      zero: rank(zero),
    };
  } catch {
    return null;
  }
}

function Stat({ label, value, sub, icon: Icon }) {
  return (
    <div className="card-base p-4">
      <div className="flex items-center gap-2 mb-1">
        {Icon && <Icon size={13} className="text-stone-400" />}
        <span className="text-[10px] uppercase tracking-widest text-stone-400 font-semibold">
          {label}
        </span>
      </div>
      <div className="text-xl font-display font-extrabold text-ink">{value}</div>
      {sub && <p className="text-[11px] text-stone-400 mt-0.5">{sub}</p>}
    </div>
  );
}

function Panel({ title, subtitle, icon: Icon, children }) {
  return (
    <section className="card-base p-5">
      <div className="flex items-center gap-2 mb-1">
        {Icon && <Icon size={15} className="text-stone-400" />}
        <h2 className="font-display font-bold text-ink text-sm">{title}</h2>
      </div>
      {subtitle && <p className="text-[11px] text-stone-400 mb-3">{subtitle}</p>}
      <div className="mt-3">{children}</div>
    </section>
  );
}

export default async function KnowledgeOpsPage() {
  const { overview, quality, integrity, collection, connectivity, freshness, sync,
          backlog, generated_at: generatedAt } = snapshot;
  const demand = await liveDemand();

  const age = Math.round((Date.now() - new Date(generatedAt).getTime()) / 3600000);
  const findings = [...(integrity.findings || []), ...(collection.findings || [])];
  const queue = collection.queue?.by_state || {};
  const stars = collection.queue?.awaiting_review_by_stars || {};

  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">
          <div>
            <span className="chip bg-teal-100 text-teal-700 border border-teal-200">
              KNOWLEDGE OPERATIONS
            </span>
            <h1 className="font-display font-extrabold text-2xl text-ink mt-2">
              How the knowledge platform is doing
            </h1>
            {/* Said out loud, always. A dashboard that does not date itself is
                a dashboard that will one day show last month's numbers to
                somebody making a decision. */}
            <p className="text-stone-500 text-sm mt-1">
              Snapshot generated {generatedAt}
              {age > 48 && (
                <span className="text-amber-700 font-semibold">
                  {" "}— {Math.round(age / 24)} days old. Run{" "}
                  <code>python3 -m ops.cli snapshot --write</code>.
                </span>
              )}
            </p>
          </div>
          <div className={`chip border ${TONE[integrity.status] || TONE.unknown}`}>
            integrity: {integrity.status}
          </div>
        </div>

        {/* ── the headline numbers ─────────────────────────────────────── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Stat label="Quality" value={`${quality.overall ?? "—"} ${quality.grade}`}
                sub={`${quality.dimensions_scored} scored · ${quality.dimensions_unknown} unknown`}
                icon={ShieldCheck} />
          <Stat label="Entities" value={overview.entities}
                sub={`${overview.relationships} relationships`} icon={Database} />
          <Stat label="Connected" value={`${connectivity.connected_pct}%`}
                sub={`${connectivity.isolated} lead nowhere`} icon={Network} />
          <Stat label="Awaiting review" value={queue.NEEDS_REVIEW || 0}
                sub={`${collection.sources?.active || 0} active feeds`} icon={Rss} />
        </div>

        {/* ── what is wrong ─────────────────────────────────────────────── */}
        <Panel title="Findings" icon={AlertTriangle}
               subtitle="Operational, not correctness. The eleven graph checks pass; these are the failures that pass them.">
          {findings.length === 0 ? (
            <p className="text-sm text-stone-400 italic">Nothing to report.</p>
          ) : (
            <ul className="space-y-2" data-testid="ops-findings">
              {findings.map((f, i) => (
                <li key={`${f.check}-${i}`} className="flex items-start gap-3">
                  <span className={`chip border shrink-0 ${SEVERITY[f.severity] || SEVERITY.UNKNOWN}`}>
                    {f.severity}
                  </span>
                  <span className="text-[13px] text-ink">
                    <span className="font-semibold">{f.check}</span>
                    {f.source_id ? ` · ${f.source_id}` : ""} — {f.detail}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Panel>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* ── the score, broken open ──────────────────────────────────── */}
          <Panel title="Knowledge quality" icon={ShieldCheck}
                 subtitle="Seven dimensions. A dimension with no data is UNKNOWN and excluded from the mean — never scored zero.">
            <div className="space-y-3" data-testid="ops-quality">
              {quality.dimensions.map((d) => (
                <div key={d.name}>
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-[13px] font-semibold text-ink capitalize">
                      {d.name.replace(/_/g, " ")}
                    </span>
                    <span className="text-[12px] font-bold text-stone-600">
                      {d.value === null ? "unknown" : d.value}
                    </span>
                  </div>
                  <div className="bg-stone-100 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        d.value === null ? "bg-stone-200"
                          : d.value < 40 ? "bg-red-400"
                          : d.value < 60 ? "bg-amber-400" : "bg-teal-400"}`}
                      style={{ width: `${d.value === null ? 100 : Math.max(d.value, 2)}%` }}
                    />
                  </div>
                  <p className="text-[11px] text-stone-400 mt-1">{d.detail}</p>
                </div>
              ))}
            </div>
          </Panel>

          {/* ── the review queue ────────────────────────────────────────── */}
          <Panel title="Review queue" icon={GitBranch}
                 subtitle="Ranked, so the most important item is the first one read. Approval happens in stewardship, not here.">
            <div className="flex flex-wrap gap-2 mb-4">
              {Object.entries(stars).sort((a, b) => b[0] - a[0]).map(([n, count]) => (
                <span key={n} className="chip bg-white border border-stone-200 text-stone-600">
                  {"★".repeat(Number(n))}{"☆".repeat(5 - Number(n))} {count}
                </span>
              ))}
              {Object.keys(stars).length === 0 && (
                <span className="text-sm text-stone-400 italic">Queue is empty.</span>
              )}
            </div>
            <ul className="space-y-2" data-testid="ops-queue">
              {(collection.top_of_queue || []).map((item, i) => (
                <li key={i} className="border-l-2 border-stone-200 pl-3">
                  <p className="text-[13px] text-ink">
                    <span className="text-amber-500">
                      {"★".repeat(item.stars || 1)}
                    </span>{" "}
                    <span className="font-semibold">{item.type}</span> — {item.title}
                  </p>
                  {item.why && <p className="text-[11px] text-stone-400">{item.why}</p>}
                </li>
              ))}
            </ul>
          </Panel>

          {/* ── pipeline state ──────────────────────────────────────────── */}
          <Panel title="Pipeline" icon={Activity}
                 subtitle="Collection ends at a pull request. Sync starts at a push to main. The gap between them is a person.">
            <dl className="text-[13px] space-y-1.5">
              {[
                ["Feed health", collection.feed_status],
                ["Sources", `${collection.sources?.active || 0} active · ${collection.sources?.pending_verification || 0} unverified · ${collection.sources?.dead || 0} dead`],
                ["Last collection", collection.last_run || "never"],
                ["Last successful sync", sync.last_success || "never recorded"],
                ["Last failed sync", sync.last_failure || "none"],
                ["Graph validation", snapshot.graph_validation || "not run"],
                ["Engine compatibility", snapshot.engine_compatibility || "not run"],
                ["Freshness", `${freshness.fresh} fresh · ${freshness.ageing} ageing · ${freshness.stale} stale`],
                ["Crosswalk", `${overview.crosswalk_rows ?? "—"} terms · ${overview.crosswalk_resolved_pct ?? "—"}% resolved`],
              ].map(([label, value]) => (
                <div key={label} className="flex justify-between gap-4">
                  <dt className="text-stone-400">{label}</dt>
                  <dd className="text-ink font-medium text-right">{String(value)}</dd>
                </div>
              ))}
            </dl>
          </Panel>

          {/* ── demand, live ────────────────────────────────────────────── */}
          <Panel title="Search demand — last 7 days" icon={Search}
                 subtitle="Live from search_events. The only thing on this page that is not from the snapshot.">
            {!demand ? (
              <p className="text-sm text-stone-400 italic" data-testid="ops-no-demand">
                No search data in the last seven days. Search tracking writes to{" "}
                <code>search_events</code> from the live search box.
              </p>
            ) : (
              <>
                <p className="text-[12px] text-stone-500 mb-3">
                  {demand.total} searches · {demand.unique} distinct terms ·{" "}
                  <span className="font-semibold text-red-600">
                    {demand.zeroTotal} returned nothing
                  </span>
                </p>
                <div className="grid grid-cols-2 gap-4 text-[12px]">
                  <div>
                    <p className="text-[10px] uppercase tracking-widest text-stone-400 mb-1">
                      Most searched
                    </p>
                    {demand.top.map(([term, n]) => (
                      <p key={term} className="flex justify-between">
                        <span className="truncate text-ink">{term}</span>
                        <span className="text-stone-400">{n}</span>
                      </p>
                    ))}
                  </div>
                  <div>
                    <p className="text-[10px] uppercase tracking-widest text-stone-400 mb-1">
                      Found nothing
                    </p>
                    {demand.zero.map(([term, n]) => (
                      <p key={term} className="flex justify-between">
                        <span className="truncate text-ink">{term}</span>
                        <span className="text-red-500">{n}</span>
                      </p>
                    ))}
                  </div>
                </div>
              </>
            )}
          </Panel>
        </div>

        {/* ── the backlog ───────────────────────────────────────────────── */}
        <Panel title="Research backlog" icon={Search}
               subtitle="Topics people looked for that ValueWeave does not cover. Gaps, not knowledge — nothing here may become an entity without research against a public source.">
          {backlog?.length ? (
            <table className="w-full text-[13px]" data-testid="ops-backlog">
              <thead>
                <tr className="text-[10px] uppercase tracking-widest text-stone-400 text-left">
                  <th className="pb-2">Term</th>
                  <th className="pb-2 text-right">Score</th>
                  <th className="pb-2 text-right">Searches</th>
                  <th className="pb-2 text-right">Requests</th>
                  <th className="pb-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {backlog.slice(0, 12).map((row) => (
                  <tr key={row.term} className="border-t border-stone-100">
                    <td className="py-1.5 text-ink">{row.term}</td>
                    <td className="py-1.5 text-right text-stone-500">{row.score}</td>
                    <td className="py-1.5 text-right text-stone-500">{row.searches}</td>
                    <td className="py-1.5 text-right text-stone-500">{row.requests}</td>
                    <td className="py-1.5 text-stone-400">{row.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-sm text-stone-400 italic">
              Nothing recorded yet. The backlog is built by{" "}
              <code>python3 -m collection.cli backlog --write</code>.
            </p>
          )}
        </Panel>

        {/* ── least connected ───────────────────────────────────────────── */}
        <Panel title="Knowledge that leads nowhere" icon={Network}
               subtitle="Reachable by search, connecting to nothing. The single biggest determinant of whether this feels like a network or a list of rows.">
          <div className="flex flex-wrap gap-2" data-testid="ops-least-connected">
            {(connectivity.least_connected || []).map((e) => (
              <span key={e.name} className="chip bg-white border border-stone-200 text-stone-600">
                {e.name} <span className="text-stone-400">· {e.type} · {e.degree}</span>
              </span>
            ))}
          </div>
          {connectivity.isolated_by_type && (
            <p className="text-[11px] text-stone-400 mt-3">
              Isolated by type:{" "}
              {Object.entries(connectivity.isolated_by_type)
                .map(([t, n]) => `${t} (${n})`).join(" · ")}
            </p>
          )}
        </Panel>

        <p className="text-[11px] text-stone-400">
          Every figure except search demand comes from{" "}
          <code>frontend/lib/ops/snapshot.json</code>, composed from committed
          artifacts by <code>python3 -m ops.cli snapshot --write</code>. Reproduce
          any number with <code>python3 -m ops.cli status</code>.
        </p>
      </div>
    </AdminShell>
  );
}
