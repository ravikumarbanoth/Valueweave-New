export const NAVIGATION_SETTING_KEYS = {
  research: "navigation.research.enabled",
  districts: "navigation.districts.enabled",
  radar: "navigation.radar.enabled",
  collaborators: "navigation.collaborators.enabled",
  questions: "navigation.questions.enabled",
  discover: "navigation.discover.enabled",
  skills: "navigation.skills.enabled",
  schemes: "navigation.schemes.enabled",
  resources: "navigation.resources.enabled",
  roadmaps: "navigation.roadmaps.enabled",
};

export const DEFAULT_PLATFORM_SETTINGS = {
  "site.title": "ValueWeave",
  "site.description": "India's collaboration and opportunity discovery platform for builders, local businesses, and district-first entrepreneurship.",
  "site.tagline": "Where ambition finds its team.",
  // PX Phase 7. Was "Where Ambition Finds Its Team." with a 33-word
  // subheading. Both are still admin-editable; only the DEFAULTS changed.
  //
  // The test the brief sets is whether a heading helps answer one of five
  // questions a first-year student actually has — what can I explore, what
  // should I learn, what can I start, what support exists, what do I do next.
  // "Where Ambition Finds Its Team" answers none of them, and the subheading
  // took four lines on a phone to say the same thing at more length.
  "homepage.hero.heading": "Find what to learn, what to start, and who can help.",
  "homepage.hero.subheading": "Skills, business ideas and government schemes for every district in Telangana and Andhra Pradesh — researched from official sources, free to use.",
  "homepage.cta.primary.label": "Discover Yourself",
  "homepage.cta.secondary.label": "Explore Ideas",
  "homepage.cta.tertiary.label": "Find Collaborators",
  "homepage.video.url": "https://youtu.be/hRhhYQLPJ7Q?si=ZPAl8q878ZuNFZkY",
  "footer.text": "Where ambition finds its team. Find what to build and who to build it with — from your district.",
  "footer.contact_email": "valueweave.team@gmail.com",
  "footer.links": [
    { "href": "/about", "label": "About" },
    { "href": "/ideas", "label": "Idea Library" },
    { "href": "/research", "label": "Research" },
    { "href": "/district", "label": "Districts" },
    { "href": "/opportunity-radar", "label": "Opportunity Radar" },
    { "href": "/collaborators", "label": "Collaborators" },
    { "href": "/privacy", "label": "Privacy" },
    { "href": "/terms", "label": "Terms" }
  ],
  "contact.email": "valueweave.team@gmail.com",
  "announcement.enabled": false,
  "announcement.text": "",
  "maintenance.enabled": false,
  "maintenance.text": "ValueWeave is undergoing maintenance. Some features may be temporarily unavailable.",
  "theme.primary_color": "#f59e0b",
  "theme.secondary_color": "#14b8a6",
  "theme.accent_color": "#facc15",
  "social.youtube": "",
  "social.instagram": "",
  "social.x": "",
  "modules.skills.enabled": true,
  "modules.schemes.enabled": true,
  "modules.resources.enabled": true,
  "modules.roadmaps.enabled": true,
  "modules.opportunity_index.enabled": true,
  "homepage.sections.skills.enabled": true,
  "homepage.sections.schemes.enabled": true,
  "homepage.sections.resources.enabled": true,
  [NAVIGATION_SETTING_KEYS.research]: true,
  [NAVIGATION_SETTING_KEYS.districts]: true,
  [NAVIGATION_SETTING_KEYS.radar]: true,
  [NAVIGATION_SETTING_KEYS.collaborators]: true,
  [NAVIGATION_SETTING_KEYS.questions]: true,
  [NAVIGATION_SETTING_KEYS.discover]: true,
  [NAVIGATION_SETTING_KEYS.skills]: true,
  [NAVIGATION_SETTING_KEYS.schemes]: true,
  [NAVIGATION_SETTING_KEYS.resources]: true,
  [NAVIGATION_SETTING_KEYS.roadmaps]: true,
};

