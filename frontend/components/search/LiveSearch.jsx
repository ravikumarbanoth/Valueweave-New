// The search box, everywhere.
//
// WHAT A STUDENT SHOULD BE ABLE TO DO
// -----------------------------------
// Type three letters and see what exists. Not press Search, wait for a page,
// read it, go back and try a different word — three letters and a list. That
// loop is the whole difference between a search box you use once and one you
// think with, and on a Tier-2 mobile connection the difference is thirty
// seconds versus one.
//
// The Search button stays. Suggestions are for finding a thing you can name;
// the results page is for a question with more than one answer, and someone
// who wants "everything about electricians" should not have to pick one row
// from a dropdown to get there.
//
// WHY THE LIST IS GROUPED
// -----------------------
// Eight rows of mixed districts, skills and articles asks the reader to sort
// them. A one-word heading above each run of the same kind costs a line and
// removes the sorting: someone who wanted a scheme reads one heading.
//
// KEYBOARD AND SCREEN READERS
// ---------------------------
// This is a combobox, so it is built as one: `role="combobox"` on the input
// with `aria-expanded` and `aria-activedescendant`, `role="listbox"` on the
// panel, `role="option"` on each row. Arrow keys move the active option
// WITHOUT moving focus — focus stays in the input so typing continues to work,
// which is why the active row is tracked by id rather than by focusing it.
// Enter opens it, Escape closes the panel and leaves the text alone.
//
// TOUCH
// -----
// Rows are 44px minimum, and on a phone the panel is a block in normal flow
// between the input and the Search button rather than an overlay — so the
// on-screen keyboard cannot cover it and it cannot cover the button.
// `onMouseDown` and not `onClick` on a row: a click fires after blur, and blur
// closes the panel, so an onClick handler on a row that no longer exists never
// runs.
"use client";

import { useCallback, useEffect, useId, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Search, Loader2, CornerDownLeft } from "lucide-react";
import { trackSearch } from "@/lib/search-tracking";
import { recall } from "@/lib/journey";
import { useLanguage } from "@/lib/language";

//: Matches MIN_QUERY on the server. Suggesting after one character means
//: suggesting from a query the ranker will not answer.
const MIN_CHARS = 2;

//: Long enough that a fast typist makes one request per word rather than one
//: per letter, short enough that a slow one never notices waiting. Measured
//: against the box, not chosen from a blog post: at 250ms the list visibly
//: lags the cursor, at 80ms a seven-letter word costs five requests.
const DEBOUNCE_MS = 140;

/**
 * Split a name around every run that matches the query, for highlighting.
 *
 * Match on the words of the query, not the whole string, so "tile mason"
 * highlights both halves of "Tiles Fixing (Tile Mason)". Case-insensitive and
 * accent-blind is deliberate: the highlight should show the reader why the row
 * is here, and a highlight that disagrees with their eyes is worse than none.
 */
export function highlight(name, query) {
  const text = String(name || "");
  const words = String(query || "")
    .toLowerCase()
    .split(/[^\p{L}\p{N}]+/u)
    .filter((w) => w.length >= 2)
    .sort((a, b) => b.length - a.length);
  if (!words.length) return [{ text, hit: false }];

  const lower = text.toLowerCase();
  const marks = new Array(text.length).fill(false);
  for (const word of words) {
    let from = lower.indexOf(word);
    while (from !== -1) {
      for (let i = from; i < from + word.length; i += 1) marks[i] = true;
      from = lower.indexOf(word, from + word.length);
    }
  }

  const parts = [];
  let start = 0;
  for (let i = 1; i <= text.length; i += 1) {
    if (i === text.length || marks[i] !== marks[start]) {
      parts.push({ text: text.slice(start, i), hit: marks[start] });
      start = i;
    }
  }
  return parts;
}

