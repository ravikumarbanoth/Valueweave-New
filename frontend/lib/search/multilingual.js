// Three ways to type the same thing.
//
// THE PROBLEM
// -----------
// A student in Khammam types one of these into the box:
//
//     "electrician"          English
//     "ఎలక్ట్రిషియన్"           Telugu script
//     "elektrishian"         Tanglish — Telugu sounds, Latin letters
//
// They mean the same trade. Before this file, only the first one worked. The
// second returned nothing at all: `normaliseTerm` keeps Telugu characters, so
// the query survived, and then every rung of the ladder compared it against
// names written in Latin script and found no overlap. The third returned
// nothing either — it is four edits from "electrician", and the typo budget
// stops at two, correctly, because a budget wide enough to bridge it would
// also make "electrician" match "elevation".
//
// Tanglish is not a typo. It is a spelling system. It needs a different tool.
//
// WHAT THIS IS NOT
// ----------------
// Not a translator, and not a second search engine. It resolves an input to an
// English CONCEPT and hands that concept's English terms to the ladder that
// already exists in knowledge-search.js. Everything downstream — the six match
// rungs, the typo budget, the acronym handling, the diversify pass — is
// untouched and does all the same work it did before.
//
// THREE LAYERS, CHEAPEST FIRST
// ----------------------------
//   1  exact lookup   the normalised input is a known alias, in any language
//   2  transliterate  Telugu script -> Latin, then try layer 1 and 3 again
//   3  phonetic key   consonant skeleton, so spelling variance collapses
//
// Layer 3 is deliberately confined to the curated concept table in
// vocabulary/concepts.js. A consonant skeleton is a blunt instrument — "rt" is the key
// for "raitu" and would also be the key for "root", "rate" and "art" — and
// running it over 647 free-form entity names would manufacture nonsense. Over
// a closed vocabulary whose keys are asserted unique by a test, it is exactly
// the right blunt instrument.

// A .js data module and not a .json one, for two reasons that both matter:
// bare `node` refuses a JSON import without an import attribute that the
// bundler does not accept, so a .json here would be untestable outside a
// build; and a vocabulary is worth annotating — half of what makes the table
// maintainable is the note saying why a term is in it.
import CONCEPTS from "./vocabulary/concepts.js";

// ── Normalisation ──────────────────────────────────────────────────────────
// Wider than search-vocabulary's normaliseTerm, which is Latin-facing. Zero
// width joiners in particular: "వైర్‌మ్యాన్" carries a U+200C between the
// syllables and a user typing the same word on a different keyboard may not.
// Two strings that look identical on screen must compare equal.
const ZERO_WIDTH = /[​-‍﻿]/g;

export function normalise(text) {
  return String(text || "")
    .normalize("NFC")
    .replace(ZERO_WIDTH, "")
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\p{M}\s]/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

// ── Telugu -> Latin ────────────────────────────────────────────────────────
// Telugu is an abugida: a consonant carries an inherent "a" unless a vowel
// sign replaces it or a virama removes it. Transliteration is therefore a
// single left-to-right pass with one character of pending state, not a
// dictionary — which is the whole point, because it means all 61 districts,
// every scheme and everything researched next year are reachable in Telugu
// script without anyone adding a row anywhere.
//
//     మెదక్   -> me + da + k        -> "medak"
//     ఖమ్మం   -> kha + m + ma + m   -> "khammam"
//     లిఫ్ట్   -> li + f + t         -> "lift"
//
// The scheme is phonetic rather than scholarly: no diacritics, no distinction
// between the dental and retroflex series. A reader looking for a district
// does not care that త and ట are different letters, and the phonetic key
// below folds the distinction away regardless.
const TE_VOWEL = {
  "అ": "a", "ఆ": "aa", "ఇ": "i", "ఈ": "ii",
  "ఉ": "u", "ఊ": "uu", "ఋ": "ru", "ౠ": "ruu",
  "ఌ": "lu", "ఎ": "e", "ఏ": "ee", "ఐ": "ai",
  "ఒ": "o", "ఓ": "oo", "ఔ": "au",
};

const TE_MATRA = {
  "ా": "aa", "ి": "i", "ీ": "ii", "ు": "u",
  "ూ": "uu", "ృ": "ru", "ౄ": "ruu", "ె": "e",
  "ే": "ee", "ై": "ai", "ొ": "o", "ో": "oo",
  "ౌ": "au",
};

