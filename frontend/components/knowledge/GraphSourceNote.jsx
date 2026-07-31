// Says which knowledge system is answering.
//
// `/schemes` and `/skills` can be served by the admin CMS or by the researched
// knowledge graph. A user is entitled to know which — the two have different
// provenance guarantees, and only one of them can name a public source per row.
import Link from "next/link";

export default function GraphSourceNote({ source, kind, browseHref }) {
  if (source !== "GRAPH") return null;
  return (
    <div data-testid="graph-source-note"
         className="max-w-5xl mx-auto px-4 sm:px-6 pt-6">
      <p className="text-xs text-stone-500 bg-stone-50 border border-stone-150 rounded-xl px-3 py-2">
        Showing {kind} from our research team, each one checked against an official
        public source.{" "}
        <Link href={browseHref} className="underline hover:text-ink">
          Browse all {kind} in the Knowledge Explorer →
        </Link>
      </p>
    </div>
  );
}