export default function LiveSearch({
  initialQuery = "",
  placeholder = "Electrician, PMEGP, Medak…",
  label = "What are you looking for?",
  labelClassName = "block font-display font-bold text-[15px] text-ink mb-3",
  hiddenLabel = false,
  size = "hero",
  autoFocus = false,
  testId = "live-search",
}) {
  const router = useRouter();
  const listboxId = useId();
  const { t } = useLanguage();

  const [query, setQuery] = useState(initialQuery);
  const [items, setItems] = useState([]);
  const [resolved, setResolved] = useState(null);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [active, setActive] = useState(-1);
  //: Has this person typed here yet? On a results page the box arrives
  //: pre-filled with what they searched for, and without this the panel
  //: opened by itself on load — a dropdown covering the answers to the
  //: question it is offering to help them ask. It also means a visitor who
  //: never touches the box costs zero requests.
  const [touched, setTouched] = useState(false);

  const inputRef = useRef(null);
  const boxRef = useRef(null);
  //: Every in-flight request carries the sequence number it was issued with.
  //: Without this, "electr" answering after "electrician" replaces the right
  //: list with a staler one — the classic autocomplete race, and the one that
  //: makes a fast box feel haunted.
  const seq = useRef(0);

  const go = useCallback((term) => {
    const q = String(term ?? query).trim();
    setOpen(false);
    router.push(q ? `/knowledge?q=${encodeURIComponent(q)}` : "/knowledge");
  }, [query, router]);

  useEffect(() => {
    const q = query.trim();
    if (!touched) return undefined;
    if (q.length < MIN_CHARS) {
      setItems([]);
      setResolved(null);
      setLoading(false);
      return undefined;
    }

    const mine = (seq.current += 1);
    setLoading(true);
    const timer = setTimeout(async () => {
      try {
        // Phase 9. `as` is the audience this visitor told us they were, or
        // nothing at all. It goes in the URL rather than a header or a cookie
        // because the route is a shared public cache: two students typing
        // "elec" must hit one cache entry, and a student and a farmer must hit
        // two. A header would have made every one of them cache-identical and
        // served the farmer the student's order.
        const as = recall();
        const response = await fetch(
          `/api/search/suggest?q=${encodeURIComponent(q)}${as ? `&as=${as}` : ""}`);
        const data = await response.json();
        if (mine !== seq.current) return;
        setItems(data.items || []);
        setResolved(data.resolved || null);
        setOpen(true);
        setActive(-1);
        // The signal the research backlog reads.
        //
        // `search_events` and `lib/search-tracking.js` have both existed since
        // migration 004, and `trackSearch` had ZERO callers — the admin page
        // at /admin/search-intelligence renders a "No-Results Searches —
        // content gaps" panel over an empty table and says so in its own copy.
        // Every no-result search since launch was discarded at the moment it
        // happened.
        //
        // Recorded on the SETTLED query only: the debounce means "electrician"
        // produces one event rather than eleven, and a prefix of a word nobody
        // finished typing is not a content gap. Fire-and-forget — trackSearch
        // swallows its own errors and this must never delay the list.
        trackSearch({ query: q, page: "search", resultsCount: (data.items || []).length });
      } catch {
        // Offline, or the route is down. Leave whatever is on screen and let
        // the Search button do its job — the form still works without this.
        if (mine === seq.current) setItems([]);
      } finally {
        if (mine === seq.current) setLoading(false);
      }
    }, DEBOUNCE_MS);

    return () => clearTimeout(timer);
  }, [query, touched]);

  // A tap anywhere else closes the panel. Pointerdown rather than click so it
  // beats the browser's own focus handling on iOS.
  useEffect(() => {
    if (!open) return undefined;
    const away = (event) => {
      if (boxRef.current && !boxRef.current.contains(event.target)) setOpen(false);
    };
    document.addEventListener("pointerdown", away);
    return () => document.removeEventListener("pointerdown", away);
  }, [open]);

  const onKeyDown = (event) => {
    if (event.key === "Escape") {
      setOpen(false);
      return;
    }
    if (!open || items.length === 0) return;
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      const step = event.key === "ArrowDown" ? 1 : -1;
      // Wraps through -1, which is "no option active, the input is the target"
      // — pressing up from the first row puts you back in your own text
      // rather than teleporting to the bottom of the list.
      setActive((current) => {
        const next = current + step;
        if (next < -1) return items.length - 1;
        if (next >= items.length) return -1;
        return next;
      });
    } else if (event.key === "Enter" && active >= 0) {
      event.preventDefault();
      setOpen(false);
      router.push(items[active].href);
    }
  };

  const big = size === "hero";
  let previousGroup = null;

  return (
    <div ref={boxRef} className="relative w-full" data-testid={testId}>
      <form
        role="search"
        onSubmit={(event) => { event.preventDefault(); go(); }}
        className="w-full"
      >
        <label
          htmlFor={`${listboxId}-input`}
          className={hiddenLabel ? "sr-only" : labelClassName}
        >
          {label}
        </label>

        {/* A flex COLUMN on a phone, a positioned block from `sm` up.

            The order matters and only on the small screen. With the submit
            button in normal flow under the input — which is where it has to be
            at 390px, since an absolute one leaves about 160px of usable field
            — a panel placed after the form appears BELOW the button, ninety
            pixels from the text it is completing. Making the wrapper a column
            lets the panel sit at order-2 and the button at order-3, so
            suggestions are directly under the box and the button is still
            there, under them, for an explicit search.

            From `sm` the wrapper is a positioning context again: the button
            returns inside the pill and the panel becomes an overlay. */}
        <div className="relative flex flex-col sm:block">
          {/* Pinned to the FIRST LINE of the wrapper, not its middle. The
              wrapper is a column on a phone — input, panel, button — so
              `top-1/2` put the magnifier halfway down the whole stack and,
              with a panel open, on top of the Search button. From `sm` the
              wrapper is the input again and centring is correct. */}
          <Search
            size={big ? 20 : 18}
            aria-hidden="true"
            className={`absolute left-4 ${big ? "sm:left-5 top-[1.4rem]" : "top-3"}
                        sm:top-1/2 sm:-translate-y-1/2 text-stone-400 pointer-events-none`}
          />
          <input
            id={`${listboxId}-input`}
            ref={inputRef}
            value={query}
            onChange={(event) => { setTouched(true); setQuery(event.target.value); }}
            onKeyDown={onKeyDown}
            onFocus={() => { if (items.length) setOpen(true); }}
            placeholder={placeholder}
            autoComplete="off"
            autoCorrect="off"
            spellCheck="false"
            // eslint-disable-next-line jsx-a11y/no-autofocus
            autoFocus={autoFocus}
            data-testid={`${testId}-input`}
            role="combobox"
            aria-expanded={open && items.length > 0}
            aria-controls={listboxId}
            aria-autocomplete="list"
            aria-activedescendant={active >= 0 ? `${listboxId}-opt-${active}` : undefined}
            className={`order-1 ${big
              ? `w-full rounded-full border-2 border-stone-200 bg-white pl-12 sm:pl-14 pr-5 sm:pr-32
                 py-4 sm:py-5 text-base sm:text-lg text-ink placeholder:text-stone-400
                 focus:border-amber-400 focus:outline-none focus:ring-4 focus:ring-amber-500/10
                 shadow-sm transition-colors`
              : `w-full input-field pl-11`}`}
          />
          {loading && (
            <Loader2
              size={16}
              aria-hidden="true"
              className={`absolute ${big ? "right-4 sm:right-28 top-[1.55rem]" : "right-3 top-3.5"}
                          sm:top-1/2 sm:-translate-y-1/2 text-stone-300 animate-spin`}
            />
          )}
          {/* Inside the pill from `sm` up, full width below it on a phone. At
              390px an absolute button leaves about 160px of usable field and
              truncates the placeholder mid-word — found on a screenshot in
              Phase 6 and kept fixed here. */}
          <button
            type="submit"
            data-testid={`${testId}-submit`}
            className={`order-3 ${big
              ? `btn-primary w-full mt-3 sm:mt-0 sm:w-auto sm:absolute sm:right-2 sm:top-1/2
                 sm:-translate-y-1/2 sm:!px-6 !py-3 sm:!py-2.5`
              : "btn-primary mt-2 w-full sm:w-auto sm:ml-2"}`}
          >
            {t("search.button")}
          </button>

          {open && items.length > 0 && (
            <div
              className="order-2 mt-2 rounded-2xl border border-stone-200 bg-white shadow-xl
                         overflow-hidden text-left z-30
                         sm:absolute sm:left-0 sm:right-0 sm:top-full"
              data-testid={`${testId}-panel`}
            >
              {resolved && (
                <p className="px-4 py-2 text-[11px] text-stone-500 bg-stone-50 border-b border-stone-100"
                   data-testid={`${testId}-resolved`}>
                  Showing results for <span className="font-semibold text-ink">{resolved}</span>
                </p>
              )}

              <ul id={listboxId} role="listbox" aria-label={t("search.suggestions")}
                  className="max-h-[60vh] overflow-y-auto">
                {items.map((item, index) => {
                  const heading = item.groupLabel !== previousGroup ? item.groupLabel : null;
                  previousGroup = item.groupLabel;
                  return (
                    <li key={item.id} role="presentation">
                      {heading && (
                        <p className="px-4 pt-3 pb-1 text-[10px] uppercase tracking-widest text-stone-400">
                          {heading}
                        </p>
                      )}
                      <div
                        id={`${listboxId}-opt-${index}`}
                        role="option"
                        aria-selected={active === index}
                        data-testid={`${testId}-option`}
                        onMouseDown={(event) => { event.preventDefault(); router.push(item.href); }}
                        onMouseEnter={() => setActive(index)}
                        className={`flex items-center justify-between gap-3 px-4 py-2.5 min-h-[44px]
                                    cursor-pointer ${active === index ? "bg-amber-50" : ""}`}
                      >
                        <span className="min-w-0">
                          <span className="block text-[14px] text-ink leading-snug">
                            {highlight(item.name, query).map((part, i) => (
                              part.hit
                                ? <mark key={i} className="bg-amber-200/70 text-ink rounded-[2px]">{part.text}</mark>
                                : <span key={i}>{part.text}</span>
                            ))}
                          </span>
                          {/* Why a row that does not contain the typed word is
                              here. Without it, "electrician" returning "Power
                              Distribution Technician" reads as a bug. */}
                          {item.via && (
                            <span className="block text-[11px] text-stone-400">
                              matched “{item.via}”
                            </span>
                          )}
                        </span>
                        <span className="text-[11px] text-stone-400 shrink-0">{item.kind}</span>
                      </div>
                    </li>
                  );
                })}
              </ul>

              <button
                type="button"
                onMouseDown={(event) => { event.preventDefault(); go(); }}
                data-testid={`${testId}-see-all`}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 min-h-[44px]
                           text-[13px] font-display font-bold text-amber-700 border-t border-stone-100
                           hover:bg-amber-50 transition-colors"
              >
                {t("search.see_all")} “{query.trim()}”
                <CornerDownLeft size={14} aria-hidden="true" />
              </button>
            </div>
          )}
        </div>
      </form>

      {/* Announced to a screen reader without being read aloud on every
          keystroke — polite, and only the count, because reading eight names
          after every letter is unusable. */}
      <span className="sr-only" role="status" aria-live="polite">
        {open && items.length > 0
          ? `${items.length} suggestion${items.length === 1 ? "" : "s"}`
          : ""}
      </span>

    </div>
  );
}
