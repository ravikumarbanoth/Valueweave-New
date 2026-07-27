// Page controls for the explorer. Server-rendered links, not client state, so a
// page of knowledge is shareable and the back button behaves.
import Link from "next/link";

export default function KnowledgePagination({ page, pageSize, total, hrefFor }) {
  const pages = Math.max(1, Math.ceil(total / pageSize));
  if (pages <= 1) return null;
  const window = [page - 1, page, page + 1].filter((p) => p >= 1 && p <= pages);
  return (
    <nav data-testid="knowledge-pagination" className="flex items-center justify-center gap-2 pt-4"
         aria-label="Pagination">
      {page > 1 && (
        <Link href={hrefFor(page - 1)} className="chip hover:bg-stone-100">← Previous</Link>
      )}
      {window[0] > 1 && <Link href={hrefFor(1)} className="chip hover:bg-stone-100">1</Link>}
      {window[0] > 2 && <span className="text-muted text-sm px-1">…</span>}
      {window.map((p) => (
        <Link key={p} href={hrefFor(p)} aria-current={p === page ? "page" : undefined}
              className={`chip ${p === page ? "bg-ink text-white" : "hover:bg-stone-100"}`}>
          {p}
        </Link>
      ))}
      {window[window.length - 1] < pages - 1 && <span className="text-muted text-sm px-1">…</span>}
      {window[window.length - 1] < pages && (
        <Link href={hrefFor(pages)} className="chip hover:bg-stone-100">{pages}</Link>
      )}
      {page < pages && (
        <Link href={hrefFor(page + 1)} className="chip hover:bg-stone-100">Next →</Link>
      )}
    </nav>
  );
}
