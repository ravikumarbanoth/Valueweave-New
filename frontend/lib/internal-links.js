// ValueWeave — Automated internal linking engine.
// Adapted to the EXISTING platform routes: ideas → /ideas/[slug] (Idea
// Library), collaborators → /explore (Opportunity Marketplace).

function toTitleCase(str) {
  return str
    .split(" ")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");
}

function sectorToRadarSegment(sector) {
  const map = {
    agriculture: "agriculture",
    agritech: "agriculture",
    healthcare: "healthcare",
    "health care": "healthcare",
    food: "agriculture",
    "food processing": "agriculture",
    education: "students",
    technology: "students",
    media: "students",
    energy: "telangana",
    recycling: "andhra-pradesh",
    manufacturing: "telangana",
    retail: "under-5-lakhs",
    finance: "under-5-lakhs",
    services: "under-5-lakhs",
    logistics: "telangana",
    tourism: "andhra-pradesh",
    aquaculture: "andhra-pradesh",
  };
  return map[(sector || "").toLowerCase()] || null;
}

// ── Research article → related links ──
export function getArticleRelatedLinks(article) {
  const links = [];

  for (const district of article.districtTags) {
    links.push({
      label: `Opportunities in ${toTitleCase(district)}`,
      href: `/district/${district.toLowerCase().replace(/\s+/g, "-")}`,
      type: "district",
      relevanceScore: 90,
    });
  }

  for (const ideaSlug of article.relatedIdeas) {
    links.push({
      label: toTitleCase(ideaSlug.replace(/-/g, " ")),
      href: `/ideas/${ideaSlug}`,
      type: "idea",
      relevanceScore: 85,
    });
  }

  const radarSegment = sectorToRadarSegment(article.sector);
  if (radarSegment) {
    links.push({
      label: `${toTitleCase(article.sector)} Opportunity Radar`,
      href: `/opportunity-radar/${radarSegment}`,
      type: "radar",
      relevanceScore: 80,
    });
  }

  for (const state of article.stateTags) {
    const stateSlug = state.toLowerCase().replace(/\s+/g, "-");
    links.push({
      label: `Top Opportunities in ${state}`,
      href: `/opportunity-radar/${stateSlug}`,
      type: "radar",
      relevanceScore: 75,
    });
  }

  links.push({
    label: "Explore live opportunities",
    href: "/explore",
    type: "collaborator",
    relevanceScore: 70,
  });

  return links.sort((a, b) => (b.relevanceScore || 0) - (a.relevanceScore || 0));
}

// ── District page → related links ──
export function getDistrictRelatedLinks(district, allArticles) {
  const links = [];

  const matchingArticles = (allArticles || []).filter((a) =>
    a.districtTags.map((t) => t.toLowerCase()).includes(district.slug.toLowerCase())
  );
  for (const article of matchingArticles.slice(0, 5)) {
    links.push({
      label: article.title,
      href: `/research/${article.slug}`,
      type: "research",
      relevanceScore: 90,
    });
  }

  const stateSlug = district.state.toLowerCase().replace(/\s+/g, "-");
  links.push({
    label: `${district.state} Opportunity Radar`,
    href: `/opportunity-radar/${stateSlug}`,
    type: "radar",
    relevanceScore: 80,
  });

  links.push({
    label: "Browse the Idea Library",
    href: "/ideas",
    type: "idea",
    relevanceScore: 78,
  });

  links.push({
    label: `Explore opportunities near ${district.name}`,
    href: "/explore",
    type: "collaborator",
    relevanceScore: 70,
  });

  return links.sort((a, b) => (b.relevanceScore || 0) - (a.relevanceScore || 0));
}

// ── Opportunity radar item → related links ──
export function getRadarItemLinks(item) {
  const links = [];

  if (item.researchSlug) {
    links.push({ label: "Read Full Research", href: `/research/${item.researchSlug}`, type: "research", relevanceScore: 95 });
  }
  if (item.ideaSlug) {
    links.push({ label: "View Business Idea", href: `/ideas/${item.ideaSlug}`, type: "idea", relevanceScore: 90 });
  }
  for (const district of (item.districtSuitability || []).slice(0, 3)) {
    links.push({
      label: `${toTitleCase(district.replace(/-/g, " "))} District Profile`,
      href: `/district/${district}`,
      type: "district",
      relevanceScore: 80,
    });
  }
  links.push({ label: "Explore live opportunities", href: "/explore", type: "collaborator", relevanceScore: 75 });

  return links;
}
