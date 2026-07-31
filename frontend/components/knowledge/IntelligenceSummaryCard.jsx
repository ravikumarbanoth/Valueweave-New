"use client";
// The dashboard's User Intelligence summary (Step 3, Priority 1).
//
// Eight scores in one card, each linking to the full explanation on /profile.
// A score is shown as "—" rather than 0 when the engine could not compute it:
// telling a user their funding readiness is zero when the truth is that we have no
// data to assess it is the single easiest way for this platform to mislead.
import Link from "next/link";
import { SCORE_LABELS, scoreLabel, scoreTone } from "@/lib/intelligence";

const ORDER = [
  "startup_readiness",
  "skill_profile",
  "business_readiness",
  "district_opportunity",
  "learning_roadmap",
  "funding_readiness",
  "collaboration_score",
  "ai_readiness",
];

export default function IntelligenceSummaryCard({ summary }) {
  const scores = summary?.scores || {};
  const present = ORDER.filter((k) => k in scores);
  if (present.length === 0) return null;

  const headline = scores.startup_readiness;

  return (
    <section data-testid="intelligence-summary-card" className="card-base p-5 mb-6">
      <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
        <div>
          <h2 className="font-display font-bold text-ink">Your intelligence summary</h2>
          <p className="text-xs text-muted mt-0.5">
            Worked out by matching your profile against what we have researched. Every score is
            explainable.
          </p>
        </div>
        {headline && (
          <div className="text-right">
            <p className={`font-display font-extrabold text-3xl ${scoreTone(headline.score, headline.status)}`}>
              {scoreLabel(headline.score, headline.status)}
            </p>
            <p className="text-[10px] uppercase tracking-widest text-muted">Startup readiness</p>
          </div>
        )}
      </div>

      <dl className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {present
          .filter((k) => k !== "startup_readiness")
          .map((key) => {
            const s = scores[key];
            return (
              <div key={key} data-testid={`summary-score-${key}`} className="min-w-0">
                <dt className="text-[10px] uppercase tracking-widest text-muted truncate">
                  {SCORE_LABELS[key] || key}
                </dt>
                <dd className={`font-display font-bold text-lg ${scoreTone(s.score, s.status)}`}>
                  {scoreLabel(s.score, s.status)}
                </dd>
              </div>
            );
          })}
      </dl>

      <Link href="/profile" data-testid="summary-explain-link"
            className="text-[12px] text-muted underline hover:text-ink mt-4 inline-block">
        See why each score is what it is →
      </Link>
    </section>
  );
}
