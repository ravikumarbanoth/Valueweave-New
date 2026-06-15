import { notFound } from "next/navigation";
import { compileMDX } from "next-mdx-remote/rsc";
import remarkGfm from "remark-gfm";
import { marked } from "marked";
import { getAllArticleSlugs } from "@/lib/mdx";
import { getCombinedArticles, getCombinedArticleBySlug } from "@/lib/research";
import { buildArticleMetadata, articleJsonLd, faqJsonLd, breadcrumbJsonLd, BASE_URL } from "@/lib/seo";
import { getArticleRelatedLinks } from "@/lib/internal-links";
import { ArticleTemplate } from "@/components/research/ArticleTemplate";
import { mdxComponents } from "@/components/research/MDXContent";
import AppNavbar from "@/components/AppNavbar";
import PageTracker from "@/components/PageTracker";
import RequestContentWidget from "@/components/RequestContentWidget";

// MDX file articles are prerendered; database article slugs are not known
// at build time, so dynamicParams (default true) renders them on demand
// and ISR caches them. Updates from the admin editor appear within 5 min.
export const revalidate = 300;

export async function generateStaticParams() {
  return getAllArticleSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }) {
  const article = await getCombinedArticleBySlug(params.slug);
  if (!article) return {};
  return buildArticleMetadata(article);
}

// Render markdown/MDX defensively: admin-typed content may contain
// characters that are invalid MDX (e.g. a stray "{"). Try the rich MDX
// pipeline first (Callouts, themed tables); fall back to plain markdown.
async function renderBody(article) {
  try {
    const { content } = await compileMDX({
      source: article.content,
      components: mdxComponents,
      options: { mdxOptions: { remarkPlugins: [remarkGfm] } },
    });
    return content;
  } catch {
    const html = marked.parse(article.content || "");
    return <div className="md-preview" dangerouslySetInnerHTML={{ __html: html }} />;
  }
}

export default async function ResearchArticlePage({ params }) {
  const article = await getCombinedArticleBySlug(params.slug);
  if (!article) notFound();

  const allArticles = await getCombinedArticles();
  const relatedLinks = getArticleRelatedLinks(article);
  const relatedArticles = allArticles
    .filter((a) => a.category === article.category || article.relatedIdeas.includes(a.slug))
    .filter((a) => a.slug !== article.slug)
    .slice(0, 3);

  const breadcrumbs = [
    { name: "Home", url: BASE_URL },
    { name: "Research", url: `${BASE_URL}/research` },
    { name: article.title, url: `${BASE_URL}/research/${article.slug}` },
  ];

  const mdx = await renderBody(article);
  const { content, ...articleMeta } = article;

  const jsonLd = [articleJsonLd(article), breadcrumbJsonLd(breadcrumbs)];
  if (article.faq.length > 0) jsonLd.push(faqJsonLd(article.faq));

  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <PageTracker
        pageType="research"
        slug={article.slug}
        title={article.title}
        district={article.district || null}
        sector={article.category || null}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <ArticleTemplate
        article={articleMeta}
        relatedLinks={relatedLinks}
        relatedArticles={relatedArticles}
        mdx={mdx}
      />
      <div className="max-w-3xl mx-auto px-4 pb-10">
        <div className="flex items-center justify-between pt-6 border-t border-stone-200 mt-6">
          <p className="text-[13px] text-stone-400">Can&apos;t find what you need?</p>
          <RequestContentWidget
            defaultType="research"
            district={article.district || null}
            sector={article.category || null}
            prefillTitle={article.title}
            buttonLabel="Request Related Article"
            compact
          />
        </div>
      </div>
    </div>
  );
}
