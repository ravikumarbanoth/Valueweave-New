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
// WHY A FORM AND NOT THE LIVE SEARCH COMPONENT
// --------------------------------------------
// KnowledgeSearch queries as you type, which is right where it sits: inside a
// page you already chose to be on. In the hero it would be wrong twice. It
// fetches the whole 647-row index on first keystroke, which is a cost to put on
// every landing-page visitor including the ones who scroll straight past; and
// when the projection is unreachable it would render an empty state at the top
// of the homepage.
//
// A form navigates to /knowledge?q=… instead. No fetch until someone means it,
// the result lands on the page built to show results, and the URL is shareable.
//
// THE SIX CHIPS ARE THE POINT
// ---------------------------
// A search box only helps someone who already knows the word. The row beneath is
// for everyone else: pick who you are, and the next page starts from that rather
// than from our module names.
"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import Link from "next/link";
import { Search } from "lucide-react";
import { AUDIENCES, HOME_PROMPTS } from "@/lib/audiences";

export default function HomeHeroSearch({ heading, subheading }) {
  const router = useRouter();
  const [query, setQuery] = useState("");

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

      <form
        onSubmit={(event) => {
          event.preventDefault();
          go(query);
        }}
        role="search"
        className="max-w-2xl mx-auto"
      >
        {/* The question is visible, not just an accessible label. It is the one
            sentence the brief asks the page to open with, and a placeholder
            cannot carry it — a placeholder disappears the moment anyone types. */}
        <label
          htmlFor="home-search"
          className="block font-display font-bold text-[15px] text-ink mb-3"
        >
          What opportunity are you looking for today?
        </label>

        <div className="relative">
          <Search
            size={20}
            aria-hidden="true"
            className="absolute left-5 top-[1.4rem] sm:top-1/2 sm:-translate-y-1/2 text-stone-400 pointer-events-none"
          />
          <input
            id="home-search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            data-testid="home-search-input"
            placeholder="Electrician, PMEGP, Medak…"
            autoComplete="off"
            className="w-full rounded-full border-2 border-stone-200 bg-white pl-14 pr-5 sm:pr-32 py-4 sm:py-5
                       text-base sm:text-lg text-ink placeholder:text-stone-400
                       focus:border-amber-400 focus:outline-none focus:ring-4 focus:ring-amber-500/10
                       shadow-sm transition-colors"
          />
          {/* Inside the pill from `sm` up, a full-width button below it on a
              phone. At 390px the absolute button left about 160px of usable
              field and truncated the placeholder mid-word. */}
          <button
            type="submit"
            data-testid="home-search-submit"
            className="btn-primary w-full mt-3 sm:mt-0 sm:w-auto
                       sm:absolute sm:right-2 sm:top-1/2 sm:-translate-y-1/2 sm:!px-6 !py-3 sm:!py-2.5"
          >
            Search
          </button>
        </div>
      </form>

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
