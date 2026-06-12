"use client";
// Admin Research Publisher — article editor.
// Used by /admin/research/new (no id) and /admin/research/[id].
// Auto-saves drafts every 30s, warns before leaving with unsaved changes,
// and renders a live markdown preview (marked).

import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { marked } from "marked";
import { createClient } from "@/lib/supabase-browser";
import { CATEGORY_LABELS } from "@/lib/theme";
import { DISTRICTS } from "@/lib/districts-data";

const EMPTY = {
  title: "",
  slug: "",
  excerpt: "",
  category: "healthcare",
  district: "",
  author: "ValueWeave Research Team",
  cover_image: "",
  content: "",
  status: "draft",
  seo_title: "",
  seo_description: "",
  keywords: "",
  faq_json: [],
};

const slugify = (t) =>
  t.toLowerCase().replace(/&/g, "and").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 80);

export default function ArticleEditor({ id, mdxSlugs = [] }) {
  const supabase = createClient();
  const router = useRouter();
  const [form, setForm] = useState(EMPTY);
  const [dbId, setDbId] = useState(id || null);
  const [loading, setLoading] = useState(!!id);
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [err, setErr] = useState("");
  const [lastSaved, setLastSaved] = useState(null);
  const [tab, setTab] = useState("write");
  const [seoOpen, setSeoOpen] = useState(false);
  const [slugTouched, setSlugTouched] = useState(!!id);
  const formRef = useRef(form);
  const dirtyRef = useRef(false);
  formRef.current = form;
  dirtyRef.current = dirty;

  // Load existing article
  useEffect(() => {
    if (!id) return;
    (async () => {
      const { data, error } = await supabase.from("research_articles").select("*").eq("id", id).single();
      if (error || !data) {
        setErr(error ? `Could not load article: ${error.message}` : "Article not found.");
      } else {
        setForm({
          ...EMPTY,
          ...data,
          excerpt: data.excerpt || "",
          district: data.district || "",
          cover_image: data.cover_image || "",
          content: data.content || "",
          seo_title: data.seo_title || "",
          seo_description: data.seo_description || "",
          keywords: (data.keywords || []).join(", "),
          faq_json: Array.isArray(data.faq_json) ? data.faq_json : [],
        });
      }
      setLoading(false);
    })();
  }, [id, supabase]);

  function update(key, value) {
    setForm((prev) => {
      const next = { ...prev, [key]: value };
      if (key === "title" && !slugTouched) next.slug = slugify(value);
      return next;
    });
    if (key === "slug") setSlugTouched(true);
    setDirty(true);
  }

  const slugConflict = useMemo(
    () => mdxSlugs.includes(form.slug) ? "This slug belongs to a file-based MDX article — the database version will take priority over it." : "",
    [form.slug, mdxSlugs]
  );

  const toRow = useCallback((f) => ({
    title: f.title.trim(),
    slug: f.slug.trim(),
    excerpt: f.excerpt.trim() || null,
    category: f.category || null,
    district: f.district.trim() || null,
    author: f.author.trim() || null,
    cover_image: f.cover_image.trim() || null,
    content: f.content,
    seo_title: f.seo_title.trim() || null,
    seo_description: f.seo_description.trim() || null,
    keywords: f.keywords.split(",").map((k) => k.trim()).filter(Boolean),
    faq_json: f.faq_json.filter((q) => q.question?.trim() && q.answer?.trim()),
  }), []);

  const save = useCallback(async (statusOverride) => {
    const f = formRef.current;
    if (!f.title.trim() || !f.slug.trim()) {
      setErr("Title and slug are required.");
      return null;
    }
    setSaving(true);
    setErr("");
    const row = toRow(f);
    if (statusOverride) {
      row.status = statusOverride;
      if (statusOverride === "published") row.published_at = new Date().toISOString();
    }
    let result;
    if (dbId) {
      result = await supabase.from("research_articles").update(row).eq("id", dbId).select("id, status").single();
    } else {
      row.status = row.status || "draft";
      result = await supabase.from("research_articles").insert(row).select("id, status").single();
    }
    setSaving(false);
    if (result.error) {
      const msg = result.error.code === "23505"
        ? "That slug is already used by another article."
        : result.error.message;
      setErr(`Save failed: ${msg}`);
      return null;
    }
    setDbId(result.data.id);
    if (statusOverride) setForm((p) => ({ ...p, status: statusOverride }));
    setDirty(false);
    setLastSaved(new Date());
    if (!dbId) router.replace(`/admin/research/${result.data.id}`);
    return result.data;
  }, [dbId, supabase, router, toRow]);

  // Auto-save every 30 seconds while dirty (drafts and edits alike)
  useEffect(() => {
    const t = setInterval(() => {
      if (dirtyRef.current && formRef.current.title.trim() && formRef.current.slug.trim()) {
        save();
      }
    }, 30000);
    return () => clearInterval(t);
  }, [save]);

  // Warn before leaving with unsaved changes
  useEffect(() => {
    const onBeforeUnload = (e) => {
      if (dirtyRef.current) {
        e.preventDefault();
        e.returnValue = "";
      }
    };
    window.addEventListener("beforeunload", onBeforeUnload);
    return () => window.removeEventListener("beforeunload", onBeforeUnload);
  }, []);

  async function publish() {
    const res = await save("published");
    if (res) router.push("/admin/research");
  }
  async function unpublish() {
    await save("draft");
  }

  const previewHtml = useMemo(() => {
    try { return marked.parse(form.content || "*Nothing to preview yet.*"); }
    catch { return "<p>Preview unavailable.</p>"; }
  }, [form.content]);

  if (loading) {
    return (
      <main className="max-w-3xl mx-auto px-4 py-10">
        <div className="skeleton h-10 w-2/3 mb-4" /><div className="skeleton h-64 w-full" />
      </main>
    );
  }

  return (
    <main className="max-w-3xl mx-auto px-4 sm:px-6 py-8 pb-24">
      {/* Header bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <Link href="/admin/research" className="text-sm font-display font-semibold text-muted hover:text-ink">
          ← All articles
        </Link>
        <div className="flex items-center gap-2 text-xs text-muted">
          <span className={`chip ${form.status === "published" ? "bg-teal-100 text-teal-700" : "bg-amber-100 text-amber-700"}`}>
            {form.status}
          </span>
          {saving ? <span>Saving…</span> : lastSaved ? <span>Saved {lastSaved.toLocaleTimeString("en-IN")}</span> : dirty ? <span className="text-amber-600">Unsaved changes</span> : null}
        </div>
      </div>

      {err && (
        <div data-testid="editor-error" className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm mb-4">{err}</div>
      )}

      <div className="card-base p-5 sm:p-6 flex flex-col gap-5">
        {/* Title + slug */}
        <div>
          <label className="label-display">Title *</label>
          <input data-testid="editor-title" value={form.title} onChange={(e) => update("title", e.target.value)}
            placeholder="Healthcare Business Opportunities in Medak District" className="input-field !text-base font-display font-bold" />
        </div>
        <div>
          <label className="label-display">Slug *</label>
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted shrink-0">/research/</span>
            <input data-testid="editor-slug" value={form.slug} onChange={(e) => update("slug", slugify(e.target.value))} className="input-field font-mono !text-sm" />
          </div>
          {slugConflict && <p className="text-xs text-amber-600 mt-1">{slugConflict}</p>}
        </div>

        {/* Excerpt */}
        <div>
          <label className="label-display">Excerpt</label>
          <textarea value={form.excerpt} onChange={(e) => update("excerpt", e.target.value)} rows={2}
            placeholder="One or two sentences shown on cards and used as the default meta description."
            className="input-field resize-none" />
        </div>

        {/* Category / District / Author / Cover */}
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="label-display">Category</label>
            <select value={form.category} onChange={(e) => update("category", e.target.value)} className="input-field">
              {Object.entries(CATEGORY_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </div>
          <div>
            <label className="label-display">District</label>
            <input list="vw-districts" value={form.district} onChange={(e) => update("district", e.target.value)}
              placeholder="e.g. Medak" className="input-field" />
            <datalist id="vw-districts">
              {DISTRICTS.map((d) => <option key={d.slug} value={d.name} />)}
            </datalist>
          </div>
          <div>
            <label className="label-display">Author</label>
            <input value={form.author} onChange={(e) => update("author", e.target.value)} className="input-field" />
          </div>
          <div>
            <label className="label-display">Cover Image URL</label>
            <input value={form.cover_image} onChange={(e) => update("cover_image", e.target.value)}
              placeholder="https://… (optional)" className="input-field" />
          </div>
        </div>

        {/* Content with write/preview tabs */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="label-display !mb-0">Content (Markdown)</label>
            <div className="flex gap-1">
              {["write", "preview"].map((t) => (
                <button key={t} onClick={() => setTab(t)} data-testid={`editor-tab-${t}`}
                  className={`px-3 py-1 rounded-full text-xs font-display font-semibold capitalize transition-colors ${
                    tab === t ? "bg-ink text-white" : "bg-stone-100 text-stone-600 hover:bg-stone-200"
                  }`}>
                  {t}
                </button>
              ))}
            </div>
          </div>
          {tab === "write" ? (
            <textarea data-testid="editor-content" value={form.content} onChange={(e) => update("content", e.target.value)}
              rows={18} placeholder={"## Overview\n\nWrite your article in Markdown…"}
              className="input-field font-mono !text-sm !leading-relaxed resize-y" />
          ) : (
            <div data-testid="editor-preview" className="md-preview border-2 border-stone-200 rounded-xl px-5 py-4 min-h-[200px] bg-white"
              dangerouslySetInnerHTML={{ __html: previewHtml }} />
          )}
        </div>

        {/* SEO & FAQ (AI-ready fields) */}
        <div className="border-t border-stone-100 pt-4">
          <button onClick={() => setSeoOpen((o) => !o)} className="font-display font-bold text-sm text-ink flex items-center gap-2">
            <span className={`transition-transform ${seoOpen ? "rotate-90" : ""}`}>▸</span>
            SEO & FAQ <span className="text-xs text-muted font-normal">(optional — auto-generated from title/excerpt when empty)</span>
          </button>
          {seoOpen && (
            <div className="mt-4 flex flex-col gap-4">
              <div>
                <label className="label-display">SEO Title</label>
                <input value={form.seo_title} onChange={(e) => update("seo_title", e.target.value)}
                  placeholder={form.title || "Defaults to the article title"} className="input-field" />
              </div>
              <div>
                <label className="label-display">SEO Description</label>
                <textarea value={form.seo_description} onChange={(e) => update("seo_description", e.target.value)} rows={2}
                  placeholder={form.excerpt || "Defaults to the excerpt"} className="input-field resize-none" />
              </div>
              <div>
                <label className="label-display">Keywords (comma-separated)</label>
                <input value={form.keywords} onChange={(e) => update("keywords", e.target.value)}
                  placeholder="healthcare business, medak, diagnostics" className="input-field" />
              </div>
              <div>
                <label className="label-display">FAQ (rendered + FAQPage schema)</label>
                {form.faq_json.map((f, i) => (
                  <div key={i} className="bg-stone-50 border border-stone-200 rounded-xl p-3 mb-2">
                    <input value={f.question} onChange={(e) => {
                      const faq = [...form.faq_json]; faq[i] = { ...faq[i], question: e.target.value }; update("faq_json", faq);
                    }} placeholder="Question?" className="input-field !min-h-0 !py-2 mb-2" />
                    <textarea value={f.answer} onChange={(e) => {
                      const faq = [...form.faq_json]; faq[i] = { ...faq[i], answer: e.target.value }; update("faq_json", faq);
                    }} placeholder="Answer" rows={2} className="input-field !min-h-0 !py-2 resize-none" />
                    <button onClick={() => update("faq_json", form.faq_json.filter((_, j) => j !== i))}
                      className="text-xs text-red-600 font-display font-semibold mt-1.5">Remove</button>
                  </div>
                ))}
                <button onClick={() => update("faq_json", [...form.faq_json, { question: "", answer: "" }])}
                  className="btn-ghost !px-3 !py-1.5 text-xs border border-stone-200">+ Add FAQ</button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Action bar */}
      <div className="sticky bottom-0 mt-5 bg-cream/95 backdrop-blur-md border-t border-stone-200 -mx-4 sm:-mx-6 px-4 sm:px-6 py-3 flex flex-wrap items-center gap-3">
        <button data-testid="editor-save-draft" onClick={() => save()} disabled={saving}
          className="btn-secondary !py-2.5 text-sm disabled:opacity-50">
          {saving ? "Saving…" : "Save Draft"}
        </button>
        {form.status === "published" ? (
          <>
            <button data-testid="editor-unpublish" onClick={unpublish} disabled={saving}
              className="btn-ghost !py-2.5 text-sm border border-stone-200 disabled:opacity-50">Unpublish</button>
            <Link href={`/research/${form.slug}`} target="_blank" className="btn-ghost !py-2.5 text-sm border border-stone-200">
              View live ↗
            </Link>
          </>
        ) : (
          <button data-testid="editor-publish" onClick={publish} disabled={saving}
            className="btn-primary !py-2.5 text-sm disabled:opacity-50">
            Publish →
          </button>
        )}
        <span className="text-xs text-muted ml-auto">Auto-saves every 30s</span>
      </div>
    </main>
  );
}
