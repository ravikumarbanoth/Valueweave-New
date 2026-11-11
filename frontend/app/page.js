import HomeHeroSearch from "@/components/HomeHeroSearch";
import HomeHeroValueProps from "@/components/HomeHeroValueProps";
import HomeHowItWorks from "@/components/HomeHowItWorks";
import HomeVideoEmbed from "@/components/HomeVideoEmbed";
import HomeFeatureGrid from "@/components/HomeFeatureGrid";
import HomeFeaturedOpportunities from "@/components/HomeFeaturedOpportunities";
import HomeSuccessJourney from "@/components/HomeSuccessJourney";
import HomeLiveActivity from "@/components/HomeLiveActivity";
import HomeWhySection from "@/components/HomeWhySection";
import HomeDiscoverSection from "@/components/HomeDiscoverSection";
import HomeSectorsSection from "@/components/HomeSectorsSection";
import HomeResearchArticles from "@/components/HomeResearchArticles";
import HomeConnections from "@/components/HomeConnections";
import HomeHeroHub from "@/components/HomeHeroHub";
import NetworkSection from "@/components/network/NetworkSection";
import HomeFinalCta from "@/components/HomeFinalCta";
import HomeNavClient from "@/components/HomeNavClient";
import { getPlatformSettings, enabled, setting } from "@/lib/settings";
import { NAVIGATION_SETTING_KEYS } from "@/lib/settings-schema";
import { BASE_URL, speakableJsonLd, webApplicationJsonLd, websiteJsonLd } from "@/lib/seo";

const NAV_LINKS = [
  { href: "/", label: "Home" },
  { href: "/discover", label: "Discover", settingKey: NAVIGATION_SETTING_KEYS.discover },
  { href: "/districts", label: "Districts", settingKey: NAVIGATION_SETTING_KEYS.districts },
  { href: "/readiness", label: "Industrial Readiness" },
  { href: "/manufacturing", label: "Manufacturing" },
  { href: "/scale", label: "Scale" },
  { href: "/network", label: "Network", settingKey: NAVIGATION_SETTING_KEYS.collaborators },
  { href: "/ai", label: "AI" },
];

export default async function LandingPage() {
  const settings = await getPlatformSettings();
  const navLinks = NAV_LINKS.filter((link) => !link.settingKey || enabled(settings, link.settingKey));
  const heroHeading = setting(settings, "homepage.hero.heading");
  const heroSubheading = setting(settings, "homepage.hero.subheading");
  const primaryCta = setting(settings, "homepage.cta.primary.label");
  const secondaryCta = setting(settings, "homepage.cta.secondary.label");
  const tertiaryCta = setting(settings, "homepage.cta.tertiary.label");
  const homepageVideoUrl = setting(settings, "homepage.video.url");
  const jsonLd = [websiteJsonLd(), webApplicationJsonLd(), speakableJsonLd({ url: BASE_URL })];

  // The page is one network. Every section sits in a <NetworkSection>, which
  // draws the same two rails and the same seam forks in one shared
  // coordinate system (components/network/geometry.js), so the lines run
  // unbroken from the hero to the footer — where FooterClient draws the hub
  // they converge on. `index` only varies how far each pair of rails bows;
  // it is a fixed sequence, not randomness.
  //
  // Order follows Discover → Opportunities → Research → how it all connects →
  // Explore → Learn → Connect → Participate. No section was removed in this
  // change; two moved up (opportunities, research) and one is new
  // (HomeConnections, real paths through the knowledge graph).
  return (
    <div className="min-h-screen bg-cream font-body">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      {/* ── NAV ───────────────────────────────────────────────── */}
      <HomeNavClient navLinks={navLinks} />

      {/* ── HERO: the question, the search, and the hub ─────────── */}
      <NetworkSection index={0} first testId="net-hero">
        <section className="pt-28 sm:pt-32 pb-16 sm:pb-20 px-4 sm:px-6 relative overflow-hidden">
          <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_60%_50%_at_50%_62%,rgba(249,115,22,0.13)_0%,transparent_60%),radial-gradient(ellipse_50%_50%_at_10%_80%,rgba(13,148,136,0.08)_0%,transparent_55%)]" />
          <div className="max-w-6xl mx-auto">
            <HomeHeroSearch heading={heroHeading} subheading={heroSubheading} />
            <HomeHeroValueProps primaryCta={primaryCta} secondaryCta={secondaryCta} tertiaryCta={tertiaryCta} />
            <HomeHeroHub />
          </div>
        </section>
      </NetworkSection>

      {/* "Who is here so far" (HomepageStats) was removed from the homepage
          earlier; the component is kept, not deleted. */}

      {/* ── OPPORTUNITIES ─────────────────────────────────────── */}
      <NetworkSection index={1} testId="net-opportunities"><HomeFeaturedOpportunities /></NetworkSection>

      {/* ── RESEARCH ──────────────────────────────────────────── */}
      <NetworkSection index={2} tone="warm" testId="net-research"><HomeResearchArticles /></NetworkSection>

      {/* ── HOW IT CONNECTS: real knowledge-graph paths ───────── */}
      <NetworkSection index={3} testId="net-connections"><HomeConnections /></NetworkSection>

      {/* ── EXPLORE: districts, skills, schemes, industries ───── */}
      <NetworkSection index={4} tone="warm" testId="net-explore"><HomeFeatureGrid /></NetworkSection>

      {/* ── LEARN: how it works, the video, the path ──────────── */}
      <NetworkSection index={5} testId="net-how"><HomeHowItWorks /></NetworkSection>
      <NetworkSection index={6} tone="warm" testId="net-video"><HomeVideoEmbed youtubeUrl={homepageVideoUrl} /></NetworkSection>
      <NetworkSection index={7} testId="net-journey"><HomeSuccessJourney /></NetworkSection>

      {/* ── CONNECT: people, and the gap they fill ────────────── */}
      <NetworkSection index={8} tone="warm" testId="net-activity"><HomeLiveActivity /></NetworkSection>
      <NetworkSection index={9} testId="net-why"><HomeWhySection /></NetworkSection>
      <NetworkSection index={10} tone="warm" testId="net-discover"><HomeDiscoverSection /></NetworkSection>
      <NetworkSection index={11} testId="net-sectors"><HomeSectorsSection /></NetworkSection>

      {/* ── PARTICIPATE ───────────────────────────────────────── */}
      <NetworkSection index={12} last testId="net-final"><HomeFinalCta /></NetworkSection>
    </div>
  );
}
