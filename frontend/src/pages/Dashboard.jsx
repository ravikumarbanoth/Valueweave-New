import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, Lightbulb, Bookmark, Users, MessageCircle, Briefcase } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { fetchSavedIdeas } from "@/lib/api";
import IdeaCard from "@/components/IdeaCard";

export default function Dashboard() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  const [savedIdeas, setSavedIdeas] = React.useState([]);

  React.useEffect(() => {
    if (!loading && !user) {
      navigate("/login?next=/dashboard", { replace: true });
    }
  }, [user, loading, navigate]);

  React.useEffect(() => {
    if (user) fetchSavedIdeas().then(setSavedIdeas).catch(() => {});
  }, [user]);

  if (loading || !user) {
    return <div className="vw-container py-16"><div className="h-72 w-full rounded-3xl bg-muted/40 animate-pulse" /></div>;
  }

  return (
    <div data-testid="dashboard-page" className="vw-container py-8 md:py-12">
      <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
        <div>
          <div className="vw-section-label mb-2">Your space</div>
          <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
            Hi, {user.name?.split(" ")[0] || "builder"} 👋
          </h1>
          <p className="text-muted-foreground mt-1">Pick up where you left off, or discover something new to build.</p>
        </div>
      </div>

      {/* Quick access bento */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
        {/* Browse Ideas — prominent */}
        <Link
          to="/ideas"
          data-testid="dashboard-browse-ideas-card"
          className="md:col-span-2 group relative overflow-hidden rounded-3xl bg-primary text-primary-foreground p-7 md:p-10 hover:-translate-y-1 transition-transform shadow-[0_12px_40px_-12px_rgba(232,93,4,0.5)]"
        >
          <div className="absolute inset-0 opacity-30" style={{
            backgroundImage: "radial-gradient(circle at 90% 10%, rgba(255,255,255,0.4), transparent 50%)"
          }} />
          <div className="relative flex flex-col gap-4 max-w-md">
            <span className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-white/15 backdrop-blur-md">
              <Lightbulb className="h-6 w-6" />
            </span>
            <div>
              <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                Browse the Idea Library
              </h2>
              <p className="text-primary-foreground/85 mt-1">
                29+ Bharat-grounded ideas with team roles, investment tiers and district fit.
              </p>
            </div>
            <span className="inline-flex items-center gap-2 font-semibold">
              Open library <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </span>
          </div>
        </Link>

        <QuickCard icon={Bookmark} title="Saved Ideas" count={savedIdeas.length} to="#saved" testid="dashboard-saved-card" />
        <QuickCard icon={Users} title="My Teams" count={0} to="#" testid="dashboard-teams-card" comingSoon />
        <QuickCard icon={Briefcase} title="Opportunities" count={0} to="/opportunities" testid="dashboard-opportunities-card" comingSoon />
        <QuickCard icon={MessageCircle} title="Messages" count={0} to="#" testid="dashboard-messages-card" comingSoon />
      </div>

      {/* Saved ideas */}
      <section id="saved" className="space-y-6">
        <div className="flex items-end justify-between">
          <h2 className="text-xl md:text-2xl font-bold tracking-tight" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
            Saved ideas
          </h2>
          <Link to="/ideas" className="vw-btn-ghost text-sm" data-testid="dashboard-explore-more">Explore more <ArrowRight className="h-4 w-4" /></Link>
        </div>
        {savedIdeas.length === 0 ? (
          <div className="vw-card p-10 text-center">
            <Bookmark className="h-10 w-10 mx-auto text-primary mb-3" />
            <h3 className="text-lg font-bold mb-1">No saved ideas yet</h3>
            <p className="text-muted-foreground mb-4">Bookmark ideas from the library to revisit them here.</p>
            <Link to="/ideas" className="vw-btn-primary" data-testid="dashboard-empty-browse">Browse ideas</Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {savedIdeas.map((i) => <IdeaCard key={i.slug} idea={i} />)}
          </div>
        )}
      </section>
    </div>
  );
}

function QuickCard({ icon: Icon, title, count, to, testid, comingSoon }) {
  return (
    <Link to={to} data-testid={testid} className="vw-card p-6 flex flex-col gap-3 relative">
      <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-secondary text-primary">
        <Icon className="h-5 w-5" />
      </span>
      <div>
        <h3 className="font-bold tracking-tight" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{title}</h3>
        <p className="text-sm text-muted-foreground">{comingSoon ? "Coming soon" : `${count} items`}</p>
      </div>
    </Link>
  );
}
