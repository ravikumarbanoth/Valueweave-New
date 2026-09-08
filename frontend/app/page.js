import HomepageStats from "@/components/HomepageStats";
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

  return (
    <div className="min-h-screen bg-cream font-body">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      {/* ── NAV ───────────────────────────────────────────────── */}
      <HomeNavClient navLinks={navLinks} />

      {/* ── HERO ────────────────────────────────────────────────── */}
      <section className="pt-28 sm:pt-32 pb-16 sm:pb-20 px-4 sm:px-6 relative overflow-hidden">
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_60%_60%_at_80%_20%,rgba(249,115,22,0.14)_0%,transparent_60%),radial-gradient(ellipse_50%_50%_at_10%_80%,rgba(13,148,136,0.12)_0%,transparent_55%)]" />
        <div className="max-w-6xl mx-auto">
          <HomeHeroSearch heading={heroHeading} subheading={heroSubheading} />
          <HomeHeroValueProps primaryCta={primaryCta} secondaryCta={secondaryCta} tertiaryCta={tertiaryCta} />
        </div>
      </section>

      {/* ── 2. STATS ──────────────────────────────────────────── */}
      <HomepageStats />

      {/* ── 3. HOW VALUEWEAVE WORKS ───────────────────────────── */}
      <HomeHowItWorks />

      {/* ── 4. EXPLAINER VIDEO ────────────────────────────────── */}
      <HomeVideoEmbed youtubeUrl={homepageVideoUrl} />

      {/* ── 5. WHAT YOU CAN DO HERE ───────────────────────────── */}
      <HomeFeatureGrid />

      {/* ── 6. FEATURED OPPORTUNITIES ─────────────────────────── */}
      <HomeFeaturedOpportunities />

      {/* ── 7. SUCCESS JOURNEY ───────────────────────────────── */}
      <HomeSuccessJourney />

      {/* ── 8. LIVE ACTIVITY ──────────────────────────────────── */}
      <HomeLiveActivity />

      {/* ── 9. COLLABORATION GAP ──────────────────────────────── */}
      <HomeWhySection />

      {/* ── 10. DISCOVER YOURSELF DETAIL ──────────────────────── */}
      <HomeDiscoverSection />

      {/* ── 11. BUILT FOR INDIA'S BUILDERS ────────────────────── */}
      <HomeSectorsSection />

      {/* ── 12. FINAL CTA ─────────────────────────────────────── */}
      <HomeFinalCta />
    </div>
  );
}
