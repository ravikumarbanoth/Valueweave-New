import React from "react";
import { Link } from "react-router-dom";
import { Briefcase, ArrowRight } from "lucide-react";

export default function Opportunities() {
  return (
    <div className="vw-container py-16 md:py-24" data-testid="opportunities-page">
      <div className="max-w-2xl mx-auto text-center">
        <span className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-secondary text-primary mb-5">
          <Briefcase className="h-6 w-6" />
        </span>
        <div className="vw-section-label mb-2">Opportunities</div>
        <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight leading-tight" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
          Collaborate, hire and co-build — coming soon.
        </h1>
        <p className="text-muted-foreground mt-3">
          Meanwhile, pick from <Link to="/ideas" className="text-primary font-semibold">29+ Bharat-grounded ideas</Link> and start assembling your team.
        </p>
        <Link to="/ideas" className="vw-btn-primary mt-6" data-testid="opportunities-explore-ideas">
          Browse the Idea Library <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  );
}