const TE_CONSONANT = {
  "క": "k", "ఖ": "kh", "గ": "g", "ఘ": "gh", "ఙ": "ng",
  "చ": "ch", "ఛ": "chh", "జ": "j", "ఝ": "jh", "ఞ": "ny",
  "ట": "t", "ఠ": "th", "డ": "d", "ఢ": "dh", "ణ": "n",
  "త": "t", "థ": "th", "ద": "d", "ధ": "dh", "న": "n",
  "ప": "p", "ఫ": "f", "బ": "b", "భ": "bh", "మ": "m",
  "య": "y", "ర": "r", "ఱ": "r", "ల": "l", "ళ": "l",
  "ఴ": "l", "వ": "v", "శ": "s", "ష": "sh", "స": "s",
  "హ": "h",
};

const TE_VIRAMA = "్";
const TE_ANUSVARA = "ం";
const TE_VISARGA = "ః";
const TE_CANDRABINDU = "ఁ";

const TELUGU_RANGE = /[ఀ-౿]/;

/** True when the text contains any Telugu character. */
export function hasTelugu(text) {
  return TELUGU_RANGE.test(String(text || ""));
}

/**
 * Telugu script to a phonetic Latin spelling.
 *
 * Anything that is not Telugu passes through untouched, so a mixed query —
 * "మెదక్ electrician", which is exactly how a bilingual person types — comes
 * out as "medak electrician" and searches as one phrase.
 *
 * TWO DECISIONS THAT LOOK WRONG AND ARE NOT
 * ------------------------------------------
 * Long vowels are written short. A faithful scheme gives నిజామాబాద్ as
 * "nijaamaabaad", and the district is spelled Nizamabad — three edits away,
 * past any typo budget worth having. Compacting them gives "nijamabad", one
 * edit, which the fuzzy rung already reaches. The goal is to find the row, not
 * to satisfy a transliteration standard.
 *
 * And the anusvara ం becomes "n" before a consonant, "m" otherwise. It is a
 * nasal that takes the place of whatever follows it, so వరంగల్ is Warangal and
 * not "Waramgal"; ఖమ్మం, where it ends the word, stays Khammam.
 */
export function transliterateTelugu(text) {
  const src = [...String(text || "").normalize("NFC").replace(ZERO_WIDTH, "")];
  const out = [];
  let pending = null; // the inherent or applied vowel of the consonant just emitted

  const flush = () => {
    if (pending) out.push(pending);
    pending = null;
  };

  src.forEach((ch, i) => {
    if (TE_CONSONANT[ch] !== undefined) {
      flush();
      out.push(TE_CONSONANT[ch]);
      pending = "a";
    } else if (TE_MATRA[ch] !== undefined) {
      pending = TE_MATRA[ch];
    } else if (ch === TE_VIRAMA) {
      pending = null;
    } else if (TE_VOWEL[ch] !== undefined) {
      flush();
      out.push(TE_VOWEL[ch]);
    } else if (ch === TE_ANUSVARA) {
      flush();
      out.push(TE_CONSONANT[src[i + 1]] !== undefined ? "n" : "m");
    } else if (ch === TE_VISARGA) {
      flush();
      out.push("h");
    } else if (ch === TE_CANDRABINDU) {
      flush();
      out.push("n");
    } else {
      flush();
      out.push(ch);
    }
  });
  flush();

  return out.join("").replace(/([aeiou])\1/g, "$1");
}

// ── Phonetic key ───────────────────────────────────────────────────────────
// Tanglish spelling is unstable in predictable ways. The same trade is written
// "elektrishian", "electrishan", "elektrisian"; the same district "khammam" or
// "kammam"; the same word "vyavasayam" or "vyavasaayam". What stays constant is
// the consonant skeleton, so that is what we compare.
//
// The English side needs one pass first, because English spelling encodes
// sounds that Telugu romanisation writes plainly: the "cian" in "electrician"
// is the same sound as the "shian" someone types by ear.
const SOUND_FOLDS = [
  [/tion/g, "san"], [/sion/g, "san"], [/cious/g, "sas"],
  [/cia/g, "sa"], [/cie/g, "se"], [/ci/g, "si"], [/ce/g, "se"], [/cy/g, "sy"],
  [/chh/g, "c"], [/ch/g, "c"], [/sh/g, "s"], [/zh/g, "s"], [/ph/g, "f"],
  [/gh/g, "g"], [/bh/g, "b"], [/dh/g, "d"], [/th/g, "t"], [/kh/g, "k"],
  [/ck/g, "k"], [/qu/g, "k"], [/x/g, "ks"], [/z/g, "s"], [/w/g, "v"],
  [/c/g, "k"], [/q/g, "k"], [/j/g, "j"],
];

const VOWELS = new Set(["a", "e", "i", "o", "u"]);
//: Dropped from the skeleton, not from the word. `y` and `h` are written
//: inconsistently between romanisations of the same sound ("shiyan"/"shian",
//: "Mahaboobnagar"/"Mahbubnagar") and carry almost no discriminating power.
const SKELETON_DROP = new Set(["y", "h"]);

