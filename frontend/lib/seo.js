// ValueWeave — Reusable SEO utilities (metadata, JSON-LD, sitemap helpers).
// Adapted from the SEO Growth Engine pack to plain JS and the existing
// layout.js metadata conventions.

const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL || "https://valueweave.in";

const ORG_JSON_LD = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "ValueWeave",
  url: BASE_URL,
  logo: `${BASE_URL}/logo.png`,
  description:
    "ValueWeave connects skilled youth and entrepreneurs in tier-2/tier-3 India with local business opportunities, collaborators, and resources.",
  address: { "@type": "PostalAddress", addressRegion: "Telangana", addressCountry: "IN" },
};

// ── Base metadata ──
export function buildBaseMetadata(overrides = {}) {
  return {
    metadataBase: new URL(BASE_URL),
    description:
      "Discover local business ideas, find collaborators, and explore district-level opportunities across Telangana and Andhra Pradesh.",
    openGraph: {
      siteName: "ValueWeave",
      type: "website",
      locale: "en_IN",
    },
    twitter: { card: "summary_large_image" },
    robots: { index: true, follow: true, googleBot: { index: true, follow: true } },
    ...overrides,
  };
}

// ── Research article metadata ──
export function buildArticleMetadata(article) {
  const url = `${BASE_URL}/research/${article.slug}`;
  return buildBaseMetadata({
    title: article.metaTitle || article.title,
    description: article.metaDescription,
    alternates: { canonical: url },
    openGraph: {
      siteName: "ValueWeave",
      title: article.metaTitle || article.title,
      description: article.metaDescription,
      url,
      type: "article",
      publishedTime: article.publishedAt,
      modifiedTime: article.updatedAt,
      tags: [article.sector, ...article.districtTags, ...article.stateTags],
    },
    twitter: {
      card: "summary_large_image",
      title: article.metaTitle || article.title,
      description: article.metaDescription,
    },
  });
}

// ── District page metadata ──
export function buildDistrictMetadata(district) {
  const title = `Business Opportunities in ${district.name}, ${district.state}`;
  const description = `Explore top business ideas, emerging sectors, government schemes, and collaborator opportunities in ${district.name} district.`;
  const url = `${BASE_URL}/district/${district.slug}`;
  return buildBaseMetadata({
    title,
    description,
    alternates: { canonical: url },
    openGraph: { siteName: "ValueWeave", title, description, url, type: "website" },
  });
}

// ── JSON-LD generators ──
export function articleJsonLd(article) {
  return {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: article.title,
    description: article.metaDescription,
    datePublished: article.publishedAt,
    dateModified: article.updatedAt,
    author: { "@type": "Organization", name: "ValueWeave Research Team", url: BASE_URL },
    publisher: ORG_JSON_LD,
    url: `${BASE_URL}/research/${article.slug}`,
    keywords: [article.sector, ...article.districtTags, ...article.stateTags].join(", "),
  };
}

export function faqJsonLd(faqs) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: (faqs || []).map((faq) => ({
      "@type": "Question",
      name: faq.question,
      acceptedAnswer: { "@type": "Answer", text: faq.answer },
    })),
  };
}

export function localBusinessJsonLd(district) {
  return {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    name: `ValueWeave — ${district.name}`,
    description: district.profileSummary,
    address: {
      "@type": "PostalAddress",
      addressLocality: district.name,
      addressRegion: district.state,
      addressCountry: "IN",
    },
    url: `${BASE_URL}/district/${district.slug}`,
  };
}

export function breadcrumbJsonLd(items) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  };
}

export function organizationJsonLd() {
  return ORG_JSON_LD;
}

// ── Sitemap entry helper ──
export function sitemapEntry(path, opts = {}) {
  return {
    url: `${BASE_URL}${path}`,
    lastModified: opts.lastMod || new Date().toISOString(),
    changeFrequency: opts.changeFreq || "weekly",
    priority: opts.priority ?? 0.7,
  };
}

export { BASE_URL };
