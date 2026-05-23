import React from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Wallet, Users, TrendingUp, Sparkles, Bookmark, BookmarkCheck, MapPin, Shield, Briefcase, GraduationCap, Building2, Heart } from "lucide-react";
import { fetchIdea, fetchRelatedIdeas, formatINR, toggleSaveIdea } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import IdeaCard from "@/components/IdeaCard";
import { toast } from "sonner";

export default function IdeaDetail() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [idea, setIdea] = React.useState(null);
  const [related, setRelated] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [saved, setSaved] = React.useState(false);
  const [notFound, setNotFound] = React.useState(false);

  React.useEffect(() => {
    setLoading(true);
    setNotFound(false);
    fetchIdea(slug)
      .then((d) => { setIdea(d); setLoading(false); })
      .catch(() => { setNotFound(true); setLoading(false); });
    fetchRelatedIdeas(slug).then(setRelated).catch(() => {});
    window.scrollTo({ top: 0, behavior: "instant" });
  }, [slug]);

  const handleSave = async () => {
    if (!user) {
      toast.info("Sign in to save this idea", {
        action: { label: "Sign in", onClick: () => navigate(`/login?next=/ideas/${slug}`) },
      });
      return;
    }
    try {
      const res = await toggleSaveIdea(slug);
      setSaved(res.saved);
      toast.success(res.saved ? "Idea saved" : "Idea removed from saves");
    } catch (e) {
      toast.error("Could not save right now");
    }
  };

  const handleJoin = () => {
    if (!user) {
      navigate(`/login?next=/ideas/${slug}`);
    } else {
      toast.success("Coming soon: team-up flow", { description: "We'll connect you with collaborators in your district." });
    }
  };

  if (loading) {
    return <div className="vw-container py-16"><div className="h-72 w-full rounded-3xl bg-muted/40 animate-pulse" /></div>;
  }
  if (notFound) {
    return (
      <div className="vw-container py-24 text-center" data-testid="idea-not-found">
        <h1 className="text-3xl font-bold mb-3">Idea not found</h1>
        <p className="text-muted-foreground mb-6">It may have been removed or the link is wrong.</p>
        <Link to="/ideas" className="vw-btn-primary"><ArrowLeft className="h-4 w-4" /> Back to Idea Library</Link>
      </div>
    );
  }

  return (
    <div data-testid={`idea-detail-${idea.slug}`} className="vw-container py-8 md:py-12">
      <Link to="/ideas" className="inline-flex items-center gap-2 text-sm font-semibold text-muted-foreground hover:text-primary mb-6" data-testid="idea-detail-back">
        <ArrowLeft className="h-4 w-4" /> Back to Idea Library
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12">
        {/* Main */}
        <div className="lg:col-span-8 space-y-8">
          <header className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <span className="vw-chip">{idea.sector}</span>
              <span className="vw-chip-muted">{idea.execution_type}</span>
              {idea.featured && (
                <span className="vw-chip bg-primary/10 text-primary"><Sparkles className="h-3 w-3" /> Featured</span>
              )}
              {idea.beginner_friendly && (
                <span className="vw-chip-muted bg-emerald-50 text-emerald-700">Beginner-friendly</span>
              )}
            </div>
            <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight leading-tight" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              {idea.title}
            </h1>
            <p className="text-lg text-muted-foreground leading-relaxed max-w-2xl">{idea.short_description}</p>
          </header>

          <Section title="The opportunity" body={idea.detailed_description} />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <InfoBlock icon={Shield} title="Problem solved" body={idea.problem_solved} />
            <InfoBlock icon={Heart} title="Target customers" body={idea.target_customers} />
          </div>

          <ListSection icon={Briefcase} title="Team roles needed" items={idea.team_roles_needed} />
          <ListSection icon={GraduationCap} title="Skills required" items={idea.skills_required} />
          <ListSection icon={Sparkles} title="Ideal for" items={idea.ideal_for} accent />
          <ListSection icon={MapPin} title="Suitable district types" items={idea.suitable_district_types} />
          <ListSection icon={Building2} title="Eligible government schemes" items={idea.eligible_government_schemes} />

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-2">
            <Metric label="Risk" value={idea.risk_level} />
            <Metric label="Scalability" value={idea.scalability_level} />
            <Metric label="Competition" value={idea.competition_level} />
            <Metric label="Growth Trend" value={idea.growth_trend} />
            <Metric label="AI-Proof" value={idea.ai_proof_level} />
            <Metric label="Setup" value={idea.setup_difficulty} />
            <Metric label="Licensing" value={idea.licensing_complexity} />
            <Metric label="Remote possible" value={idea.remote_possible ? "Yes" : "No"} />
          </div>
        </div>

        {/* Sticky summary */}
        <aside className="lg:col-span-4">
          <div className="lg:sticky lg:top-24 space-y-4">
            <div className="vw-card p-6 md:p-7 space-y-5">
              <div>
                <div className="vw-section-label mb-1">Investment tiers</div>
                <div className="space-y-2">
                  <TierRow label="Minimum" value={formatINR(idea.minimum_investment)} />
                  <TierRow label="Medium scale" value={formatINR(idea.medium_scale_investment)} />
                  <TierRow label="Advanced scale" value={formatINR(idea.advanced_scale_investment)} />
                </div>
              </div>
              <div className="h-px bg-border" />
              <div>
                <div className="vw-section-label mb-1">Estimated monthly revenue</div>
                <div className="text-xl font-bold tracking-tight">
                  {formatINR(idea.estimated_monthly_revenue_min)} – {formatINR(idea.estimated_monthly_revenue_max)}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <Mini icon={Users} label={`${idea.ideal_team_size_min}-${idea.ideal_team_size_max} people`} />
                <Mini icon={TrendingUp} label={`${idea.trending_score} trending`} />
                <Mini icon={Wallet} label={`From ${formatINR(idea.minimum_investment)}`} />
                <Mini icon={Bookmark} label={`${idea.save_count.toLocaleString("en-IN")} saves`} />
              </div>

              <button onClick={handleJoin} className="vw-btn-primary w-full" data-testid="idea-detail-join-cta">
                Want to build this? Join ValueWeave
              </button>
              <button onClick={handleSave} className="vw-btn-outline w-full" data-testid="idea-detail-save-cta">
                {saved ? <><BookmarkCheck className="h-4 w-4" /> Saved</> : <><Bookmark className="h-4 w-4" /> Save this idea</>}
              </button>
              {!user && (
                <p className="text-xs text-muted-foreground text-center">
                  Sign in to save ideas, join teams and message collaborators.
                </p>
              )}
            </div>
          </div>
        </aside>
      </div>

      {/* Related */}
      {related.length > 0 && (
        <section className="mt-16 md:mt-24">
          <div className="flex items-end justify-between mb-6">
            <h2 className="text-2xl md:text-3xl font-bold tracking-tight" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              Related ideas
            </h2>
            <Link to="/ideas" className="vw-btn-ghost text-sm" data-testid="idea-detail-see-more">See all</Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {related.map((r) => <IdeaCard key={r.slug} idea={r} />)}
          </div>
        </section>
      )}
    </div>
  );
}

