// Three ways to type the same thing.
//
// THE PROBLEM
// -----------
// A student in Khammam types one of these into the box:
//
//     "electrician"          English
//     "ఎలక్ట్రిషియన్"           Telugu script
//     "elektrishian"         Tanglish — Telugu sounds, Latin letters
//     "నాకు electrician course కావాలి"   Natural Telugu + English
//     "మెదక్లో ఎలక్ట్రిషియన్ కోర్స్"      Telugu locative suffix + Trade
//
// They mean the same trade. This module resolves the input to English CONCEPTS
// and hands that concept's English terms to the ranking ladder in knowledge-search.js.
// Everything downstream — the match rungs, typo budget, acronyms, and diversity pass —
// does all the same work it did before.

import CONCEPTS from "./vocabulary/concepts.js";

// ── Normalisation ──────────────────────────────────────────────────────────
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
 */
export function transliterateTelugu(text) {
  const src = [...String(text || "").normalize("NFC").replace(ZERO_WIDTH, "")];
  const out = [];
  let pending = null;

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

// ── Suffix and Locative Normalisation ──────────────────────────────────────
/**
 * Strips attached Telugu postpositions/locatives (e.g. -లో, -ల్లో, -కు, -కి, -తో, -lo)
 * so district queries like "మెదక్లో" or "medaklo" resolve to "మెదక్" / "medak".
 */
export function stripSuffix(token) {
  if (!token || typeof token !== "string") return token;
  let t = normalise(token);
  if (hasTelugu(t)) {
    // Anusvara + lo: ఖమ్మంలో -> ఖమ్మం
    if (t.endsWith("ంలో")) return t.slice(0, -3) + "ం";
    // Double la + lo: వరంగల్లో -> వరంగల్
    if (t.endsWith("ల్లో")) return t.slice(0, -4) + "ల్";
    // Simple lo: మెదక్లో -> మెదక్, హైదరాబాద్లో -> హైదరాబాద్
    if (t.endsWith("లో") && t.length > 2) return t.slice(0, -2);
    // Ku / Ki
    if ((t.endsWith("కు") || t.endsWith("కి")) && t.length > 2) return t.slice(0, -2);
    // Tho
    if (t.endsWith("తో") && t.length > 2) return t.slice(0, -2);
    return t;
  }
  // Latin / Tanglish suffixes
  if (t.length > 4) {
    if (t.endsWith("llo")) return t.slice(0, -3) + "l";
    if (t.endsWith("lo") || t.endsWith("la")) return t.slice(0, -2);
    if (t.endsWith("ki") || t.endsWith("ku")) return t.slice(0, -2);
    if (t.endsWith("tho")) return t.slice(0, -3);
  }
  return t;
}

// Known district names for fast query entity recognition
const KNOWN_DISTRICTS = new Set([
  "medak", "warangal", "hyderabad", "khammam", "karimnagar", "nizamabad",
  "mahabubnagar", "nalgonda", "siddipet", "rangareddy", "medchal", "sangareddy",
  "adilabad", "suryapet", "jagtial", "peddapalli", "mancherial", "nirmal",
  "bhadradri", "mahabubabad", "jangaon", "hanumakonda", "wanaparthy", "nagarkurnool",
  "gadwal", "narayanpet", "mulugu", "vikarabad", "guntur", "vijayawada",
  "visakhapatnam", "vizag", "tirupati", "kurnool", "nellore", "kakinada",
  "anantapur", "rajahmundry", "kadapa", "srikakulam", "vizianagaram", "eluru",
  "chittoor", "ongole", "nandyal"
]);

// ── Phonetic key ───────────────────────────────────────────────────────────
const SOUND_FOLDS = [
  [/tion/g, "san"], [/sion/g, "san"], [/cious/g, "sas"],
  [/cia/g, "sa"], [/cie/g, "se"], [/ci/g, "si"], [/ce/g, "se"], [/cy/g, "sy"],
  [/chh/g, "c"], [/ch/g, "c"], [/sh/g, "s"], [/zh/g, "s"], [/ph/g, "f"],
  [/gh/g, "g"], [/bh/g, "b"], [/dh/g, "d"], [/th/g, "t"], [/kh/g, "k"],
  [/ck/g, "k"], [/qu/g, "k"], [/x/g, "ks"], [/z/g, "s"], [/w/g, "v"],
  [/c/g, "k"], [/q/g, "k"], [/j/g, "j"],
];

const VOWELS = new Set(["a", "e", "i", "o", "u"]);
const SKELETON_DROP = new Set(["y", "h"]);
const MIN_PHONETIC_INPUT = 4;
const MIN_SKELETON = 3;

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
    const collapsed = chars.filter((c, i) => c !== chars[i - 1]).join("");
    if (collapsed) parts.push(collapsed);
  }
  const key = parts.join(" ");
  return key.replace(/\s/g, "").length < MIN_SKELETON ? "" : key;
}

// ── The concept table ──────────────────────────────────────────────────────
const BY_ALIAS = new Map();
const BY_PHONETIC = new Map();
const BY_ID = new Map();

