// The first thing on the page: a question, a box, and six ways in.
//
// WHAT THIS REPLACED
// ------------------
// The hero was a marketing column and a decorative animation. Three buttons —
// "Discover Yourself", "Explore Ideas", "Find Collaborators" — then a floating
// arrangement of emoji cards labelled "AI · Hyderabad", "Agri · Warangal".
//
// The search box existed. It was in section five, roughly two thousand pixels
// down on a phone, inside the feature grid. So the platform's single most useful
// control was below eight screens of pitch, and a visitor who knew exactly what
// they wanted — "PMEGP", "electrician", "Medak" — had no way to say so.
//
// THE BOX IS NOW LIVE, AND THE OBJECTION THAT KEPT IT STATIC IS GONE
// -------------------------------------------------------------------
// This was a plain form, deliberately: the old live component fetched the
// whole 647-row index into the browser on the first keystroke, which is a cost
// to put on every landing-page visitor including the ones who scroll straight
// past, and it rendered an empty state at the top of the homepage whenever the
// projection was unreachable.
//
// LiveSearch has neither problem. The index stays on the server and the wire
// carries two characters out and eight rows back — under 2 KB — and when the
// route fails it returns an empty list, so the box degrades to exactly the
// form this used to be. The submit button still navigates to /knowledge?q=…,
// so the URL is still shareable and the results page is still the place
// results are shown.
//
// Which matters here more than anywhere: this is the first control a first-time
// visitor sees, and "type three letters and watch the platform answer" teaches
// what ValueWeave is faster than any paragraph above it can.
//
// THE SIX CHIPS ARE THE POINT
// ---------------------------
// A search box only helps someone who already knows the word. The row beneath is
// for everyone else: pick who you are, and the next page starts from that rather
// than from our module names.
//
// PHASE 9 — THE ANSWER IS NOW REMEMBERED
// --------------------------------------
// The six chips below were worth one page view each. A visitor picked
// "Student", read the student page, went to a skill, came back, and was asked
// who they were all over again — by a platform whose whole promise is that it
// knows them.
//
// A returning visitor now sees their own answer at the top instead of the
// question, with a one-tap way out. The question is not deleted, it is
// demoted: "Not you?" opens the same six, and choosing again overwrites.
//
// WHY THE SWAP HAPPENS AFTER PAINT
// --------------------------------
// `recall()` reads localStorage, which the server cannot see. Reading it
// during render would make the server HTML and the first client render
// disagree, and React would throw a hydration error on the most important
// page on the site. So the first paint is always the anonymous one — six
// chips, exactly as before — and the greeting replaces it in an effect. A
// first-time visitor never sees a flicker because there is nothing to swap in.
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import LiveSearch from "@/components/search/LiveSearch";
import { AUDIENCES, AUDIENCE_BY_SLUG, GOALS, HOME_PROMPTS } from "@/lib/audiences";
import { recall, remember, forget } from "@/lib/journey";
import { useLanguage } from "@/lib/language";

