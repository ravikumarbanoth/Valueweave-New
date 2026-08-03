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
"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import LiveSearch from "@/components/search/LiveSearch";
import { AUDIENCES, HOME_PROMPTS } from "@/lib/audiences";

export default function HomeHeroSearch({ heading, subheading }) {
  const router = useRouter();

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
          label="What opportunity are you looking for today?"
          labelClassName="block font-display font-bold text-[15px] text-ink mb-3 text-center"
          placeholder="Electrician, PMEGP, Medak…"
        />
      </div>

      {/* An empty box is a wall. These are the words people actually arrive
          with, and every one of them returns something from the graph. */}
      <div className="flex flex-wrap justify-center gap-2 mt-5" data-testid="home-search-prompts">
        <span className="text-xs text-stone-400 self-center mr-1">Try:</span>
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

      <div className="mt-10">
        <p className="text-sm font-display font-bold text-ink mb-3">
          Or tell us who you are
        </p>
        <div className="flex flex-wrap justify-center gap-2.5" data-testid="home-audiences">
          {AUDIENCES.map((audience) => (
            <Link
              key={audience.slug}
              href={`/start/${audience.slug}`}
              data-testid="home-audience"
              className="inline-flex items-center gap-2 rounded-full bg-white border-2 border-stone-200
                         px-4 py-2.5 font-display font-semibold text-sm text-ink
                         hover:border-teal-500 hover:bg-teal-50 transition-colors min-h-[44px]"
            >
              <span aria-hidden="true">{audience.emoji}</span>
              {audience.label}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