function Section({ title, body }) {
  return (
    <section>
      <div className="vw-section-label mb-2">{title}</div>
      <p className="text-base md:text-lg text-foreground/85 leading-relaxed">{body}</p>
    </section>
  );
}

function InfoBlock({ icon: Icon, title, body }) {
  return (
    <div className="vw-card p-5">
      <div className="flex items-center gap-2 mb-2">
        <Icon className="h-4 w-4 text-primary" />
        <h4 className="text-sm font-bold tracking-tight">{title}</h4>
      </div>
      <p className="text-sm text-muted-foreground leading-relaxed">{body}</p>
    </div>
  );
}

function ListSection({ icon: Icon, title, items, accent }) {
  if (!items?.length) return null;
  return (
    <section>
      <div className="flex items-center gap-2 mb-3">
        <Icon className="h-4 w-4 text-primary" />
        <h3 className="text-sm font-bold uppercase tracking-[0.15em] text-foreground">{title}</h3>
      </div>
      <div className="flex flex-wrap gap-2">
        {items.map((it) => (
          <span key={it} className={accent ? "vw-chip" : "vw-chip-muted"}>{it}</span>
        ))}
      </div>
    </section>
  );
}

function TierRow({ label, value }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="text-base font-bold tracking-tight">{value}</span>
    </div>
  );
}

function Mini({ icon: Icon, label }) {
  return (
    <div className="flex items-center gap-2 text-foreground/80">
      <Icon className="h-4 w-4 text-primary" />
      <span className="font-semibold">{label}</span>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-xl border border-border p-3 bg-card">
      <div className="text-[10px] uppercase tracking-wider text-muted-foreground font-bold">{label}</div>
      <div className="text-sm font-bold mt-0.5">{value}</div>
    </div>
  );
}
