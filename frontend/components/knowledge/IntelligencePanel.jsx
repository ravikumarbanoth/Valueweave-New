// Phase 3 — the intelligence block on a profile page.
//
// Renders the five business scores plus the skill profile and learning roadmap.
// Owner-only by construction: RLS on user_intelligence.* is `auth.uid() = user_id`
// with no admin exception, so a visitor to someone else's /profile/[id] reads
// nothing and this panel renders its not-available state. The `isMe` prop controls
// the wording, not the authorisation.
"use client";

import ScoreCard from "./ScoreCard";
import SkillGapPanel from "./SkillGapPanel";
import UnverifiedNotice from "./UnverifiedNotice";
import { SCORE_LABELS, STATUS } from "@/lib/intelligence";

const BUSINESS_SCORES = [
  "startup_readiness",
  "business_readiness",
  "funding_readiness",
  "ai_readiness",
  "district_opportunity",
];

export default function IntelligencePanel({ skill, business, learning, state, isMe = false }) {
  if (!state?.available) {
    return (
      <section data-testid="intelligence-panel-unavailable" className="card-base p-5 mb-6">
        <h2 className="font-display font-extrabold text-xl text-ink mb-2">
          Knowledge graph profile
        </h2>
        <p className="text-sm text-muted leading-relaxed">
          {isMe
            ? state?.message ||
              "We have not analysed your profile yet. Add skills and a district to get started."
            : "This is only visible to the person who owns the profile."}
        </p>
      </section>
    );
  }

  const resolved = skill?.resolved_skills || [];
  const unresolved = skill?.unresolved_skills || [];
  const roadmap = learning?.roadmap || [];

  return (
    <section data-testid="intelligence-panel" className="mb-6">
      <div className="flex items-baseline justify-between gap-3 mb-3">
        <h2 className="font-display font-extrabold text-xl text-ink">
          Knowledge graph profile
        </h2>
        <span className="text-xs text-stone-400">rule-based · no AI</span>
      </div>

      <UnverifiedNotice hasUnverified className="mb-4" />

      {/* ── Business, funding, AI and startup readiness ── */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-5">
        {BUSINESS_SCORES.map((key) => {
          const s = business?.[key] || {};
          return (
            <ScoreCard
              key={key}
              testId={`score-${key}`}
              label={SCORE_LABELS[key] || key}
              score={s.score}
              status={s.status}
              confidence={s.confidence}
              reason={s.reason}
            />
          );
        })}
        <ScoreCard
          testId="score-skill_profile"
          label={SCORE_LABELS.skill_profile}
          score={skill?.score}
          status={skill?.status}
          confidence={skill?.confidence}
          reason={skill?.reason}
          detail={
            skill?.resolve_rate_pct !== null && skill?.resolve_rate_pct !== undefined ? (
              <p className="text-[10px] text-stone-400 mt-2 tabular-nums">
                {skill.resolved_skill_count}/{skill.claimed_skill_count} skills matched
                to researched data ({skill.resolve_rate_pct}%)
              </p>
            ) : null
          }
        />
      </div>

      {/* ── Skill profile: matched, and honestly, unmatched ── */}
      <div className="mb-5">
        <SkillGapPanel
          testId="skill-profile-panel"
          title="Skill profile"
          have={resolved.map((r) => r.canonical_name)}
          need={roadmap.map((r) => r.skill)}
          noData={unresolved.map((u) => u.term)}
        />
      </div>

      {/* ── Learning roadmap ── */}
      <section data-testid="learning-roadmap" className="card-base p-5">
        <div className="flex items-baseline justify-between gap-3 mb-3">
          <h3 className="font-display font-extrabold text-base text-ink">Learning roadmap</h3>
          {learning?.status === STATUS.APPLIED && roadmap.length === 0 && (
            <span className="chip bg-teal-50 text-teal-700 border border-teal-200 text-[10px]">
              nothing outstanding
            </span>
          )}
        </div>

        {roadmap.length === 0 ? (
          <p className="text-xs text-muted leading-relaxed">
            {learning?.reason ||
              "No roadmap yet — this needs at least one skill that matches a researched business."}
          </p>
        ) : (
          <ol className="space-y-2.5">
            {roadmap.slice(0, 8).map((step) => (
              <li
                key={step.entity_id}
                className="flex items-start gap-3 rounded-2xl bg-stone-50 border border-stone-150 p-3"
              >
                <span className="shrink-0 w-6 h-6 rounded-full bg-ink text-white flex items-center justify-center text-[11px] font-bold tabular-nums">
                  {step.step}
                </span>
                <div className="min-w-0">
                  <p className="font-display font-bold text-sm text-ink">{step.skill}</p>
                  <p className="text-xs text-muted mt-0.5">
                    unlocks {step.unlocks_businesses} matched business
                    {step.unlocks_businesses === 1 ? "" : "es"}
                    {step.nsqf_level ? ` · NSQF ${step.nsqf_level}` : ""}
                    {step.learning_duration ? ` · ${step.learning_duration}` : ""}
                  </p>
                  {/* TRAINED_BY has 3 edges in the whole graph, so this is usually
                      absent. Saying so beats an empty row. */}
                  {step.providers?.length > 0 ? (
                    <p className="text-[10px] text-teal-700 mt-1">
                      training: {step.providers.slice(0, 2).join(", ")}
                    </p>
                  ) : (
                    <p className="text-[10px] text-stone-400 mt-1">
                      no linked training provider recorded yet
                    </p>
                  )}
                </div>
              </li>
            ))}
          </ol>
        )}
      </section>
    </section>
  );
}
