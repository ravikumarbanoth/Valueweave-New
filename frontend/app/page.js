import Link from "next/link";
import { Shield, Smartphone, Sparkles } from "lucide-react";
import HomepageStats from "@/components/HomepageStats";
import HomeStartHere from "@/components/HomeStartHere";
import HomeHowItWorks from "@/components/HomeHowItWorks";
import HomeVideoEmbed from "@/components/HomeVideoEmbed";
import HomeFeatureGrid from "@/components/HomeFeatureGrid";
import HomeFeaturedOpportunities from "@/components/HomeFeaturedOpportunities";
import HomeSuccessJourney from "@/components/HomeSuccessJourney";
import HomeLiveActivity from "@/components/HomeLiveActivity";
import MobileStartHereSheet from "@/components/MobileStartHereSheet";
import MobileNavMenu from "@/components/MobileNavMenu";
import { getPlatformSettings, enabled, setting } from "@/lib/settings";
import { NAVIGATION_SETTING_KEYS } from "@/lib/settings-schema";
import { BASE_URL, speakableJsonLd, webApplicationJsonLd, websiteJsonLd } from "@/lib/seo";

const FLOATING_CARDS = [
  { top: "8%", left: "12%", emoji: "🤖", label: "AI · Hyderabad", bg: "bg-blue-50", border: "border-blue-200" },
  { top: "15%", right: "0%", emoji: "🌾", label: "Agri · Warangal", bg: "bg-emerald-50", border: "border-emerald-200" },
  { bottom: "14%", left: "0%", emoji: "🏪", label: "Retail · Vijayawada", bg: "bg-amber-50", border: "border-amber-200" },
  { bottom: "22%", right: "10%", emoji: "⚡", label: "EV · Coimbatore", bg: "bg-violet-50", border: "border-violet-200" },
];

const GAP_CARDS = [
  {
    icon: "🔍",
    title: "Talent without visibility",
    desc: "A diploma-holder electrician in Warangal, a coder in Vizag, a baker in Guntur — full of skill, invisible to the people who'd build with them.",
  },
  {
    icon: "💡",
    title: "Ideas without teams",
    desc: "Founders in tier-2 cities like Hyderabad, Vijayawada, Coimbatore have ambition and insight, but no easy way to find a co-founder locally.",
  },
  {
    icon: "🤝",
    title: "Trust without proof",
    desc: "LinkedIn rewards titles; Fiverr rewards bidding. Neither rewards real collaboration. We're building the third option.",
  },
];

const DISCOVER_CARDS = [
  { emoji: "💡", label: "Innovator", desc: "Product & Strategy Lead — spots opportunities others miss.", bg: "bg-violet-50", border: "border-violet-200" },
  { emoji: "🦁", label: "Leader", desc: "CEO / Managing Director — sets direction and owns outcomes.", bg: "bg-rose-50", border: "border-rose-200" },
  { emoji: "🏗️", label: "Builder", desc: "Operations & Delivery Lead — makes things actually run.", bg: "bg-amber-50", border: "border-amber-200" },
  { emoji: "🎙️", label: "Influencer", desc: "Marketing & Sales Lead — tells the story, builds the brand.", bg: "bg-pink-50", border: "border-pink-200" },
];

