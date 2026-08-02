// Who is reading, and where each of them should start.
//
// WHY THIS EXISTS
// ---------------
// The landing page asked a visitor to pick a PRODUCT AREA — "Discover
// Yourself", "Industrial Readiness", "Scale" — before it asked them anything
// about themselves. Those are the names of our modules. A 17-year-old in
// Nizamabad does not arrive thinking "I need industrial readiness"; they arrive
// thinking "I finished ITI, now what?".
//
// So the first choice on the page is now who you are, and each answer opens a
// page that starts from that. Same surfaces underneath, same routes, same data —
// only the way in is different.
//
// EVERY DESTINATION IS REAL
// -------------------------
// Each `href` below resolves to a page that exists and a category the graph
// actually holds. `Certification` has 30 entities and no relationships, so it is
// worth browsing and not worth putting in a connected-knowledge section — those
// are different questions and the answers differ. tests/test_landing asserts
// every one of these, because a curated start page that opens an empty category
// is worse than not curating at all.

export const AUDIENCES = [
  {
    slug: "student",
    emoji: "🎓",
    label: "Student",
    // Second person, present tense, and about their situation rather than our
    // taxonomy. Read these aloud: each one should sound like the first thing a
    // person who knows the ropes would say.
    headline: "Still studying? Start with what your district already needs.",
    intro:
      "The fastest way to a job or your own business is a skill someone near you is " +
      "already paying for. Here is where to look.",
    starts: [
      { href: "/knowledge?type=skill", label: "Skills worth learning", hint: "45 researched, with how long each takes" },
      { href: "/knowledge?type=provider", label: "Where to learn them", hint: "25 training centres" },
      { href: "/knowledge?type=institution", label: "Colleges and institutes", hint: "66 across both states" },
      { href: "/knowledge?type=scheme", label: "Schemes you may qualify for", hint: "40 government schemes" },
      { href: "/discover", label: "Not sure what suits you?", hint: "A free 7-minute assessment" },
    ],
    prompts: ["ITI", "Electrician", "AI", "Nursing", "Government schemes"],
  },
  {
    slug: "job-seeker",
    emoji: "🧭",
    label: "Job Seeker",
    headline: "Looking for work? Start from what your district hires for.",
    intro:
      "Employers near you need particular skills. Find the skill, then the place " +
      "that teaches it, then the businesses that hire for it.",
    starts: [
      { href: "/knowledge?type=skill", label: "Skills employers ask for", hint: "with difficulty and training time" },
      { href: "/knowledge?type=provider", label: "Where to get trained", hint: "25 training centres" },
      { href: "/knowledge?type=msme", label: "Businesses in your area", hint: "40 researched employers" },
      { href: "/knowledge?type=district", label: "What your district is known for", hint: "61 districts" },
      { href: "/explore", label: "Opportunities posted by people", hint: "the collaborator marketplace" },
    ],
    prompts: ["Welding", "Tailoring", "Driver", "Data entry", "Warangal"],
  },
  {
    slug: "entrepreneur",
    emoji: "🚀",
    label: "Entrepreneur",
    headline: "Want to start something? Start from what already works nearby.",
    intro:
      "Every business idea here says what it costs to start, what skills it needs " +
      "and which government schemes can help fund it.",
    starts: [
      { href: "/opportunity-radar", label: "Business ideas, ranked", hint: "by fit and demand" },
      { href: "/knowledge?type=business", label: "Researched business opportunities", hint: "45 with investment ranges" },
      { href: "/knowledge?type=scheme", label: "Schemes that can fund you", hint: "40 government schemes" },
      { href: "/knowledge?type=bank", label: "Who lends to small business", hint: "21 kinds of funder" },
      { href: "/collaborators", label: "Find people to build with", hint: "the collaborator marketplace" },
    ],
    prompts: ["PMEGP", "Food processing", "Solar", "Mudra loan", "Manufacturing"],
  },
  {
    slug: "farmer",
    emoji: "🌾",
    label: "Farmer",
    headline: "Farming? Start from what grows well where you are.",
    intro:
      "Which crops suit your soil and climate, who buys them, and which schemes " +
      "support growers — all in one place.",
    starts: [
      { href: "/knowledge?type=crop", label: "Crops and what they need", hint: "45 with soil and climate" },
      { href: "/knowledge?type=scheme", label: "Schemes for growers", hint: "40 government schemes" },
      { href: "/knowledge?type=market", label: "Where produce is sold", hint: "11 market channels" },
      { href: "/knowledge?type=export", label: "Countries that buy from here", hint: "29 export destinations" },
      { href: "/knowledge?type=district", label: "Your district", hint: "61 districts" },
    ],
    prompts: ["Turmeric", "Drip irrigation", "PM Kisan", "Organic farming", "Cold storage"],
  },
  {
    slug: "skilled-worker",
    emoji: "🔧",
    label: "Skilled Worker",
    headline: "Already have a trade? See where it can take you.",
    intro:
      "The same skill can mean a job, a certificate, or your own unit. Here is " +
      "what each route looks like.",
    starts: [
      { href: "/knowledge?type=skill", label: "Your trade, in detail", hint: "45 skills researched" },
      { href: "/knowledge?type=certification", label: "Certificates worth having", hint: "30 certifications" },
      { href: "/knowledge?type=business", label: "Businesses you could start", hint: "45 with what they cost" },
      { href: "/knowledge?type=provider", label: "Where to upgrade your skill", hint: "25 training centres" },
      { href: "/collaborators", label: "People looking for your skill", hint: "the collaborator marketplace" },
    ],
    prompts: ["Electrician", "Tile mason", "Welding", "Carpentry", "Plumbing"],
  },
  {
    slug: "business-owner",
    emoji: "🏭",
    label: "Business Owner",
    headline: "Already running something? Here is what growing it takes.",
    intro:
      "Equipment, materials, buyers, funding and export routes — researched from " +
      "official sources, with where each figure came from.",
    starts: [
      { href: "/knowledge?type=machinery", label: "Machinery and equipment", hint: "69 researched" },
      { href: "/knowledge?type=material", label: "Raw materials", hint: "21 with typical sources" },
      { href: "/knowledge?type=market", label: "Where to sell", hint: "11 market channels" },
      { href: "/knowledge?type=export", label: "Where local businesses export", hint: "29 countries" },
      { href: "/knowledge?type=bank", label: "Funding and credit", hint: "21 kinds of funder" },
    ],
    prompts: ["Export", "Machinery", "Working capital", "Packaging", "Quality"],
  },
];

export const AUDIENCE_BY_SLUG = Object.fromEntries(AUDIENCES.map((a) => [a.slug, a]));

//: The example searches under the homepage box. Half are the words the brief
//: named; the rest are what the graph is strongest at, so a first click is
//: unlikely to land on an empty page.
export const HOME_PROMPTS = [
  "Electrician",
  "AI",
  "Government schemes",
  "Medak",
  "Farming",
  "Solar",
  "Manufacturing",
  "PMEGP",
  "Welding",
  "Turmeric",
];
