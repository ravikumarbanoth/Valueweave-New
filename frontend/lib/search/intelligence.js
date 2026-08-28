import { resolveQuery } from "../search-vocabulary.js";
import { normalise, hasTelugu, transliterateTelugu, stripSuffix } from "./multilingual.js";

const INTENT_KEYWORDS = [
  [
    "learn",
    [
      // English
      "course", "courses", "training", "learn", "certificate", "certification",
      "classes", "institute", "iti", "polytechnic", "study", "coaching",
      // Telugu
      "కోర్స్", "కోర్సు", "కోర్సులు", "శిక్షణ", "నేర్చుకోవాలి", "నేర్చుకోవాలనుకుంటున్నాను",
      "ట్రైనింగ్", "సర్టిఫికేట్", "పని నేర్చుకోవాలి", "నేర్చుకోవడం", "తరగతులు",
      // Tanglish
      "course", "courses", "shikshana", "sikshana", "nerchukovali", "training",
      "pani nerchukovali", "certificate"
    ]
  ],
  [
    "job",
    [
      // English
      "job", "jobs", "vacancy", "hire", "recruit", "work", "employment", "salary",
      // Telugu
      "ఉద్యోగం", "ఉద్యోగాలు", "ఉద్యోగ", "జాబ్", "జాబ్స్", "పని", "ఉపాధి", "కొలువు", "జీతం",
      // Tanglish
      "udyogam", "udyogalu", "job", "jobs", "pani", "upadhi", "koluvu"
    ]
  ],
  [
    "business",
    [
      // English
      "business", "startup", "start", "shop", "enterprise", "industry",
      "manufacturing unit", "investment", "unit",
      // Telugu
      "వ్యాపారం", "వ్యాపార", "పరిశ్రమ", "సొంత వ్యాపారం", "స్టార్ట్", "ప్రారంభించాలి",
      "దుకాణం", "యూనిట్", "పెట్టుబడి", "తయారీ", "బిజినెస్",
      // Tanglish
      "vyaparam", "parishrama", "sontha vyaparam", "start cheyali", "business"
    ]
  ],
  [
    "scheme",
    [
      // English
      "scheme", "schemes", "subsidy", "loan", "grant", "yojana", "funding",
      "pmegp", "mudra", "credit",
      // Telugu
      "పథకం", "పథకాలు", "సబ్సిడీ", "రాయితీ", "రుణం", "అప్పు", "యోజన", "ఆర్థిక సహాయం",
      // Tanglish
      "pathakam", "pathakalu", "subsidy", "rayiti", "runam", "appu", "yojana"
    ]
  ],
  [
    "service",
    [
      // English
      "repair", "service", "fix", "servicing", "mechanic",
      // Telugu
      "రిపేర్", "సర్వీస్", "మరమ్మత్తు", "బాగు చేయడం",
      // Tanglish
      "repair", "service", "bagu cheyadam"
    ]
  ],
  [
    "question",
    [
      // English
      "how", "what", "where", "why", "who", "which", "when",
      // Telugu
      "ఎలా", "ఏమిటి", "ఎక్కడ", "ఎందుకు", "ఎవరు", "ఏది", "ఎప్పుడు",
      // Tanglish
      "ela", "emiti", "ekkada", "enduku", "evaru", "eppudu"
    ]
  ],
];

const INTENT_LABELS = {
  learn: "a learning or training search",
  job: "a jobs and employment search",
  business: "a business or entrepreneurship search",
  scheme: "a government scheme or subsidy search",
  service: "a service or repair search",
  question: "a question",
  unknown: "a search",
};

