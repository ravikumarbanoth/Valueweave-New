// Admin publishing dashboard (Option A workflow).
// Articles are filesystem MDX: drop a file in content/research/ and it goes
// live at the next deploy (instantly in dev). This page gives admins a
// status view: published/draft state, frontmatter validation, and the
// publishing checklist. No database, no paid APIs.
//
// Access: signed-in users whose email is in the ADMIN_EMAILS env var
// (comma-separated). In development it is open for convenience.

import Link from "next/link";
import { notFound } from "next/navigation";
import { getAllArticles } from "@/lib/mdx";
import { createClient } from "@/lib/supabase-server";
import AppNavbar from "@/components/AppNavbar";

export const dynamic = "force-dynamic";

export const metadata = { title: "Research Admin | ValueWeave", robots: { index: false, follow: false } };

async function isAdmin() {
  if (process.env.NODE_ENV === "development") return true;
  const allowed = (process.env.ADMIN_EMAILS || "")
    .split(",")
    .map((e) => e.trim().toLowerCase())
    .filter(Boolean);
  if (allowed.length === 0) return false;
  try {
    const supabase = createClient();
    const { data: { user } } = await supabase.auth.getUser();
    return !!user?.email && allowed.includes(user.email.toLowerCase());
  } catch {
    return false;
  }
}

const REQUIRED_FIELDS = ["title", "metaTitle", "metaDescription", "category", "sector"];

export default async function ResearchAdminPage() {
  if (!(await isAdmin())) notFound();

  const articles = getAllArticles({ includeDrafts: true });

  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-10 pb-20">
        <span className="chip bg-amber-100 text-amber-700 mb-3">ADMIN · RESEARCH HUB</span>
        <h1 className="font-display font-extrabold tracking-tight text-3xl mb-2">Research Publishing</h1>
        <p className="text-muted text-sm mb-8 max-w-2xl">
          Articles are MDX files in <code className="bg-stone-100 px-1.5 py-0.5 rounded text-xs">content/research/</code>.
          Add a file and deploy to publish; set <code className="bg-stone-100 px-1.5 py-0.5 rounded text-xs">published: false</code> in
          frontmatter to unpublish without deleting.
        </p>

        {/* Articles table */}
        <div className="card-base overflow-hidden mb-10">
          <div className="px-5 py-3 border-b border-stone-100 bg-stone-50 flex justify-between items-center">
            <span className="font-display font-bold text-sm">Articles ({articles.length})</span>
            <span className="text-xs text-muted">{articles.filter((a) => a.published).length} live</span>
          </div>
          {articles.length === 0 && (
            <p className="p-6 text-sm text-muted">No articles yet. Add your first .mdx file below.</p>
          )}
          {articles.map((a) => {
            const missing = REQUIRED_FIELDS.filter((f) => !a[f]);
            return (
              <div key={a.slug} className="px-5 py-4 border-b border-stone-100 last:border-0 flex flex-wrap items-center gap-3">
                <div className="flex-1 min-w-[220px]">
                  <Link href={`/research/${a.slug}`} className="font-display font-bold text-sm text-ink hover:text-amber-700">
                    {a.title || a.slug}
                  </Link>
                  <p className="text-xs text-muted mt-0.5">
                    /research/{a.slug} · {a.readingTime} min · {a.faq.length} FAQ · updated{" "}
                    {new Date(a.updatedAt).toLocaleDateString("en-IN")}
                  </p>
                  {missing.length > 0 && (
                    <p className="text-xs text-red-600 mt-1">Missing frontmatter: {missing.join(", ")}</p>
                  )}
                </div>
                <span className={`chip ${a.published ? "bg-teal-100 text-teal-700" : "bg-stone-100 text-stone-500"}`}>
                  {a.published ? "Published" : "Draft"}
                </span>
                <span className={`chip ${a.districtTags.length ? "bg-amber-50 text-amber-700" : "bg-stone-50 text-stone-400"}`}>
                  {a.districtTags.length} districts
                </span>
              </div>
            );
          })}
        </div>

        {/* How to publish */}
        <div className="card-base p-6">
          <h2 className="font-display font-bold text-lg mb-4">How to publish a new article</h2>
          <ol className="list-decimal list-inside space-y-2 text-sm text-muted mb-5">
            <li>Create <code className="bg-stone-100 px-1.5 py-0.5 rounded text-xs">content/research/your-article-slug.mdx</code></li>
            <li>Fill the frontmatter (template below) — district tags use slugs from /district</li>
            <li>Write the body in Markdown; <code className="bg-stone-100 px-1.5 py-0.5 rounded text-xs">&lt;Callout type=&quot;tip|warning|info&quot;&gt;</code> is supported</li>
            <li>Commit and deploy — the page, metadata, JSON-LD schemas, and sitemap entry generate automatically</li>
          </ol>
          <pre className="bg-ink text-stone-200 rounded-xl p-4 text-xs overflow-x-auto leading-relaxed">{`---
title: "Your Article Title"
metaTitle: "SEO Title | ValueWeave"
metaDescription: "150-160 char description for Google."
category: "agriculture"   # agriculture|healthcare|technology|manufacturing|energy|retail|education|logistics|food-processing|handicrafts
sector: "Agriculture"
districtTags: ["medak", "warangal"]
stateTags: ["Telangana"]
investmentRange:
  min: 100000
  max: 500000
  currency: "INR"
  label: "₹1L – ₹5L"
faq:
  - question: "…?"
    answer: "…"
relatedIdeas: ["idea-library-slug"]
publishedAt: "2026-06-12T00:00:00.000Z"
updatedAt: "2026-06-12T00:00:00.000Z"
published: true
---

## Overview

Your content here…`}</pre>
        </div>
      </main>
    </div>
  );
}
