// Admin Research Publisher — dashboard.
// Server wrapper: passes the legacy file-based MDX article list (read-only)
// to the client dashboard, which manages database articles live.
// Auth/role gating happens in layout.js.

import { getAllArticles } from "@/lib/mdx";
import ResearchAdminClient from "./ResearchAdminClient";

export default function ResearchAdminPage() {
  const mdxArticles = getAllArticles({ includeDrafts: true }).map((a) => ({
    slug: a.slug,
    title: a.title || a.slug,
    published: a.published,
    category: a.category,
    updatedAt: a.updatedAt,
  }));
  return <ResearchAdminClient mdxArticles={mdxArticles} />;
}