export const PLATFORM_SETTING_DEFINITIONS = [
  { key: "site.title", label: "Site Title", type: "text", category: "Branding" },
  { key: "site.description", label: "Site Description", type: "textarea", category: "SEO" },
  { key: "site.tagline", label: "Tagline", type: "text", category: "Branding" },
  { key: "homepage.hero.heading", label: "Hero Heading", type: "text", category: "Homepage" },
  { key: "homepage.hero.subheading", label: "Hero Subheading", type: "textarea", category: "Homepage" },
  { key: "homepage.cta.primary.label", label: "Primary CTA Label", type: "text", category: "Buttons" },
  { key: "homepage.cta.secondary.label", label: "Secondary CTA Label", type: "text", category: "Buttons" },
  { key: "homepage.cta.tertiary.label", label: "Tertiary CTA Label", type: "text", category: "Buttons" },
  { key: "homepage.video.url", label: "Homepage Video URL", type: "url", category: "Homepage" },
  { key: "homepage.sections.skills.enabled", label: "Show Skills Section", type: "boolean", category: "Homepage" },
  { key: "homepage.sections.schemes.enabled", label: "Show Schemes Section", type: "boolean", category: "Homepage" },
  { key: "homepage.sections.resources.enabled", label: "Show Resources Section", type: "boolean", category: "Homepage" },
  { key: "footer.text", label: "Footer Text", type: "textarea", category: "Footer" },
  { key: "footer.links", label: "Footer Links", type: "json", category: "Footer" },
  { key: "footer.contact_email", label: "Footer Contact Email", type: "email", category: "Footer" },
  { key: "contact.email", label: "Contact Email", type: "email", category: "Platform" },
  { key: "announcement.enabled", label: "Announcement Enabled", type: "boolean", category: "Platform" },
  { key: "announcement.text", label: "Announcement Text", type: "textarea", category: "Platform" },
  { key: "maintenance.enabled", label: "Maintenance Mode", type: "boolean", category: "Platform" },
  { key: "maintenance.text", label: "Maintenance Message", type: "textarea", category: "Platform" },
  { key: "modules.skills.enabled", label: "Enable Skills Module", type: "boolean", category: "Platform" },
  { key: "modules.schemes.enabled", label: "Enable Schemes Module", type: "boolean", category: "Platform" },
  { key: "modules.resources.enabled", label: "Enable Resources Module", type: "boolean", category: "Platform" },
  { key: "modules.roadmaps.enabled", label: "Enable Roadmaps Module", type: "boolean", category: "Platform" },
  { key: "modules.opportunity_index.enabled", label: "Enable Opportunity Index", type: "boolean", category: "Platform" },
  { key: "theme.primary_color", label: "Primary Color", type: "color", category: "Branding" },
  { key: "theme.secondary_color", label: "Secondary Color", type: "color", category: "Branding" },
  { key: "theme.accent_color", label: "Accent Color", type: "color", category: "Branding" },
  { key: "social.youtube", label: "YouTube URL", type: "url", category: "Footer" },
  { key: "social.instagram", label: "Instagram URL", type: "url", category: "Footer" },
  { key: "social.x", label: "X URL", type: "url", category: "Footer" },
  { key: NAVIGATION_SETTING_KEYS.research, label: "Show Research", type: "boolean", category: "Navigation" },
  { key: NAVIGATION_SETTING_KEYS.districts, label: "Show Districts", type: "boolean", category: "Navigation" },
  { key: NAVIGATION_SETTING_KEYS.radar, label: "Show Radar", type: "boolean", category: "Navigation" },
  { key: NAVIGATION_SETTING_KEYS.collaborators, label: "Show Collaborators", type: "boolean", category: "Navigation" },
  { key: NAVIGATION_SETTING_KEYS.questions, label: "Show Questions", type: "boolean", category: "Navigation" },
  { key: NAVIGATION_SETTING_KEYS.discover, label: "Show Discover Yourself", type: "boolean", category: "Navigation" },
  { key: NAVIGATION_SETTING_KEYS.skills, label: "Enable Skills Menu", type: "boolean", category: "Navigation" },
  { key: NAVIGATION_SETTING_KEYS.schemes, label: "Enable Schemes Menu", type: "boolean", category: "Navigation" },
  { key: NAVIGATION_SETTING_KEYS.resources, label: "Enable Resources Menu", type: "boolean", category: "Navigation" },
  { key: NAVIGATION_SETTING_KEYS.roadmaps, label: "Enable Roadmaps Menu", type: "boolean", category: "Navigation" },
];

export function getDefaultSetting(key) {
  return DEFAULT_PLATFORM_SETTINGS[key];
}

export function coerceSettingValue(type, value) {
  if (type === "boolean") return value === true || value === "true";
  if (type === "json") return Array.isArray(value) || (value && typeof value === "object") ? value : [];
  return value == null ? "" : String(value);
}