const NAV_LINKS = [
  { href: "/discover", label: "Discover", settingKey: NAVIGATION_SETTING_KEYS.discover },
  { href: "/ideas", label: "Ideas" },
  { href: "/explore", label: "Explore" },
  { href: "/collaborators", label: "Collaborators", settingKey: NAVIGATION_SETTING_KEYS.collaborators },
  { href: "/research", label: "Research", settingKey: NAVIGATION_SETTING_KEYS.research },
  { href: "/district", label: "Districts", settingKey: NAVIGATION_SETTING_KEYS.districts },
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
      <nav className="fixed top-0 inset-x-0 z-50 bg-cream/85 backdrop-blur-md border-b border-stone-200/60">
        <div className="max-w-6xl mx-auto h-16 px-4 sm:px-6 flex items-center justify-between gap-3">
          <Link href="/" className="flex items-center gap-2.5 shrink-0">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500 to-yellow-400 flex items-center justify-center shadow-md shadow-amber-500/30">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 3L4 7.5V16.5L12 21L20 16.5V7.5L12 3Z" stroke="#fff" strokeWidth="2" strokeLinejoin="round"/><path d="M4 7.5L12 12M12 12L20 7.5M12 12V21" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>
            </div>
            <span className="font-display font-extrabold text-lg tracking-tight">Value<span className="text-amber-500">Weave</span></span>
          </Link>

          {/* Desktop nav links */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((l) => (
              <Link key={l.href} href={l.href} className="text-sm font-display font-semibold text-muted hover:text-ink px-3 py-2 rounded-lg hover:bg-stone-100 transition-colors">
                {l.label}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <Link href="/signin" data-testid="nav-signin" className="btn-secondary !py-2 !px-4 text-sm hidden sm:inline-flex">Sign in</Link>
            <Link href="/get-started" data-testid="nav-join" className="btn-primary !py-2 !px-4 sm:!px-5 text-sm">
              <span className="sm:hidden">Join</span>
              <span className="hidden sm:inline">Join ValueWeave</span>
            </Link>

            {/* Mobile hamburger */}
            <MobileNavMenu />
          </div>
        </div>
      </nav>

      {/* ── HERO ──────────────────────────────────────────────── */}
      <section className="pt-32 pb-20 px-4 sm:px-6 relative overflow-hidden">
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_60%_60%_at_80%_20%,rgba(249,115,22,0.14)_0%,transparent_60%),radial-gradient(ellipse_50%_50%_at_10%_80%,rgba(13,148,136,0.12)_0%,transparent_55%)]" />
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-12 items-center">
          <div>
            <div className="inline-flex items-center gap-2 bg-amber-200 rounded-full px-4 py-1.5 mb-6 animate-fadeUp">
              <span className="w-2 h-2 rounded-full bg-amber-500 ring-4 ring-amber-500/20" />
              <span className="text-xs font-display font-semibold text-amber-700">Now Open · Bharat Edition</span>
            </div>
            <h1 className="h-hero mb-6 animate-fadeUp" data-speakable>
              {heroHeading}
            </h1>
            <p className="text-base sm:text-lg text-muted leading-relaxed mb-7 max-w-md animate-fadeUp" style={{ animationDelay: "0.1s" }} data-speakable>
              {heroSubheading}
            </p>

            {/* Primary CTAs — only 3 */}
            <div className="flex flex-wrap gap-3 mb-6 animate-fadeUp" style={{ animationDelay: "0.2s" }}>
              <Link href="/discover" data-testid="hero-cta-discover" className="btn-teal">🧠 {primaryCta}</Link>
              <Link href="/ideas" data-testid="hero-cta-ideas" className="btn-primary">💡 {secondaryCta}</Link>
              <Link href="/collaborators" data-testid="hero-cta-collabs" className="btn-secondary">🤝 {tertiaryCta}</Link>
            </div>

            <ul className="flex flex-wrap gap-x-5 gap-y-2 animate-fadeUp" style={{ animationDelay: "0.3s" }}>
              <li className="inline-flex items-center gap-1.5 text-xs sm:text-sm text-muted">
                <Shield size={14} className="text-teal-600" /> Google-authenticated profiles
              </li>
              <li className="inline-flex items-center gap-1.5 text-xs sm:text-sm text-muted">
                <Smartphone size={14} className="text-teal-600" /> Mobile-first
              </li>
              <li className="inline-flex items-center gap-1.5 text-xs sm:text-sm text-muted">
                <Sparkles size={14} className="text-teal-600" /> Free to join
              </li>
            </ul>
          </div>

          <div className="relative h-[440px] hidden md:block">
            <div className="absolute inset-0 m-auto w-72 h-72 rounded-[60%_40%_30%_70%/60%_30%_70%_40%] bg-gradient-to-br from-amber-500/15 to-teal-500/15" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="relative w-24 h-24 rounded-full bg-gradient-to-br from-amber-500 to-yellow-400 flex items-center justify-center shadow-xl shadow-amber-500/30">
                <svg width="44" height="44" viewBox="0 0 24 24" fill="none"><path d="M12 3L4 7.5V16.5L12 21L20 16.5V7.5L12 3Z" stroke="#fff" strokeWidth="1.8" strokeLinejoin="round"/><path d="M4 7.5L12 12M12 12L20 7.5M12 12V21" stroke="#fff" strokeWidth="1.8" strokeLinecap="round"/></svg>
                <span className="absolute -inset-2 rounded-full border-2 border-amber-500/30 animate-ping" />
              </div>
            </div>
            {FLOATING_CARDS.map((card, index) => (
              <div
                key={card.label}
                className={`absolute ${card.bg} border ${card.border} rounded-2xl px-3 py-2 flex items-center gap-2 shadow-sm animate-float`}
                style={{ top: card.top, left: card.left, right: card.right, bottom: card.bottom, animationDelay: `${index * 0.5}s` }}
              >
                <span className="text-xl">{card.emoji}</span>
                <span className="text-xs font-display font-semibold text-ink whitespace-nowrap">{card.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── 1. START HERE ─────────────────────────────────────── */}
      <HomeStartHere />

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
      <section id="why" className="bg-warm py-20 sm:py-24 px-4 sm:px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <span className="chip bg-teal-100 text-teal-600 mb-4">WHY VALUEWEAVE EXISTS</span>
            <h2 className="h-section">
              The collaboration gap in<br />
              <span className="text-teal-500">India&apos;s grassroots economy.</span>
            </h2>
            <p className="mt-5 text-muted max-w-2xl mx-auto text-base sm:text-lg leading-relaxed">
              Millions of brilliant minds across India aren&apos;t held back by lack of skill — they&apos;re held back by lack of the right connections.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-5">
            {GAP_CARDS.map((card) => <GapCard key={card.title} {...card} />)}
          </div>

          <div className="text-center mt-12">
            <p className="font-display font-bold text-lg max-w-2xl mx-auto leading-snug text-ink">
              ValueWeave is the missing bridge — between skill and opportunity, between ambition and team, between idea and execution.
            </p>
          </div>
        </div>
      </section>

      {/* ── 10. DISCOVER YOURSELF DETAIL ──────────────────────── */}
      <section id="discover" className="py-20 sm:py-24 px-4 sm:px-6">
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-12 items-center">
          <div>
            <span className="chip bg-teal-100 text-teal-600 mb-4">FREE ASSESSMENT</span>
            <h2 className="h-section mb-5">
              Not sure where to start?<br />
              <span className="text-teal-500">Find your founder DNA.</span>
            </h2>
            <p className="text-muted text-base sm:text-lg leading-relaxed mb-6 max-w-md">
              A free 7-minute assessment that maps your personality, sector interests, budget, and district into your entrepreneur archetype, founder role, and the business ideas best suited to where you live.
            </p>
            <ul className="flex flex-col gap-2.5 mb-7">
              {[
                ["🧠", "Your archetype & founder role — Innovator, Builder, Leader & more"],
                ["📍", "Business ideas matched to your district's real opportunity demand"],
                ["💰", "Filtered by what you can actually invest, from ₹30K to ₹15L+"],
                ["🚀", "Turn your top idea into a live opportunity post in one click"],
              ].map(([icon, text]) => (
                <li key={text} className="flex items-start gap-2.5 text-sm text-muted">
                  <span className="text-base">{icon}</span>
                  <span className="leading-relaxed">{text}</span>
                </li>
              ))}
            </ul>
            <Link href="/discover" data-testid="section-cta-discover" className="btn-teal">
              Take the free assessment →
            </Link>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {DISCOVER_CARDS.map((card) => (
              <div key={card.label} className={`${card.bg} border ${card.border} rounded-2xl p-5 hover:-translate-y-1 hover:shadow-md transition-all`}>
                <div className="text-3xl mb-2">{card.emoji}</div>
                <div className="font-display font-bold text-sm mb-1">{card.label}</div>
                <div className="text-xs text-muted leading-relaxed">{card.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── 11. BUILT FOR INDIA'S BUILDERS ────────────────────── */}
      <section className="py-20 sm:py-24 px-4 sm:px-6 bg-warm">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <span className="chip bg-amber-100 text-amber-700 mb-4">EVERY SKILL HAS A HOME</span>
            <h2 className="h-section">
              Built for India&apos;s <span className="text-amber-500">builders.</span>
            </h2>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { e: "🤖", l: "AI & Tech", c: "bg-blue-50" },
              { e: "🏪", l: "Local Biz", c: "bg-amber-50" },
              { e: "⚡", l: "EV Tech", c: "bg-green-50" },
              { e: "🚁", l: "Drone", c: "bg-violet-50" },
              { e: "🌾", l: "Agriculture", c: "bg-emerald-50" },
              { e: "🎓", l: "Student", c: "bg-rose-50" },
              { e: "🔧", l: "Trades", c: "bg-yellow-50" },
              { e: "📱", l: "Digital", c: "bg-sky-50" },
            ].map((cat) => (
              <div key={cat.l} className={`${cat.c} rounded-2xl p-5 text-center border border-stone-100 hover:-translate-y-1 hover:shadow-sm transition-all`}>
                <div className="text-3xl mb-2">{cat.e}</div>
                <div className="font-display font-bold text-sm">{cat.l}</div>
              </div>
            ))}
          </div>
          <div className="text-center mt-10">
            <Link href="/explore" className="btn-secondary">Explore opportunities →</Link>
          </div>
        </div>
      </section>

      {/* ── 12. FINAL CTA ─────────────────────────────────────── */}
      <section className="bg-ink text-white py-20 sm:py-24 px-4 sm:px-6 relative overflow-hidden">
        <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-amber-500/20 blur-3xl" />
        <div className="absolute -bottom-20 -left-20 w-96 h-96 rounded-full bg-teal-500/20 blur-3xl" />
        <div className="max-w-3xl mx-auto text-center relative">
          <span className="chip bg-amber-500/20 text-amber-300 border border-amber-500/30 mb-5">JOIN THE FIRST WAVE</span>
          <h2 className="font-display font-extrabold text-4xl sm:text-5xl md:text-6xl tracking-tight leading-[1.05] mb-5">
            Start building with<br />
            <span className="bg-gradient-to-r from-amber-500 via-yellow-400 to-teal-500 bg-clip-text text-transparent">your people.</span>
          </h2>
          <p className="text-white/60 text-base sm:text-lg mb-9 leading-relaxed">
            Free to join. Google sign-in. Mobile-first. Built for Bharat.
          </p>
          <div className="flex items-center justify-center gap-3 flex-wrap">
            <Link href="/get-started" data-testid="footer-cta-join" className="btn-primary !px-7 !py-3.5 text-base">
              Join ValueWeave ✨
            </Link>
            <Link href="/signin" data-testid="footer-cta-signin" className="inline-flex items-center justify-center gap-2 bg-white/10 hover:bg-white/15 border border-white/20 text-white rounded-full px-7 py-3.5 font-display font-semibold text-base transition-colors min-h-[44px]">
              Sign in
            </Link>
          </div>
        </div>
      </section>

      {/* ── MOBILE FLOATING START-HERE SHEET ──────────────────── */}
      <MobileStartHereSheet />
    </div>
  );
}

function GapCard({ icon, title, desc }) {
  return (
    <div className="card-base p-6 hover:-translate-y-1 hover:shadow-md transition-all">
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="font-display font-bold text-base mb-2">{title}</h3>
      <p className="text-sm text-muted leading-relaxed">{desc}</p>
    </div>
  );
}
