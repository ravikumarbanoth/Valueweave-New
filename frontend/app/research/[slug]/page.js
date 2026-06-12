import { notFound } from "next/navigation";
import { getAllArticleSlugs, getArticleBySlug, getAllArticles } from "@/lib/mdx";
import { buildArticleMetadata, articleJsonLd, faqJsonLd, breadcrumbJsonLd, BASE_URL } from "@/lib/seo";
import { getArticleRelatedLinks } from "@/lib/internal-links";
import { ArticleTemplate } from "@/components/research/ArticleTemplate";
import { MDXContent } from "@/components/research/MDXContent";
import AppNavbar from "@/components/AppNavbar";

export async function generateStaticParams() {
  return getAllArticleSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }) {
  const article = getArticleBySlug(params.slug);
  if (!article) return {};
  return buildArticleMetadata(article);
}

export default function ResearchArticlePage({ params }) {
  const article = getArticleBySlug(params.slug);
  if (!article) notFound();

  const allArticles = getAllArticles();
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

  // Strip the raw MDX source before passing the article to the client
  // component — the body is rendered server-side below.
  const { content, ...articleMeta } = article;

  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify([
            articleJsonLd(article),
            faqJsonLd(article.faq),
            breadcrumbJsonLd(breadcrumbs),
          ]),
        }}
      />
      <ArticleTemplate
        article={articleMeta}
        relatedLinks={relatedLinks}
        relatedArticles={relatedArticles}
        mdx={<MDXContent source={content} />}
      />
    </div>
  );
}
