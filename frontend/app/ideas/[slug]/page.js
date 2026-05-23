"use client";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getIdea, getSector, getBucket, formatINR } from "@/lib/idea-library";
import AppNavbar from "@/components/AppNavbar";
import ShareButton from "@/components/ShareButton";
import { MapPin, Users, Target, Wrench, IndianRupee, TrendingUp, Sparkles } from "lucide-react";

const BUCKET_COLOR = {
  "local-physical": "bg-amber-100 text-amber-800",
  "hybrid":         "bg-teal-100 text-teal-800",
  "digital":        "bg-blue-100 text-blue-800",
  "future":         "bg-violet-100 text-violet-800",
};

// Map an idea's sector to an opportunity category (for prefill).
const SECTOR_TO_OPP_CATEGORY = {
  "agriculture": "agri",
  "agritech": "agri",
  "local-services": "local-business",
  "repair-economy": "trades",
  "women-led": "local-business",
  "food-business": "local-business",
  "manufacturing": "local-business",
  "education": "student",
  "logistics": "local-business",
  "digital-services": "digital",
  "creator-economy": "digital",
  "ev-energy": "ev-electronics",
  "drone-tech": "drone",
  "climate-tech": "agri",
};

export default function IdeaDetailPage() {
  const { slug } = useParams();
  const idea = getIdea(slug);

  if (!idea) {
    return (
      <Shell>
        <div className="card-base p-10 text-center" data-testid="idea-not-found">
          <div className="text-5xl mb-3">🔍</div>
          <h2 className="font-display font-bold text-xl mb-2">Idea not found</h2>
          <Link href="/ideas" className="btn-primary">Back to ideas</Link>
        </div>
      </Shell>
    );
  }

  const sector = getSector(idea.sector);
  const bucket = getBucket(idea.bucket);
  const postHref = `/opportunities/new?title=${encodeURIComponent("Looking for collaborators — " + idea.title)}&category=${SECTOR_TO_OPP_CATEGORY[idea.sector] || "local-business"}&skills=${encodeURIComponent(idea.skills_needed.join(", "))}`;

  return (
    <Shell>
      <div className="flex items-center justify-between flex-wrap gap-3 mb-4">
        <Link href="/ideas" className="text-sm font-display font-semibold text-muted hover:text-ink">← Back to ideas</Link>
        <ShareButton url={`/ideas/${idea.slug}`} title={`${idea.title} — ValueWeave Idea Library`} />
      </div>

      <article className="card-base p-6 md:p-8">
        <div className="flex items-start gap-4 mb-5">
          <div className="text-5xl shrink-0">{idea.emoji}</div>
          <div className="flex-1">
            <div className="flex flex-wrap gap-2 mb-2">
              <span className={`chip ${BUCKET_COLOR[idea.bucket]}`}>{bucket.emoji} {bucket.label}</span>
              <span className="chip bg-amber-50 text-amber-700">{sector.emoji} {sector.label}</span>
              {idea.beginner_friendly && <span className="chip bg-teal-50 text-teal-700">Beginner friendly</span>}
              {idea.remote_possible && <span className="chip bg-blue-50 text-blue-700">Remote possible</span>}
            </div>
            <h1 data-testid="idea-title" className="font-display font-extrabold text-2xl sm:text-3xl tracking-tight leading-tight">{idea.title}</h1>
          </div>
        </div>

        <p className="text-base text-ink leading-relaxed mb-6">{idea.short_description}</p>

        <Section icon={Target} label="Problem this solves">
          <p className="text-ink leading-relaxed">{idea.problem_solved}</p>
        </Section>

        <Section icon={Users} label="Who is this ideal for?">
          <div className="flex flex-wrap gap-1.5">
            {idea.ideal_for.map((p) => (
              <span key={p} data-testid={`idea-ideal-${p}`} className="chip bg-emerald-50 text-emerald-700">{p}</span>
            ))}
          </div>
        </Section>

        <Section icon={IndianRupee} label="Investment & revenue">
          <div className="grid grid-cols-3 gap-2 mb-3">
            <Stat label="Minimum" value={formatINR(idea.investment_min)} />
            <Stat label="Medium" value={formatINR(idea.investment_med)} />
            <Stat label="Advanced" value={formatINR(idea.investment_adv)} />
          </div>
          <div className="bg-amber-50 rounded-xl px-4 py-3 text-sm">
            <span className="font-display font-bold text-amber-700">Monthly revenue range: </span>
            <span className="text-ink">{formatINR(idea.monthly_revenue_min)} – {formatINR(idea.monthly_revenue_max)}</span>
            <span className="text-stone-500 text-xs ml-2">(estimate, varies by execution)</span>
          </div>
        </Section>

        <Section icon={Wrench} label="Skills you'll need">
          <div className="flex flex-wrap gap-1.5">
            {idea.skills_needed.map((s) => <span key={s} className="chip bg-stone-100 text-stone-700">{s}</span>)}
          </div>
        </Section>

        <Section icon={Users} label="Team roles to fill">
          <div className="flex flex-wrap gap-1.5">
            {idea.team_roles.map((r) => <span key={r} className="chip bg-teal-50 text-teal-700">{r}</span>)}
          </div>
        </Section>

        <Section icon={MapPin} label="Where this works well">
          <div className="flex flex-wrap gap-1.5">
            {idea.district_fit.map((d) => <span key={d} className="chip bg-violet-50 text-violet-700">{d}</span>)}
          </div>
        </Section>

        {idea.tags.length > 0 && (
          <Section icon={TrendingUp} label="Tags">
            <div className="flex flex-wrap gap-1.5">
              {idea.tags.map((t) => <span key={t} className="chip bg-stone-50 text-stone-600 border border-stone-200">{t}</span>)}
            </div>
          </Section>
        )}

        <div className="mt-8 bg-gradient-to-r from-amber-50 to-teal-50 border border-amber-200 rounded-2xl p-5 sm:p-6 text-center">
          <Sparkles className="inline-block text-amber-600 mb-2" size={22} />
          <h3 className="font-display font-bold text-lg mb-1">Ready to start this in your district?</h3>
          <p className="text-sm text-muted mb-4 max-w-md mx-auto">Post it as an opportunity. We'll prefill the form with skills + category so you can publish in 30 seconds.</p>
          <Link href={postHref} data-testid="idea-start-cta" className="btn-primary">Start this in your district →</Link>
        </div>
      </article>
    </Shell>
  );
}

function Section({ icon: Icon, label, children }) {
  return (
    <section className="mb-6">
      <h3 className="font-display font-bold text-xs uppercase tracking-wider text-stone-600 mb-2 flex items-center gap-1.5">
        <Icon size={14} /> {label}
      </h3>
      {children}
    </section>
  );
}

function Stat({ label, value }) {
  return (
    <div className="bg-white border border-stone-200 rounded-xl px-3 py-3 text-center">
      <div className="text-[10px] uppercase tracking-wider text-stone-500 font-semibold">{label}</div>
      <div className="font-display font-extrabold text-base sm:text-lg text-ink">{value}</div>
    </div>
  );
}

function Shell({ children }) {
  return (
    <div className="min-h-screen bg-cream pb-24 md:pb-12 font-body">
      <AppNavbar />
      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-6 sm:py-8">{children}</main>
    </div>
  );
}
