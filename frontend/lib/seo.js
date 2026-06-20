// ValueWeave — Reusable SEO and GEO utilities.

const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL || "https://valueweave.in";

const ORG_JSON_LD = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "ValueWeave",
  url: BASE_URL,
  logo: `${BASE_URL}/logo.png`,
  description:
    "ValueWeave is a Bharat-focused collaboration and opportunity discovery platform for research, district intelligence, business ideas, collaborators, and local opportunities.",
  sameAs: [
    "https://www.youtube.com/@valueweave",
    "https://www.instagram.com/valueweave",
    "https://x.com/valueweave",
  ],
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
export function websiteJsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "ValueWeave",
    url: BASE_URL,
    description: ORG_JSON_LD.description,
    publisher: ORG_JSON_LD,
    potentialAction: {
      "@type": "SearchAction",
      target: `${BASE_URL}/search?q={search_term_string}`,
      "query-input": "required name=search_term_string",
    },
  };
}

export function webApplicationJsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    name: "ValueWeave",
    url: BASE_URL,
    applicationCategory: "BusinessApplication",
    operatingSystem: "Web",
    description: "Discover business ideas, district intelligence, research, opportunities, and collaborators on ValueWeave.",
    offers: { "@type": "Offer", price: "0", priceCurrency: "INR" },
    publisher: ORG_JSON_LD,
  };
}

export function speakableJsonLd({ url = BASE_URL, selectors = ["h1", "[data-speakable]"] } = {}) {
  return {
    "@context": "https://schema.org",
    "@type": "WebPage",
    url,
    speakable: {
      "@type": "SpeakableSpecification",
      cssSelector: selectors,
    },
  };
}

export function articleJsonLd(article) {
  return {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: article.title,
    description: article.metaDescription,
    datePublished: article.publishedAt,
    dateModified: article.updatedAt,
    author: { "@type": "Organization", name: article.author || "ValueWeave Research Team", url: BASE_URL },
    publisher: ORG_JSON_LD,
    url: `${BASE_URL}/research/${article.slug}`,
    keywords: [article.sector, ...article.districtTags, ...article.stateTags, ...(article.keywords || [])].join(", "),
    video: article.video?.youtubeUrl
      ? {
          "@type": "VideoObject",
          name: article.video.title || article.title,
          description: article.video.description || article.metaDescription,
          embedUrl: article.video.embedUrl,
          uploadDate: article.publishedAt,
        }
      : undefined,
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

export function businessIdeaJsonLd(idea, sector) {
  return {
    "@context": "https://schema.org",
    "@type": "CreativeWork",
    name: idea.title,
    description: idea.short_description,
    url: `${BASE_URL}/ideas/${idea.slug}`,
    about: sector?.label || idea.sector,
    keywords: (idea.tags || []).join(", "),
    audience: (idea.ideal_for || []).join(", "),
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

export function pageSummaryJsonLd({ url, title, summary, about, keywords = [] }) {
  return {
    "@context": "https://schema.org",
    "@type": "WebPage",
    url,
    name: title,
    description: summary,
    about,
    keywords: Array.isArray(keywords) ? keywords.join(", ") : keywords,
  };
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
