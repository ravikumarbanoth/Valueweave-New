import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Sparkles, Users, MapPin, Lightbulb, Compass, Handshake, ArrowUpRight } from "lucide-react";
import { fetchIdeas } from "@/lib/api";
import IdeaCard from "@/components/IdeaCard";

export default function Landing() {
  const [featured, setFeatured] = React.useState([]);

  React.useEffect(() => {
    fetchIdeas({ featured_only: true, limit: 6 }).then(setFeatured).catch(() => {});
  }, []);

  return (
    <div data-testid="landing-page">
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 vw-grain pointer-events-none" />
        <div className="vw-container pt-14 md:pt-24 pb-12 md:pb-20 grid grid-cols-1 lg:grid-cols-12 gap-10 items-center relative">
          <div className="lg:col-span-7 space-y-6">
            <span className="vw-chip">
              <Sparkles className="h-3 w-3" /> Bharat-first builder ecosystem
            </span>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.05]" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              Build the future of Bharat,
              <span className="block text-primary">together.</span>
            </h1>
            <p className="text-base md:text-lg text-muted-foreground max-w-xl leading-relaxed">
              Discover real, grounded business ideas — from soil testing labs and AI content studios to drone services — with the team, capital and district fit to make them happen.
            </p>
            <div className="flex flex-wrap gap-3 pt-2">
              <Link to="/ideas" className="vw-btn-primary" data-testid="hero-explore-ideas-cta">
                Explore Idea Library <ArrowRight className="h-4 w-4" />
              </Link>
              <Link to="/dashboard" className="vw-btn-outline" data-testid="hero-dashboard-cta">
                Go to Dashboard
              </Link>
            </div>
            <div className="flex items-center gap-6 pt-4 text-sm text-muted-foreground">
              <Stat n="29+" label="Curated Ideas" />
              <Stat n="12" label="Sectors" />
              <Stat n="80+" label="Skill paths" />
            </div>
          </div>

          <div className="lg:col-span-5 relative">
            <div className="absolute -inset-4 bg-gradient-to-br from-primary/10 via-accent/10 to-transparent rounded-[2.5rem] blur-2xl" />
            <div className="relative rounded-[2rem] overflow-hidden border border-border shadow-xl">
              <img
                src="https://static.prod-images.emergentagent.com/jobs/9893adf9-2474-40a4-9829-2cf309a21e6b/images/97ccd4e04344bcea64797549356f4a7bba62f42b67506e2d58e77cb4864e7134.png"
                alt="Builders of Bharat collaborating"
                className="w-full h-[380px] md:h-[460px] object-cover"
              />
              <div className="absolute bottom-4 left-4 right-4 bg-background/85 backdrop-blur-md border border-border rounded-2xl p-4 flex items-center gap-3">
                <span className="h-10 w-10 rounded-xl bg-primary text-white inline-flex items-center justify-center"><Lightbulb className="h-5 w-5" /></span>
                <div className="text-sm">
                  <div className="font-bold">Soil Testing Micro Lab</div>
                  <div className="text-muted-foreground">₹1.5L+ · 2-4 people · Agrarian districts</div>
                </div>
                <Link to="/ideas/soil-testing-micro-lab" className="ml-auto h-9 w-9 rounded-full bg-primary text-white inline-flex items-center justify-center hover:bg-[color:hsl(var(--primary))] hover:scale-105 transition-transform" data-testid="hero-floating-card-cta">
                  <ArrowUpRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Value Prop */}
      <section className="vw-container py-12 md:py-20">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <ValueCard icon={Compass} title="Discover" body="Browse 29+ practical, Bharat-grounded ideas across local, hybrid, digital and future sectors." />
          <ValueCard icon={Users} title="Team up" body="Find collaborators with the right skills, capital and district context to build with you." />
          <ValueCard icon={Handshake} title="Get backed" body="See eligible government schemes, investment tiers, and licensing for each idea." />
        </div>
      </section>

      {/* Featured Ideas */}
      <section className="vw-container py-8 md:py-16">
        <div className="flex items-end justify-between mb-8 gap-4">
          <div>
            <div className="vw-section-label mb-2">From the Idea Library</div>
            <h2 className="text-2xl md:text-4xl font-bold tracking-tight" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              Hand-picked, builder-ready
            </h2>
          </div>
          <Link to="/ideas" className="vw-btn-ghost text-sm" data-testid="landing-see-all-ideas-cta">
            See all <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        {featured.length === 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[0, 1, 2].map((i) => (
              <div key={i} className="vw-card p-7 h-64 animate-pulse bg-muted/40" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featured.map((idea) => <IdeaCard key={idea.slug} idea={idea} />)}
          </div>
        )}
      </section>

      {/* Big CTA strip */}
      <section className="vw-container py-12 md:py-20">
        <div className="relative overflow-hidden rounded-3xl bg-foreground text-background p-8 md:p-14">
          <div className="absolute inset-0 opacity-30" style={{
            backgroundImage: "radial-gradient(circle at 80% 20%, rgba(232,93,4,0.6), transparent 50%), radial-gradient(circle at 10% 80%, rgba(244,162,97,0.4), transparent 60%)"
          }} />
          <div className="relative grid grid-cols-1 md:grid-cols-3 items-center gap-6">
            <div className="md:col-span-2">
              <div className="vw-section-label !text-accent mb-2">Ready to build?</div>
              <h2 className="text-2xl md:text-4xl font-bold tracking-tight" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                Pick an idea. Find your team. Make it real.
              </h2>
              <p className="text-background/70 mt-2 max-w-xl">
                Every idea includes execution type, capital tiers, team roles, eligible schemes and ideal district fit — so you can actually start small and grow.
              </p>
            </div>
            <Link to="/ideas" className="vw-btn-primary md:justify-self-end" data-testid="cta-strip-explore-ideas">
              Browse the Library <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

function Stat({ n, label }) {
  return (
    <div className="flex flex-col">
      <span className="font-extrabold text-foreground text-xl">{n}</span>
      <span className="text-xs uppercase tracking-wider">{label}</span>
    </div>
  );
}

function ValueCard({ icon: Icon, title, body }) {
  return (
    <div className="vw-card p-7">
      <span className="h-11 w-11 rounded-2xl bg-secondary text-primary inline-flex items-center justify-center mb-4">
        <Icon className="h-5 w-5" />
      </span>
      <h3 className="text-lg font-bold mb-1.5" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{title}</h3>
      <p className="text-sm text-muted-foreground leading-relaxed">{body}</p>
    </div>
  );
}
