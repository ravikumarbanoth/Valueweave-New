import React from "react";
import { Link } from "react-router-dom";
import { ArrowUpRight, Sparkles, Users, MapPin, Wallet, TrendingUp } from "lucide-react";
import { formatINR } from "@/lib/api";

export default function IdeaCard({ idea }) {
  return (
    <Link
      to={`/ideas/${idea.slug}`}
      data-testid={`idea-card-${idea.slug}`}
      className="vw-card p-6 md:p-7 flex flex-col gap-4 group relative overflow-hidden"
    >
      {idea.featured && (
        <span className="absolute top-4 right-4 vw-chip bg-primary/10 text-primary">
          <Sparkles className="h-3 w-3" /> Featured
        </span>
      )}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="vw-chip">{idea.sector}</span>
        <span className="vw-chip-muted">{idea.execution_type}</span>
        {idea.beginner_friendly && (
          <span className="vw-chip-muted bg-success/10 text-emerald-700">Beginner-friendly</span>
        )}
      </div>

      <div className="space-y-2">
        <h3 className="text-xl font-bold leading-tight tracking-tight text-foreground group-hover:text-primary transition-colors">
          {idea.title}
        </h3>
        <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed">
          {idea.short_description}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3 mt-auto pt-2 text-xs">
        <div className="flex items-center gap-1.5 text-foreground/80">
          <Wallet className="h-4 w-4 text-primary" />
          <span className="font-semibold">{formatINR(idea.minimum_investment)}+</span>
        </div>
        <div className="flex items-center gap-1.5 text-foreground/80">
          <Users className="h-4 w-4 text-primary" />
          <span>{idea.ideal_team_size_min}-{idea.ideal_team_size_max} people</span>
        </div>
        <div className="flex items-center gap-1.5 text-foreground/80">
          <MapPin className="h-4 w-4 text-primary" />
          <span className="truncate">{idea.suitable_district_types?.slice(0, 2).join(", ")}</span>
        </div>
        <div className="flex items-center gap-1.5 text-foreground/80">
          <TrendingUp className="h-4 w-4 text-primary" />
          <span>{idea.growth_trend}</span>
        </div>
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-border/70 mt-2">
        <span className="text-xs text-muted-foreground">
          {idea.save_count.toLocaleString("en-IN")} saves · {idea.team_interest_count} teams interested
        </span>
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-secondary text-primary group-hover:bg-primary group-hover:text-white transition-all">
          <ArrowUpRight className="h-4 w-4" />
        </span>
      </div>
    </Link>
  );
}