//: Below this, a skeleton says nothing. "AI" would key to "a", and every
//: concept beginning with a vowel would answer to it.
const MIN_PHONETIC_INPUT = 4;

//: And below this, a skeleton says almost nothing. "raitu" (farmer) and
//: "rayiti" (subsidy) both reduce to "rt", as would "root", "rate" and "art".
//: Two letters is not evidence. Both of those words are still reachable — they
//: are exact aliases — they just do not get a phonetic fallback as well.
const MIN_SKELETON = 3;

/**
 * The consonant skeleton of a word, after sound folding.
 *
 *     electrician   -> elktrsn
 *     elektrishian  -> elktrsn
 *     ఎలక్ట్రిషియన్   -> elaktrishiyan -> elktrsn
 *
 * The first character survives even when it is a vowel: dropping it would
 * merge "udyogam" and "dyogam", and the leading sound is the one people get
 * right. Returns "" for anything too short to be meaningful.
 */
export function phoneticKey(word) {
  let w = normalise(word).replace(/[^a-z\s]/g, "");
  if (w.replace(/\s/g, "").length < MIN_PHONETIC_INPUT) return "";
  for (const [pattern, replacement] of SOUND_FOLDS) w = w.replace(pattern, replacement);

  const parts = [];
  for (const token of w.split(" ").filter(Boolean)) {
    const chars = [];
    for (let i = 0; i < token.length; i += 1) {
      const c = token[i];
      if (i === 0) { chars.push(c); continue; }
      if (VOWELS.has(c) || SKELETON_DROP.has(c)) continue;
      chars.push(c);
    }
    // "khammam" and "kammam" must not differ by a doubled letter.
    const collapsed = chars.filter((c, i) => c !== chars[i - 1]).join("");
    if (collapsed) parts.push(collapsed);
  }
  const key = parts.join(" ");
  return key.replace(/\s/g, "").length < MIN_SKELETON ? "" : key;
}

// ── The concept table ──────────────────────────────────────────────────────
// concepts.json is data, not code, so a term can be added by someone who does
// not write JavaScript. See vocabulary/README.md for the contract and
// tests/test_multilingual_search.py for what is enforced about it.
//
// Three indexes are built once at module load: by alias, by phonetic key, and
// by concept id. 200-odd concepts is nothing to index and everything to look
// up on every keystroke.
const BY_ALIAS = new Map();
const BY_PHONETIC = new Map();
const BY_ID = new Map();

function indexAlias(alias, concept, language) {
  const key = normalise(alias);
  if (!key) return;
  if (!BY_ALIAS.has(key)) BY_ALIAS.set(key, { concept, language });

  // Telugu-script aliases are also indexed under their transliteration, so
  // "మెదక్" and "medak" are one entry maintained in one place.
  if (hasTelugu(alias)) {
    const roman = normalise(transliterateTelugu(alias));
    if (roman && !BY_ALIAS.has(roman)) BY_ALIAS.set(roman, { concept, language: "te-latn" });
    const pk = phoneticKey(roman);
    if (pk && !BY_PHONETIC.has(pk)) BY_PHONETIC.set(pk, { concept, language: "te-latn" });
    return;
  }
  const pk = phoneticKey(alias);
  if (pk && !BY_PHONETIC.has(pk)) BY_PHONETIC.set(pk, { concept, language });
}

for (const concept of CONCEPTS.concepts || []) {
  BY_ID.set(concept.id, concept);
  indexAlias(concept.id, concept, "en");
  indexAlias(concept.en_canonical, concept, "en");
  for (const [language, list] of [
    ["en", concept.en], ["te", concept.te], ["tanglish", concept.tanglish],
  ]) {
    for (const alias of list || []) indexAlias(alias, concept, language);
  }
}

export const CONCEPT_COUNT = BY_ID.size;

/** Every concept, for tooling and tests. */
export function allConcepts() {
  return [...BY_ID.values()];
}

/**
 * Resolve one phrase to a concept, or null.
 *
 * `layer` records which of the three found it, which is the only way to tell
 * afterwards whether the Telugu path or the phonetic path is carrying a query
 * — and therefore the only way to know which one broke when one of them does.
 */