const DISTRICTS_MAP = {
  // Telangana
  "medak": "Medak",
  "మెదక్": "Medak",
  "warangal": "Warangal",
  "వరంగల్": "Warangal",
  "varangal": "Warangal",
  "hyderabad": "Hyderabad",
  "హైదరాబాద్": "Hyderabad",
  "haidarabad": "Hyderabad",
  "khammam": "Khammam",
  "ఖమ్మం": "Khammam",
  "karimnagar": "Karimnagar",
  "కరీంనగర్": "Karimnagar",
  "karinnagar": "Karimnagar",
  "nizamabad": "Nizamabad",
  "నిజామాబాద్": "Nizamabad",
  "nijamabad": "Nizamabad",
  "mahabubnagar": "Mahabubnagar",
  "మహబూబ్‌నగర్": "Mahabubnagar",
  "mahabubnagar": "Mahabubnagar",
  "nalgonda": "Nalgonda",
  "నల్గొండ": "Nalgonda",
  "siddipet": "Siddipet",
  "సిద్దిపేట": "Siddipet",
  "rangareddy": "Rangareddy",
  "రంగారెడ్డి": "Rangareddy",
  "medchal": "Medchal-Malkajgiri",
  "మేడ్చల్": "Medchal-Malkajgiri",
  "sangareddy": "Sangareddy",
  "సంగారెడ్డి": "Sangareddy",
  "adilabad": "Adilabad",
  "ఆదిలాబాద్": "Adilabad",
  "suryapet": "Suryapet",
  "సూర్యాపేట": "Suryapet",
  "jagtial": "Jagtial",
  "జగిత్యాల": "Jagtial",
  "peddapalli": "Peddapalli",
  "పెద్దపల్లి": "Peddapalli",
  "mancherial": "Mancherial",
  "మంచిర్యాల": "Mancherial",
  "nirmal": "Nirmal",
  "నిర్మల్": "Nirmal",
  "bhadradri": "Bhadradri Kothagudem",
  "భద్రాద్రి": "Bhadradri Kothagudem",
  "mahabubabad": "Mahabubabad",
  "మహబూబాబాద్": "Mahabubabad",
  "jangaon": "Jangaon",
  "జనగామ": "Jangaon",
  "hanumakonda": "Hanumakonda",
  "హనుమకొండ": "Hanumakonda",
  "wanaparthy": "Wanaparthy",
  "వనపర్తి": "Wanaparthy",
  "nagarkurnool": "Nagarkurnool",
  "నాగర్‌కర్నూల్": "Nagarkurnool",
  "gadwal": "Jogulamba Gadwal",
  "గద్వాల": "Jogulamba Gadwal",
  "narayanpet": "Narayanpet",
  "నారాయణపేట": "Narayanpet",
  "mulugu": "Mulugu",
  "ములుగు": "Mulugu",
  "vikarabad": "Vikarabad",
  "వికారాబాద్": "Vikarabad",
  // Andhra Pradesh
  "guntur": "Guntur",
  "గుంటూరు": "Guntur",
  "vijayawada": "Vijayawada",
  "విజయవాడ": "Vijayawada",
  "visakhapatnam": "Visakhapatnam",
  "vizag": "Visakhapatnam",
  "విశాఖపట్నం": "Visakhapatnam",
  "tirupati": "Tirupati",
  "తిరుపతి": "Tirupati",
  "kurnool": "Kurnool",
  "కర్నూలు": "Kurnool",
  "nellore": "Nellore",
  "నెల్లూరు": "Nellore",
  "kakinada": "Kakinada",
  "కాకినాడ": "Kakinada",
  "anantapur": "Anantapur",
  "అనంతపురం": "Anantapur",
  "rajahmundry": "Rajahmundry",
  "రాజమండ్రి": "Rajahmundry",
  "kadapa": "Kadapa",
  "కడప": "Kadapa",
  "srikakulam": "Srikakulam",
  "శ్రీకాకుళం": "Srikakulam",
  "vizianagaram": "Vizianagaram",
  "విజయనగరం": "Vizianagaram",
  "eluru": "Eluru",
  "ఏలూరు": "Eluru",
  "chittoor": "Chittoor",
  "చిత్తూరు": "Chittoor",
  "ongole": "Prakasam",
  "ఒంగోలు": "Prakasam",
  "nandyal": "Nandyal",
  "నంద్యాల": "Nandyal",
};

export function extractLocation(query) {
  const text = String(query || "").trim();
  if (!text) return null;

  const rawTokens = text.split(/\s+/);
  for (const raw of rawTokens) {
    const norm = normalise(raw);
    const stripped = stripSuffix(raw);
    const normStripped = normalise(stripped);

    for (const token of [norm, stripped, normStripped]) {
      if (DISTRICTS_MAP[token]) {
        return DISTRICTS_MAP[token];
      }
      if (hasTelugu(token)) {
        const roman = normalise(transliterateTelugu(token));
        if (DISTRICTS_MAP[roman]) return DISTRICTS_MAP[roman];
      }
    }
  }
  return null;
}

export function detectSearchIntent(query) {
  const raw = String(query || "");
  const q = normalise(raw);
  const roman = normalise(transliterateTelugu(raw));
  for (const [intent, triggers] of INTENT_KEYWORDS) {
    if (triggers.some((term) => {
      const nTerm = normalise(term);
      return q.includes(nTerm) || roman.includes(nTerm) || raw.toLowerCase().includes(term.toLowerCase());
    })) {
      return intent;
    }
  }
  return "unknown";
}

function normalizeGroups(groups = []) {
  if (!Array.isArray(groups)) return groups || {};
  return Object.fromEntries((groups || []).map((group) => [group.id, group.total || 0]));
}

export function detectSearchGaps(intent, groups = []) {
  const counts = normalizeGroups(groups);
  const gaps = [];
  if (intent === "learn" && !counts.skills && !counts.education && !counts.research) {
    gaps.push("Skill and training content");
  }
  if (intent === "job" && !counts.business && !counts.skills && !counts.education) {
    gaps.push("Job and occupation content");
  }
  if (intent === "scheme" && !counts.government && !counts.support) {
    gaps.push("Government scheme and subsidy content");
  }
  if (intent === "business" && !counts.business && !counts.manufacturing) {
    gaps.push("Business opportunity and MSME content");
  }
  return gaps;
}

export function analyzeSearchQuery(query, groups = []) {
  const q = String(query || "").trim();
  if (!q) return null;
  const resolution = resolveQuery(q);
  const intent = detectSearchIntent(q);
  const location = extractLocation(q);
  const normalizedGroups = normalizeGroups(groups);
  const gapSignals = detectSearchGaps(intent, normalizedGroups);

  return {
    query: q,
    intent,
    intentLabel: INTENT_LABELS[intent] || INTENT_LABELS.unknown,
    location,
    entities: resolution.concepts || [],
    resolution,
    groups: normalizedGroups,
    gaps: gapSignals,
  };
}