export default function HomeHeroSearch({ heading, subheading }) {
  const router = useRouter();
  const [known, setKnown] = useState(null);
  //: "Change" reopens the six without forgetting first, so a visitor who
  //: opens it and changes their mind still has the answer they gave.
  const [choosing, setChoosing] = useState(false);
  const { t } = useLanguage();

  useEffect(() => {
    setKnown(recall());
  }, []);

  const audience = known ? AUDIENCE_BY_SLUG[known] : null;

  const go = (term) => {
    const q = String(term || "").trim();
    router.push(q ? `/knowledge?q=${encodeURIComponent(q)}` : "/knowledge");
  };

  return (
    <div className="max-w-3xl mx-auto text-center" data-testid="home-hero-search">
      <div className="inline-flex items-center gap-2 bg-amber-200 rounded-full px-4 py-1.5 mb-6">
        <span className="w-2 h-2 rounded-full bg-amber-500 ring-4 ring-amber-500/20" />
        <span className="text-xs font-display font-semibold text-amber-700">
          Now Open · Bharat Edition
        </span>
      </div>

      {/* The heading stays whatever an admin has set — it is a CMS field and
          taking that away would be a different kind of change. The question the
          brief asks for is the visible label on the box below, which is where a
          question belongs: immediately above the thing that answers it. */}
      <h1 className="h-hero mb-5" data-speakable>{heading}</h1>
      <p className="text-base sm:text-lg text-muted leading-relaxed mb-8 max-w-xl mx-auto" data-speakable>
        {subheading}
      </p>

      <div className="max-w-2xl mx-auto text-left">
        {/* The question is a visible label, not a placeholder. It is the one
            sentence the brief asks the page to open with, and a placeholder
            cannot carry it — a placeholder disappears the moment anyone
            types. Centred, because everything else in the hero is. */}
        <LiveSearch
          testId="home-search"
          size="hero"
          label={t("search.hero_label", "What opportunity are you looking for today?")}
          labelClassName="block font-display font-bold text-[15px] text-ink mb-3 text-center"
          placeholder={t("search.placeholder", "What do you want to learn, build or earn?")}
        />
      </div>

      {/* An empty box is a wall. These are the words people actually arrive
          with, and every one of them returns something from the graph. */}
      <div className="flex flex-wrap justify-center gap-2 mt-5" data-testid="home-search-prompts">
        <span className="text-xs text-stone-400 self-center mr-1">{t("search.try")}</span>
        {HOME_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => go(prompt)}
            data-testid="home-search-prompt"
            className="chip bg-white text-stone-600 border border-stone-200 hover:border-amber-300 hover:bg-amber-50 transition-colors"
          >
            {prompt}
          </button>
        ))}
      </div>

      {audience && !choosing ? (
        <div className="mt-10" data-testid="home-welcome-back">
          <p className="font-display font-bold text-base text-ink mb-1">
            Welcome back 👋
          </p>
          {/* Transparency in the same breath as the greeting. A reader should
              never have to wonder why one row is above another, and "we nudge
              these up" is the whole truth about what the memory does — it
              cannot hide anything, and saying so is cheaper than being asked. */}
          <p className="text-sm text-muted mb-4">
            You were here as a{" "}
            <span className="font-semibold text-ink">{audience.label.toLowerCase()}</span>,
            so we nudge {audience.label.toLowerCase()} results up. Nothing is hidden.
          </p>
          <Link
            href={`/start/${audience.slug}`}
            data-testid="home-continue-as"
            className="inline-flex items-center gap-2 rounded-full bg-teal-500 text-white
                       px-6 py-3 font-display font-bold text-sm
                       hover:bg-teal-600 transition-colors min-h-[44px]"
          >
            <span aria-hidden="true">{audience.emoji}</span>
            Pick up where you left off →
          </Link>
          {/* Two separate controls, because they are two different intentions.
              "Change" is for somebody who is now a business owner; "Forget" is
              for somebody who wants us to stop knowing. Offering only the
              first would make the memory impossible to leave. */}
          <div className="mt-4 flex items-center justify-center gap-4">
            <button
              type="button"
              data-testid="home-change-audience"
              onClick={() => setChoosing(true)}
              className="text-xs font-semibold text-teal-700 underline hover:text-ink"
            >
              Change
            </button>
            <button
              type="button"
              data-testid="home-not-you"
              onClick={() => { forget(); setKnown(null); setChoosing(false); }}
              className="text-xs text-stone-400 underline hover:text-ink"
            >
              Forget me
            </button>
          </div>
        </div>
      ) : (
        <div className="mt-10">
          <p className="text-sm font-display font-bold text-ink mb-3">
            {choosing ? t("home.who_are_you", "Who are you now?") : t("home.tell_us_who", "Or tell us who you are")}
          </p>
          <div className="flex flex-wrap justify-center gap-2.5" data-testid="home-audiences">
            {AUDIENCES.map((option) => (
              <Link
                key={option.slug}
                href={`/start/${option.slug}`}
                data-testid="home-audience"
                onClick={() => remember(option.slug)}
                className="inline-flex items-center gap-2 rounded-full bg-white border-2 border-stone-200
                           px-4 py-2.5 font-display font-semibold text-sm text-ink
                           hover:border-teal-500 hover:bg-teal-50 transition-colors min-h-[44px]"
              >
                <span aria-hidden="true">{option.emoji}</span>
                {option.label}
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* POPULAR GOALS — the shortcut for people who already know what they
          came for. Shown to everyone, remembered visitor or not, because
          knowing somebody is a farmer does not mean they are not here to look
          up a scheme today. Tapping one does NOT set an audience: it is a
          destination, not a claim about who you are. */}
      <div className="mt-10">
        <p className="text-sm font-display font-bold text-ink mb-3">
          {t("home.popular_goals", "Popular goals")}
        </p>
        <div className="flex flex-wrap justify-center gap-2" data-testid="home-goals">
          {GOALS.map((goal) => (
            <Link
              key={goal.label}
              href={goal.href}
              data-testid="home-goal"
              title={goal.hint}
              className="inline-flex items-center gap-1.5 rounded-full bg-white border border-stone-200
                         px-3.5 py-2 font-display font-medium text-[13px] text-stone-700
                         hover:border-amber-400 hover:bg-amber-50 transition-colors min-h-[44px]"
            >
              <span aria-hidden="true">{goal.emoji}</span>
              {goal.label}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