function indexAlias(alias, concept, language) {
  const key = normalise(alias);
  if (!key) return;
  if (!BY_ALIAS.has(key)) BY_ALIAS.set(key, { concept, language });

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

export function allConcepts() {
  return [...BY_ID.values()];
}

/**
 * Resolve one phrase or word to a concept or transliterated search term.
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

    // Check stripped suffix for Telugu word (e.g., మెదక్లో -> మెదక్)
    const stripped = stripSuffix(phrase);
    if (stripped !== phrase) {
      const strippedRoman = normalise(transliterateTelugu(stripped));
      const viaStripped = BY_ALIAS.get(strippedRoman);
      if (viaStripped) return { ...viaStripped, layer: "transliteration", matched: strippedRoman };
      const pkStripped = phoneticKey(strippedRoman);
      const viaSoundStripped = pkStripped && BY_PHONETIC.get(pkStripped);
      if (viaSoundStripped) return { ...viaSoundStripped, layer: "transliteration+phonetic", matched: strippedRoman };
      return { concept: null, language: "te", layer: "transliteration", matched: strippedRoman };
    }

    return { concept: null, language: "te", layer: "transliteration", matched: roman };
  }

  // Latin / Tanglish
  const pk = phoneticKey(q);
  const viaSound = pk && BY_PHONETIC.get(pk);
  if (viaSound) return { ...viaSound, layer: "phonetic", matched: q };

  // Check stripped suffix for Latin/Tanglish (e.g. medaklo -> medak)
  const stripped = stripSuffix(q);
  if (stripped !== q) {
    const viaStripped = BY_ALIAS.get(stripped);
    if (viaStripped) return { ...viaStripped, layer: "alias", matched: stripped };
    const pkStripped = phoneticKey(stripped);
    const viaSoundStripped = pkStripped && BY_PHONETIC.get(pkStripped);
    if (viaSoundStripped) return { ...viaSoundStripped, layer: "phonetic", matched: stripped };
    return { concept: null, language: "tanglish", layer: "suffix", matched: stripped };
  }

  // Known district name check
  if (KNOWN_DISTRICTS.has(q)) {
    return { concept: null, language: "en", layer: "district", matched: q };
  }

  return null;
}

// ── Stop Words & Conversational Particles ──────────────────────────────────
const CONVERSATIONAL_STOP_WORDS = new Set([
  // English prepositions and particles
  "lo", "in", "for", "of", "the", "and", "me", "ki", "ku", "na", "to", "at", "by", "from", "with",
  // Telugu pronouns and conversational particles
  "నాకు", "నేను", "మాకు", "మీకు", "నా", "మా", "మీ",
  "కావాలి", "కావాలనుకుంటున్నాను", "కావాలని", "కావాల్సింది",
  "ఉంది", "ఉన్నాయి", "ఉందా", "ఉన్నాయా",
  "ఎక్కడ", "ఎలా", "ఏమిటి", "ఎందుకు", "ఎవరు", "ఏది", "ఎన్ని",
  "కోసం", "గురించి", "ద్వారా", "వద్ద",
  "చేయాలి", "చేయాలనుకుంటున్నాను", "చేయడానికి", "చేసే",
  "నేర్చుకోవాలి", "నేర్చుకోవాలనుకుంటున్నాను", "నేర్చుకోవడానికి",
  "తెలుసుకోవాలి", "చెప్పండి", "చూపించండి",
  // Tanglish transliterations
  "naaku", "naku", "nenu", "maaku", "meeku",
  "kaavali", "kavali", "kosam", "gurinchi",
  "cheyali", "nerchukovali", "telusukovali", "cheppandi",
  "ekkada", "ela", "emiti", "enduku", "undi", "undaa"
]);

/**
 * Everything a raw query should also be searched as, in English.
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
          _translated: !(hit.language === "en" && hit.layer === "alias"),
        });
      }
      add(hit.concept.en_canonical, weight, "typed");
      for (const term of hit.concept.expands_to || []) add(term, weight * 0.6, "related");
    } else if (hit.matched) {
      add(hit.matched, weight, "typed");
    }
  };

  const phrase = resolvePhrase(text);
  take(phrase, 1);

  const phraseUnderstood = Boolean(phrase?.concept);

  const words = text.split(/\s+/).map((w) => normalise(w)).filter((w) => w.length >= 2);
  if (words.length > 1 && !phraseUnderstood) {
    for (const word of words) {
      if (CONVERSATIONAL_STOP_WORDS.has(word)) continue;
      const hit = resolvePhrase(word);
      if (hit) {
        take(hit, 0.9);
      }
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
 */
export function describeResolution(resolution) {
  if (!resolution) return null;
  const names = (resolution.concepts || [])
    .filter((c) => c._translated || resolution.script === "telugu")
    .map((c) => c.en_canonical)
    .filter(Boolean);
  if (names.length) return names.join(" · ");
  if (resolution.script === "telugu" && resolution.romanised) return resolution.romanised;
  return null;
}