export function resolvePhrase(phrase) {
  const q = normalise(phrase);
  if (!q) return null;

  const direct = BY_ALIAS.get(q);
  if (direct) return { ...direct, layer: "alias", matched: q };

  if (hasTelugu(phrase)) {
    const roman = normalise(transliterateTelugu(phrase));
    const viaScript = BY_ALIAS.get(roman);
    if (viaScript) return { ...viaScript, layer: "transliteration", matched: roman };
    const pk = phoneticKey(roman);
    const viaSound = pk && BY_PHONETIC.get(pk);
    if (viaSound) return { ...viaSound, layer: "transliteration+phonetic", matched: roman };
    // No concept, but the romanisation itself is a real search term — this is
    // the path every district takes, and it must not be lost.
    return { concept: null, language: "te", layer: "transliteration", matched: roman };
  }

  const pk = phoneticKey(q);
  const viaSound = pk && BY_PHONETIC.get(pk);
  if (viaSound) return { ...viaSound, layer: "phonetic", matched: q };

  return null;
}

/**
 * Everything a raw query should also be searched as, in English.
 *
 * Returns `{ terms, concepts, script, romanised }`:
 *
 *   terms       [{term, weight, kind}] to merge into the expansion set. Same
 *               shape search-vocabulary.expandQuery already produces, because
 *               that is where they go.
 *   concepts    the concepts that fired, for "showing results for …"
 *   romanised   the Latin form of a Telugu query, or null
 *
 * The whole phrase is tried first, then each word. "మెదక్ లో ఎలక్ట్రిషియన్" —
 * "electrician in Medak", which is how the sentence is actually spoken — has
 * no whole-phrase concept and two word-level ones, and both are wanted.
 */
export function resolveQuery(raw) {
  const text = String(raw || "");
  const q = normalise(text);
  if (!q) return { terms: [], concepts: [], script: "latin", romanised: null };

  const script = hasTelugu(text) ? "telugu" : "latin";
  const terms = new Map();
  const concepts = [];
  const seenConcepts = new Set();

  const add = (term, weight, kind) => {
    const t = normalise(term);
    if (!t) return;
    const existing = terms.get(t);
    if (!existing || existing.weight < weight) terms.set(t, { weight, kind });
  };

  const take = (hit, weight) => {
    if (!hit) return;
    if (hit.concept) {
      if (!seenConcepts.has(hit.concept.id)) {
        seenConcepts.add(hit.concept.id);
        concepts.push({
          ...hit.concept,
          _layer: hit.layer,
          _language: hit.language,
          // Did we do something the reader cannot see? An exact hit on an
          // English synonym is not a translation and needs no announcement —
          // saying "showing results for welder" over a search for "welding"
          // is noise that makes the box look confused. Everything else is a
          // leap the reader is entitled to check.
          _translated: !(hit.language === "en" && hit.layer === "alias"),
        });
      }
      // The canonical English name is treated as though it were typed: someone
      // who writes "ఎలక్ట్రిషియన్" is not making an approximate request, they
      // are asking for electricians in their own language. Demoting it to
      // "related" would rank the exact answer below its own neighbours.
      add(hit.concept.en_canonical, weight, "typed");
      for (const term of hit.concept.expands_to || []) add(term, weight * 0.6, "related");
    } else if (hit.matched) {
      add(hit.matched, weight, "typed");
    }
  };

  const phrase = resolvePhrase(text);
  take(phrase, 1);

  // Only when the whole phrase did NOT land on a concept. "paala parishrama"
  // is dairy farming; its second word on its own is "industry", and letting
  // both fire put WhatsApp Business Automation above the cattle rows. If we
  // understood the sentence, the words in it are noise.
  const phraseUnderstood = Boolean(phrase?.concept);

  const words = q.split(" ").filter((w) => w.length >= 2);
  if (words.length > 1 && !phraseUnderstood) {
    // Telugu postpositions are suffixed and there is no article to strip, so
    // the only stop words worth having are the ones that appear as separate
    // tokens in the sentences people actually type.
    const STOP = new Set(["lo", "in", "for", "of", "the", "and", "me", "ki", "ku", "na"]);
    for (const word of words) {
      if (STOP.has(word)) continue;
      take(resolvePhrase(word), 0.9);
    }
  }

  const romanised = script === "telugu" ? normalise(transliterateTelugu(text)) : null;

  return {
    terms: [...terms].map(([term, { weight, kind }]) => ({ term, weight, kind })),
    concepts,
    script,
    romanised,
  };
}

/**
 * The English phrase to echo back when someone searched in another language.
 *
 * A Telugu speaker who types "పాడి పరిశ్రమ" and gets a page of English cards
 * has no way to tell whether we understood them or guessed. "Showing results
 * for dairy farming" is the difference between a search engine and a slot
 * machine. Returns null when nothing was translated, so the UI says nothing.
 */
export function describeResolution(resolution) {
  if (!resolution) return null;
  const names = (resolution.concepts || [])
    .filter((c) => c._translated)
    .map((c) => c.en_canonical)
    .filter(Boolean);
  if (names.length) return names.join(" · ");
  if (resolution.script === "telugu" && resolution.romanised) return resolution.romanised;
  return null;
}
