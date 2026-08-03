"use client";
import { useState } from "react";
import Link from "next/link";
import LiveMatches from "@/components/LiveMatches";

// ─── DISTRICT MASTER ──────────────────────────────────────────────────────────
// Tiers: Metro | Tier-1 | Tier-2 | Tier-3 | Rural
// opTags: sectors with active opportunity demand in that district

const DISTRICT_MASTER = {
  "Telangana": [
    { name: "Hyderabad", tier: "Metro", opTags: ["Technology", "Finance", "Food", "Healthcare", "Education"] },
    { name: "Rangareddy", tier: "Tier-1", opTags: ["Technology", "Manufacturing", "Education", "Food"] },
    { name: "Medchal-Malkajgiri", tier: "Tier-1", opTags: ["Manufacturing", "Technology", "Healthcare", "Education"] },
    { name: "Sangareddy", tier: "Tier-2", opTags: ["Agriculture", "Manufacturing", "Healthcare", "Education"] },
    { name: "Warangal", tier: "Tier-2", opTags: ["Education", "Healthcare", "Agriculture", "Manufacturing"] },
    { name: "Nizamabad", tier: "Tier-2", opTags: ["Agriculture", "Food", "Healthcare", "Education"] },
    { name: "Karimnagar", tier: "Tier-2", opTags: ["Agriculture", "Healthcare", "Education", "Manufacturing"] },
    { name: "Khammam", tier: "Tier-2", opTags: ["Agriculture", "Healthcare", "Education", "Manufacturing"] },
    { name: "Nalgonda", tier: "Tier-3", opTags: ["Agriculture", "Healthcare", "Education", "Finance"] },
    { name: "Mahbubnagar", tier: "Tier-3", opTags: ["Agriculture", "Healthcare", "Education", "Finance"] },
    { name: "Medak", tier: "Tier-3", opTags: ["Agriculture", "Healthcare", "Education", "Manufacturing"] },
    { name: "Siddipet", tier: "Tier-3", opTags: ["Agriculture", "Healthcare", "Education", "Finance"] },
    { name: "Suryapet", tier: "Tier-3", opTags: ["Agriculture", "Food", "Healthcare", "Education"] },
    { name: "Adilabad", tier: "Rural", opTags: ["Agriculture", "Healthcare", "Education", "Manufacturing"] },
    { name: "Jagtial", tier: "Rural", opTags: ["Agriculture", "Healthcare", "Education", "Manufacturing"] },
    { name: "Mancherial", tier: "Rural", opTags: ["Agriculture", "Manufacturing", "Healthcare", "Education"] },
    { name: "Peddapalli", tier: "Rural", opTags: ["Agriculture", "Manufacturing", "Healthcare", "Education"] },
    { name: "Nirmal", tier: "Rural", opTags: ["Agriculture", "Healthcare", "Education", "Manufacturing"] },
    { name: "Vikarabad", tier: "Rural", opTags: ["Agriculture", "Food", "Healthcare", "Education"] },
    { name: "Wanaparthy", tier: "Rural", opTags: ["Agriculture", "Healthcare", "Education", "Finance"] },
    { name: "Nagarkurnool", tier: "Rural", opTags: ["Agriculture", "Healthcare", "Education", "Manufacturing"] },
    { name: "Jogulamba Gadwal", tier: "Rural", opTags: ["Agriculture", "Healthcare", "Education", "Finance"] },
    { name: "Bhupalpally", tier: "Rural", opTags: ["Agriculture", "Manufacturing", "Healthcare", "Education"] },
    { name: "Mulugu", tier: "Rural", opTags: ["Agriculture", "Healthcare", "Education", "Manufacturing"] },
    { name: "Narayanpet", tier: "Rural", opTags: ["Agriculture", "Healthcare", "Education", "Finance"] },
    { name: "Other – Telangana", tier: "Rural", opTags: ["Agriculture", "Healthcare", "Education"] },
  ],
  "Andhra Pradesh": [
    { name: "Visakhapatnam", tier: "Metro", opTags: ["Technology", "Healthcare", "Manufacturing", "Finance", "Education"] },
    { name: "Vijayawada (NTR District)", tier: "Tier-1", opTags: ["Technology", "Finance", "Food", "Healthcare", "Education"] },
    { name: "Guntur", tier: "Tier-1", opTags: ["Agriculture", "Food", "Healthcare", "Education", "Finance"] },
    { name: "Tirupati (Tirupati District)", tier: "Tier-2", opTags: ["Education", "Healthcare", "Food", "Technology"] },
    { name: "Kurnool", tier: "Tier-2", opTags: ["Agriculture", "Healthcare", "Education", "Manufacturing"] },
    { name: "East Godavari (Kakinada)", tier: "Tier-2", opTags: ["Agriculture", "Food", "Healthcare", "Manufacturing"] },
    { name: "West Godavari (Eluru)", tier: "Tier-2", opTags: ["Agriculture", "Food", "Healthcare", "Education"] },
    { name: "Krishna (Machilipatnam)", tier: "Tier-2", opTags: ["Agriculture", "Healthcare", "Education", "Manufacturing"] },
    { name: "Nellore (Potti Sriramulu)", tier: "Tier-2", opTags: ["Agriculture", "Healthcare", "Education", "Food"] },
    { name: "Rajahmundry (Konaseema)", tier: "Tier-2", opTags: ["Agriculture", "Food", "Healthcare", "Education"] },
    { name: "Kadapa (YSR District)", tier: "Tier-3", opTags: ["Agriculture", "Healthcare", "Education", "Manufacturing"] },
    { name: "Anantapur", tier: "Tier-3", opTags: ["Agriculture", "Healthcare", "Education", "Manufacturing"] },
    { name: "Chittoor", tier: "Tier-3", opTags: ["Agriculture", "Food", "Healthcare", "Education"] },
    { name: "Prakasam (Ongole)", tier: "Tier-3", opTags: ["Agriculture", "Healthcare", "Education", "Finance"] },
    { name: "Palnadu", tier: "Rural", opTags: ["Agriculture", "Healthcare", "Education", "Manufacturing"] },
    { name: "Bapatla", tier: "Rural", opTags: ["Agriculture", "Food", "Healthcare", "Education"] },
    { name: "Srikakulam", tier: "Rural", opTags: ["Agriculture", "Healthcare", "Education", "Manufacturing"] },
    { name: "Vizianagaram", tier: "Rural", opTags: ["Agriculture", "Healthcare", "Education", "Manufacturing"] },
    { name: "Alluri Sitharama Raju", tier: "Rural", opTags: ["Agriculture", "Healthcare", "Education", "Manufacturing"] },
    { name: "Other – Andhra Pradesh", tier: "Rural", opTags: ["Agriculture", "Healthcare", "Education"] },
  ],
};

const INDIA_STATES_OTHER = [
  "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana",
  "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
  "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
  "Tamil Nadu", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
  "Delhi", "Jammu & Kashmir", "Ladakh", "Puducherry", "Chandigarh",
];

function getDistricts(state) {
  if (DISTRICT_MASTER[state]) return DISTRICT_MASTER[state];
  return [
    { name: `${state} – Major City`, tier: "Metro", opTags: ["Technology", "Finance", "Food", "Healthcare", "Education"] },
    { name: `${state} – District Town`, tier: "Tier-2", opTags: ["Healthcare", "Education", "Manufacturing", "Agriculture"] },
    { name: `${state} – Rural Area`, tier: "Rural", opTags: ["Agriculture", "Healthcare", "Education", "Manufacturing"] },
  ];
}

// Tier base multipliers per sector for district fit scoring
const TIER_BASE = {
  "Metro":  { Technology: 1.4, Finance: 1.3, Food: 1.3, Healthcare: 1.1, Education: 1.1, Agriculture: 0.5, Manufacturing: 0.8, Government: 1.0 },
  "Tier-1": { Technology: 1.2, Finance: 1.1, Food: 1.2, Healthcare: 1.2, Education: 1.2, Agriculture: 0.7, Manufacturing: 1.0, Government: 1.0 },
  "Tier-2": { Technology: 1.0, Finance: 1.0, Food: 1.0, Healthcare: 1.2, Education: 1.2, Agriculture: 1.1, Manufacturing: 1.1, Government: 1.0 },
  "Tier-3": { Technology: 0.8, Finance: 0.9, Food: 0.9, Healthcare: 1.3, Education: 1.3, Agriculture: 1.3, Manufacturing: 1.2, Government: 1.0 },
  "Rural":  { Technology: 0.6, Finance: 0.7, Food: 0.8, Healthcare: 1.4, Education: 1.4, Agriculture: 1.5, Manufacturing: 1.3, Government: 1.0 },
};

// ─── ARCHETYPES ───────────────────────────────────────────────────────────────

const ARCHETYPES = {
  Innovator:  { icon: "💡", color: "#8B5CF6",
    desc: "You challenge the status quo with fresh ideas. Imaginative, experimental, future-focused.",
    founderRole: "Product & Strategy Lead",
    roleDesc: "You define what to build and why. You spot opportunities others miss." },
  Leader:     { icon: "🦁", color: "#EF4444",
    desc: "You drive direction and inspire teams. Decisive, bold, responsibility-driven.",
    founderRole: "CEO / Managing Director",
    roleDesc: "You set direction, own outcomes, and hold the team together." },
  Builder:    { icon: "🏗️", color: "#F59E0B",
    desc: "You love making things work. Practical, dependable, execution-driven.",
    founderRole: "Operations & Delivery Lead",
    roleDesc: "You build systems, manage delivery, and make things run." },
  Analyst:    { icon: "📊", color: "#3B82F6",
    desc: "You break complexity into clarity. Logical, detail-oriented, evidence-driven.",
    founderRole: "Finance & Research Lead",
    roleDesc: "You manage numbers, validate decisions, and reduce risk." },
  Caregiver:  { icon: "❤️", color: "#10B981",
    desc: "You nurture and support others. Empathetic, patient, community-focused.",
    founderRole: "Community & Impact Lead",
    roleDesc: "You build trust, serve customers, and keep the mission human." },
  Explorer:   { icon: "🧭", color: "#F97316",
    desc: "You seek new opportunities. Adaptable, adventurous, open-minded.",
    founderRole: "Business Development Lead",
    roleDesc: "You find markets, forge partnerships, and expand reach." },
  Researcher: { icon: "🔬", color: "#06B6D4",
    desc: "You dig deep to find truth. Curious, methodical, knowledge-hungry.",
    founderRole: "R&D & Quality Lead",
    roleDesc: "You validate ideas, improve quality, and ground decisions in evidence." },
  Influencer: { icon: "🎙️", color: "#EC4899",
    desc: "You inspire and connect people. Persuasive, expressive, people-focused.",
    founderRole: "Marketing & Sales Lead",
    roleDesc: "You tell the story, attract customers, and build the brand." },
};

const ARCHETYPE_WEIGHTS = {
  Innovator:  { Creativity: 3, Curiosity: 2, RiskTaking: 1 },
  Leader:     { Leadership: 3, Communication: 2, RiskTaking: 1 },
  Analyst:    { ProblemSolving: 3, Discipline: 2, Curiosity: 1 },
  Caregiver:  { TeamOrientation: 3, Communication: 2, Discipline: 1 },
  Builder:    { Discipline: 3, ProblemSolving: 2, TeamOrientation: 1 },
  Explorer:   { Curiosity: 3, RiskTaking: 2, Creativity: 1 },
  Researcher: { Curiosity: 3, ProblemSolving: 2, Discipline: 1 },
  Influencer: { Communication: 3, Creativity: 2, Leadership: 1 },
};

function determineArchetype(pScores) {
  const scored = Object.entries(ARCHETYPE_WEIGHTS).map(([arch, weights]) => ({
    arch,
    score: Object.entries(weights).reduce((sum, [dim, w]) => sum + (pScores[dim] || 0) * w, 0),
  }));
  scored.sort((a, b) => b.score - a.score);
  return { primary: scored[0].arch, secondary: scored[1].arch };
}

// ─── IDEA LIBRARY ─────────────────────────────────────────────────────────────

const IDEA_LIBRARY = [
  { id: "IL001", name: "Rural Diagnostic Collection Center",
    sectors: ["Healthcare"], problemTags: ["Healthcare"],
    archetypes: ["Builder", "Analyst"], investRange: [500000, 1500000], investLabel: "₹5–15L",
    collab: ["Operations", "Finance", "Healthcare Specialist"] },
  { id: "IL002", name: "Telemedicine Assistance Center",
    sectors: ["Healthcare", "Technology"], problemTags: ["Healthcare"],
    archetypes: ["Caregiver", "Researcher"], investRange: [200000, 500000], investLabel: "₹2–5L",
    collab: ["Technology", "Healthcare Specialist", "Marketing"] },
  { id: "IL003", name: "Cloud Kitchen",
    sectors: ["Food"], problemTags: ["Employment"],
    archetypes: ["Innovator", "Explorer"], investRange: [100000, 300000], investLabel: "₹1–3L",
    collab: ["Operations", "Marketing", "Finance"] },
  { id: "IL004", name: "Digital Marketing Agency",
    sectors: ["Technology"], problemTags: ["Technology", "Employment"],
    archetypes: ["Influencer", "Innovator"], investRange: [50000, 200000], investLabel: "₹50K–2L",
    collab: ["Technology", "Content", "Sales"] },
  { id: "IL005", name: "Agri Advisory Service",
    sectors: ["Agriculture"], problemTags: ["Agriculture"],
    archetypes: ["Researcher", "Analyst"], investRange: [30000, 100000], investLabel: "₹30K–1L",
    collab: ["Agriculture Expert", "Finance", "Communication"] },
  { id: "IL006", name: "Skill Training Center",
    sectors: ["Education"], problemTags: ["Employment", "Education"],
    archetypes: ["Caregiver", "Leader", "Builder"], investRange: [100000, 500000], investLabel: "₹1–5L",
    collab: ["Education Expert", "Operations", "Finance"] },
  { id: "IL007", name: "District Spice Brand",
    sectors: ["Agriculture", "Food"], problemTags: ["Agriculture", "Employment"],
    archetypes: ["Explorer", "Builder"], investRange: [100000, 400000], investLabel: "₹1–4L",
    collab: ["Branding", "Operations", "Sales"] },
  { id: "IL008", name: "Solar Installation Services",
    sectors: ["Manufacturing", "Technology"], problemTags: ["Technology", "Agriculture"],
    archetypes: ["Builder", "Innovator"], investRange: [200000, 800000], investLabel: "₹2–8L",
    collab: ["Technical", "Sales", "Finance"] },
  { id: "IL009", name: "EdTech Franchise Center",
    sectors: ["Education", "Technology"], problemTags: ["Education", "Employment"],
    archetypes: ["Influencer", "Caregiver"], investRange: [200000, 800000], investLabel: "₹2–8L",
    collab: ["Education Expert", "Technology", "Marketing"] },
  { id: "IL010", name: "Rural Accounting & GST Services",
    sectors: ["Finance"], problemTags: ["FinancialAccess"],
    archetypes: ["Analyst", "Builder"], investRange: [30000, 100000], investLabel: "₹30K–1L",
    collab: ["Finance", "Legal", "Operations"] },
  { id: "IL011", name: "Organic Produce Aggregator",
    sectors: ["Agriculture"], problemTags: ["Agriculture", "Employment"],
    archetypes: ["Explorer", "Leader"], investRange: [100000, 300000], investLabel: "₹1–3L",
    collab: ["Agriculture Expert", "Logistics", "Sales"] },
  { id: "IL012", name: "Micro-Lending Group",
    sectors: ["Finance"], problemTags: ["FinancialAccess", "Employment"],
    archetypes: ["Caregiver", "Leader"], investRange: [50000, 200000], investLabel: "₹50K–2L",
    collab: ["Finance", "Community", "Operations"] },
  { id: "IL013", name: "Competitive Exam Coaching Center",
    sectors: ["Education", "Government"], problemTags: ["Education", "Employment"],
    archetypes: ["Analyst", "Researcher"], investRange: [100000, 400000], investLabel: "₹1–4L",
    collab: ["Education Expert", "Operations", "Marketing"] },
  { id: "IL014", name: "Furniture & Carpentry Unit",
    sectors: ["Manufacturing"], problemTags: ["Employment", "Transport"],
    archetypes: ["Builder", "Explorer"], investRange: [200000, 600000], investLabel: "₹2–6L",
    collab: ["Manufacturing", "Sales", "Design"] },
  { id: "IL015", name: "Community Health & Wellness Studio",
    sectors: ["Healthcare"], problemTags: ["Healthcare"],
    archetypes: ["Caregiver", "Influencer"], investRange: [100000, 300000], investLabel: "₹1–3L",
    collab: ["Healthcare Specialist", "Marketing", "Operations"] },
  { id: "IL016", name: "Water Purification & Distribution",
    sectors: ["Manufacturing", "Healthcare"], problemTags: ["Water", "Healthcare"],
    archetypes: ["Builder", "Researcher"], investRange: [200000, 700000], investLabel: "₹2–7L",
    collab: ["Technical", "Operations", "Finance"] },
  { id: "IL017", name: "Agri-Processing & Packaging Unit",
    sectors: ["Agriculture", "Manufacturing"], problemTags: ["Agriculture", "Employment"],
    archetypes: ["Builder", "Explorer"], investRange: [300000, 1000000], investLabel: "₹3–10L",
    collab: ["Manufacturing", "Agriculture Expert", "Sales"] },
  { id: "IL018", name: "Last-Mile Logistics Service",
    sectors: ["Manufacturing", "Technology"], problemTags: ["Transport", "Employment"],
    archetypes: ["Builder", "Explorer"], investRange: [100000, 400000], investLabel: "₹1–4L",
    collab: ["Logistics", "Technology", "Operations"] },
  { id: "IL019", name: "Community Finance & Savings Group",
    sectors: ["Finance"], problemTags: ["FinancialAccess", "Employment"],
    archetypes: ["Caregiver", "Analyst"], investRange: [30000, 100000], investLabel: "₹30K–1L",
    collab: ["Finance", "Community", "Operations"] },
  { id: "IL020", name: "Rural EdTech Content Studio",
    sectors: ["Education", "Technology"], problemTags: ["Education", "Technology"],
    archetypes: ["Innovator", "Researcher"], investRange: [50000, 200000], investLabel: "₹50K–2L",
    collab: ["Content", "Technology", "Education Expert"] },
];

// Q24 problem → sector boost multipliers
const PROBLEM_SECTOR_BOOST = {
  Healthcare:      { Healthcare: 1.3 },
  Education:       { Education: 1.3 },
  Employment:      { Manufacturing: 1.3, Education: 1.2 },
  Agriculture:     { Agriculture: 1.3, Food: 1.2 },
  Water:           { Manufacturing: 1.2, Healthcare: 1.2 },
  Transport:       { Manufacturing: 1.3, Technology: 1.2 },
  Technology:      { Technology: 1.3 },
  FinancialAccess: { Finance: 1.3 },
};

// Maps assessment sectors → platform opportunity categories
const SECTOR_TO_CATEGORY = {
  Technology: "ai-tech",
  Agriculture: "agri",
  Food: "local-business",
  Healthcare: "local-business",
  Education: "student",
  Finance: "local-business",
  Government: "local-business",
  Manufacturing: "trades",
};

// ─── QUESTION BANK ────────────────────────────────────────────────────────────

const QUESTIONS = [
  // BLOCK A — Personality Core (10 MCQ)
  { id: "A1", block: "A", text: "You have one free weekend and ₹500. You would most likely:", type: "mcq",
    options: [
      { label: "Try building a small app or website idea", p: { Creativity: 3, Discipline: 1 }, s: { Technology: 3 } },
      { label: "Cook something new and sell it to neighbours", p: { Creativity: 3, RiskTaking: 2 }, s: { Food: 3 } },
      { label: "Read or watch something to learn a new skill", p: { Curiosity: 3, Discipline: 2 }, s: { Education: 2 } },
      { label: "Spend time with people and catch up", p: { Communication: 3, TeamOrientation: 2 }, s: {} },
    ] },
  { id: "A2", block: "A", text: "Your college group project has no leader and the deadline is tomorrow. You:", type: "mcq",
    options: [
      { label: "Take charge immediately and assign tasks", p: { Leadership: 4 }, s: {} },
      { label: "Suggest a plan but let someone else lead", p: { Leadership: 2, Communication: 2 }, s: {} },
      { label: "Focus on your own part and do it well", p: { Discipline: 4 }, s: {} },
      { label: "Wait to see what others decide", p: { TeamOrientation: 2 }, s: {} },
    ] },
  { id: "A3", block: "A", text: "A relative offers you ₹50,000. You would most likely:", type: "mcq",
    options: [
      { label: "Start something immediately, even without a full plan", p: { RiskTaking: 4, Creativity: 1 }, s: {} },
      { label: "Research opportunities in your area carefully", p: { RiskTaking: 2, ProblemSolving: 2 }, s: { Agriculture: 2, Manufacturing: 2 } },
      { label: "Put it in a fixed deposit or safe investment", p: { Discipline: 3 }, s: { Finance: 3 } },
      { label: "Use it for further education or a course", p: { Curiosity: 3, Discipline: 1 }, s: { Education: 3 } },
    ] },
  { id: "A4", block: "A", text: "When you encounter a problem you don't understand, you:", type: "mcq",
    options: [
      { label: "Search deeply until you fully understand it", p: { Curiosity: 4, ProblemSolving: 1 }, s: {} },
      { label: "Ask someone experienced for the answer", p: { Communication: 3, TeamOrientation: 1 }, s: { Healthcare: 1 } },
      { label: "Try different approaches until one works", p: { ProblemSolving: 4 }, s: {} },
      { label: "Move on if it's not immediately important", p: { RiskTaking: 1 }, s: {} },
    ] },
  { id: "A5", block: "A", text: "Something at home breaks — a fan, a tap, a phone. You:", type: "mcq",
    options: [
      { label: "Try to fix it yourself first", p: { ProblemSolving: 3, RiskTaking: 1 }, s: { Manufacturing: 2 } },
      { label: "Look up a tutorial and follow it step by step", p: { ProblemSolving: 2, Curiosity: 2 }, s: { Technology: 2 } },
      { label: "Call someone who knows how to fix it", p: { Communication: 3 }, s: {} },
      { label: "Leave it and adjust your routine around it", p: { Discipline: 2 }, s: {} },
    ] },
  { id: "A6", block: "A", text: "A friend is confused about a topic you know well. You:", type: "mcq",
    options: [
      { label: "Explain it clearly with examples until they get it", p: { Communication: 4, Leadership: 1 }, s: { Education: 3 } },
      { label: "Write down the key points for them to read", p: { Communication: 2, Discipline: 2 }, s: { Education: 1 } },
      { label: "Send them a good article or video", p: { Curiosity: 2 }, s: { Technology: 1 } },
      { label: "Tell them the answer directly without explaining", p: { Discipline: 3 }, s: {} },
    ] },
  { id: "A7", block: "A", text: "Your daily routine is best described as:", type: "mcq",
    options: [
      { label: "Planned the night before, followed strictly", p: { Discipline: 4 }, s: { Finance: 2, Government: 2 } },
      { label: "Roughly planned, flexible when needed", p: { Discipline: 2, Leadership: 1 }, s: {} },
      { label: "No fixed plan — I work when I feel motivated", p: { Creativity: 2, RiskTaking: 2 }, s: {} },
      { label: "Depends on what others around me are doing", p: { TeamOrientation: 3 }, s: {} },
    ] },
  { id: "A8", block: "A", text: "You do your best work:", type: "mcq",
    options: [
      { label: "Alone, with full focus and no interruptions", p: { Discipline: 2, ProblemSolving: 1 }, s: {} },
      { label: "In a small team of 2–3 people you trust", p: { TeamOrientation: 3, Leadership: 1 }, s: {} },
      { label: "In a large active group with energy around you", p: { TeamOrientation: 4, Communication: 2 }, s: {} },
      { label: "It genuinely depends on the task", p: { Curiosity: 1, Creativity: 1 }, s: {} },
    ] },
  { id: "A9", block: "A", text: "You are given a blank wall in your town. You:", type: "mcq",
    options: [
      { label: "Design a mural or public art piece", p: { Creativity: 4 }, s: {} },
      { label: "Turn it into a community notice board", p: { Leadership: 2, Communication: 2 }, s: { Education: 1 } },
      { label: "Use it to advertise local businesses", p: { Communication: 3, Creativity: 1 }, s: { Technology: 1 } },
      { label: "Leave it — it's not my responsibility", p: { Discipline: 1 }, s: {} },
    ] },
  { id: "A10", block: "A", text: "Which statement feels most true for you right now?", type: "mcq",
    options: [
      { label: "I want to build something of my own, even if it's risky", p: { RiskTaking: 4, Creativity: 1 }, s: {} },
      { label: "I want a stable career first, then maybe something of my own", p: { Discipline: 3 }, s: { Finance: 2, Government: 2 } },
      { label: "I want to grow within an organisation and lead a team", p: { Leadership: 4 }, s: {} },
      { label: "I'm still figuring out what direction I want to go", p: { Curiosity: 3 }, s: {} },
    ] },

  // BLOCK B — Sector Signal (6 MCQ)
  { id: "B1", block: "B", text: "Your district needs a new service. Which would you most want to start?", type: "mcq",
    options: [
      { label: "An app connecting farmers to buyers directly", p: { Creativity: 1, ProblemSolving: 1 }, s: { Technology: 3, Agriculture: 3 } },
      { label: "A local clinic or health testing centre", p: { Leadership: 1 }, s: { Healthcare: 4 } },
      { label: "A training centre for digital & vocational skills", p: { Communication: 1 }, s: { Education: 4 } },
      { label: "A shop packaging and selling local food products", p: { Creativity: 1, RiskTaking: 1 }, s: { Food: 3, Agriculture: 2 } },
    ] },
  { id: "B2", block: "B", text: "Which of these roles would you find most satisfying?", type: "mcq",
    options: [
      { label: "Helping small businesses manage accounts & loans", p: { ProblemSolving: 1, Discipline: 1 }, s: { Finance: 4 } },
      { label: "Working with a govt. scheme to improve your district", p: { Leadership: 1, Discipline: 1 }, s: { Government: 4 } },
      { label: "Running a small factory or production unit", p: { Leadership: 1, RiskTaking: 1 }, s: { Manufacturing: 4 } },
      { label: "Teaching or coaching people in your community", p: { Communication: 2 }, s: { Education: 4 } },
    ] },
  { id: "B3", block: "B", text: "A new business opens in your town. Which excites you most?", type: "mcq",
    options: [
      { label: "A cloud kitchen delivering food via Swiggy/Zomato", p: { Creativity: 1, RiskTaking: 1 }, s: { Food: 4 } },
      { label: "A telemedicine centre for online doctor consultations", p: { Curiosity: 1 }, s: { Healthcare: 4 } },
      { label: "A coaching centre for competitive exams", p: { Discipline: 1 }, s: { Education: 3, Government: 1 } },
      { label: "A digital marketing agency for local shops", p: { Creativity: 2 }, s: { Technology: 4 } },
    ] },
  { id: "B4", block: "B", text: "Which entrepreneur story inspires you most?", type: "mcq",
    options: [
      { label: "A farmer who built a brand from local spices and exports", p: { Creativity: 1, RiskTaking: 1 }, s: { Agriculture: 4 } },
      { label: "A person who set up a small furniture manufacturing unit", p: { ProblemSolving: 1 }, s: { Manufacturing: 4 } },
      { label: "Someone running a micro-lending group for village women", p: { Leadership: 1, Communication: 1 }, s: { Finance: 3, Healthcare: 1 } },
      { label: "A young person running an online tutoring platform", p: { Creativity: 1, Curiosity: 1 }, s: { Technology: 2, Education: 3 } },
    ] },
  { id: "B5", block: "B", text: "If you had to spend 6 months mastering one area, which would you choose?", type: "mcq",
    options: [
      { label: "Building and growing a website or mobile app", p: { Curiosity: 2, ProblemSolving: 1 }, s: { Technology: 4 } },
      { label: "Preparing for UPSC, banking, or a govt. exam", p: { Discipline: 2 }, s: { Government: 4 } },
      { label: "Learning how to run a profitable small business", p: { RiskTaking: 2, Leadership: 1 }, s: { Finance: 2, Manufacturing: 1 } },
      { label: "Becoming an expert in a healthcare or wellness skill", p: { Curiosity: 1, Discipline: 1 }, s: { Healthcare: 4 } },
    ] },
  { id: "B6", block: "B", text: "Which single sentence describes your ambition best?", type: "mcq",
    options: [
      { label: "I want to solve a real problem in my district using technology", p: { ProblemSolving: 2, Curiosity: 1 }, s: { Technology: 4 } },
      { label: "I want to create jobs in my community through a business", p: { Leadership: 2, RiskTaking: 1 }, s: { Manufacturing: 2, Agriculture: 2, Food: 2 } },
      { label: "I want to serve people through healthcare or education", p: { Communication: 2 }, s: { Healthcare: 3, Education: 3 } },
      { label: "I want financial security and a respected career", p: { Discipline: 2 }, s: { Finance: 3, Government: 3 } },
    ] },

  // BLOCK C — Execution Style (4 Likert)
  { id: "C1", block: "C", text: "I am ready to start something even if I don't have all the answers yet.", type: "likert", dimension: "entrepreneurship" },
  { id: "C2", block: "C", text: "I would rather build something with a team than do it alone.", type: "likert", dimension: "collaboration" },
  { id: "C3", block: "C", text: "I recover quickly when things don't go as planned.", type: "likert", dimension: "resilience" },
  { id: "C4", block: "C", text: "I am willing to work on something for 2–3 years before seeing results.", type: "likert", dimension: "commitment" },

  // BLOCK C — Context (Q21–Q24)
  { id: "C5", block: "C", text: "Which district are you from?", type: "district" },
  { id: "C6", block: "C", text: "What is your current stage?", type: "mcq", profileKey: "education",
    options: [
      { label: "Intermediate (11th / 12th)", p: {}, s: {} },
      { label: "Undergraduate Degree", p: {}, s: {} },
      { label: "Engineering / Polytechnic", p: {}, s: {} },
      { label: "Postgraduate / MBA", p: {}, s: {} },
      { label: "Working Professional", p: {}, s: {} },
    ] },
  { id: "C7", block: "C", text: "How much can you realistically invest to start something?", type: "mcq", profileKey: "budget",
    options: [
      { label: "Under ₹50,000", budgetMax: 50000, p: {}, s: {} },
      { label: "₹50,000 – ₹2 Lakhs", budgetMax: 200000, p: {}, s: {} },
      { label: "₹2 Lakhs – ₹10 Lakhs", budgetMax: 1000000, p: {}, s: {} },
      { label: "Above ₹10 Lakhs", budgetMax: Infinity, p: {}, s: {} },
    ] },
  { id: "C8", block: "C", text: "What problem bothers you most in your community?", type: "mcq", profileKey: "problem",
    options: [
      { label: "Healthcare — people lack access to doctors or medicine", problem: "Healthcare", p: {}, s: {} },
      { label: "Education — quality education is hard to access here", problem: "Education", p: {}, s: {} },
      { label: "Employment — not enough good jobs for local youth", problem: "Employment", p: {}, s: {} },
      { label: "Agriculture — farmers face poor prices or lack of support", problem: "Agriculture", p: {}, s: {} },
      { label: "Water — clean or affordable water is a real challenge", problem: "Water", p: {}, s: {} },
      { label: "Transport — connectivity is poor for people or goods", problem: "Transport", p: {}, s: {} },
      { label: "Technology — digital access and skills are still limited", problem: "Technology", p: {}, s: {} },
      { label: "Financial Access — people struggle to get loans or save safely", problem: "FinancialAccess", p: {}, s: {} },
    ] },
];

const BUDGET_MAXES = [50000, 200000, 1000000, Infinity];

// ─── SCORE CALCULATORS ────────────────────────────────────────────────────────

function computeDimMax(qs, type) {
  const sums = {};
  qs.forEach(q => {
    if (q.type !== "mcq") return;
    const maxPerQ = {};
    q.options.forEach(opt => {
      Object.entries((type === "p" ? opt.p : opt.s) || {}).forEach(([k, v]) => {
        maxPerQ[k] = Math.max(maxPerQ[k] || 0, v);
      });
    });
    Object.entries(maxPerQ).forEach(([k, v]) => { sums[k] = (sums[k] || 0) + v; });
  });
  return sums;
}
const P_MAX = computeDimMax(QUESTIONS, "p");
const S_MAX = computeDimMax(QUESTIONS, "s");

function calcScores(answers) {
  const pRaw = { Creativity: 0, Leadership: 0, RiskTaking: 0, Communication: 0, Discipline: 0, Curiosity: 0, TeamOrientation: 0, ProblemSolving: 0 };
  const sRaw = { Technology: 0, Agriculture: 0, Healthcare: 0, Education: 0, Food: 0, Finance: 0, Government: 0, Manufacturing: 0 };
  const cDims = { entrepreneurship: 0, collaboration: 0, resilience: 0, commitment: 0 };
  QUESTIONS.forEach(q => {
    const ans = answers[q.id];
    if (ans == null) return;
    if (q.type === "mcq" && !q.profileKey) {
      const opt = q.options[ans];
      Object.entries(opt.p || {}).forEach(([k, v]) => { if (k in pRaw) pRaw[k] += v; });
      Object.entries(opt.s || {}).forEach(([k, v]) => { if (k in sRaw) sRaw[k] += v; });
    } else if (q.type === "likert") {
      cDims[q.dimension] = ans;
    }
  });
  const pScores = {};
  Object.keys(pRaw).forEach(k => { pScores[k] = P_MAX[k] ? Math.round(Math.min(100, (pRaw[k] / P_MAX[k]) * 100)) : 50; });
  const sectorScores = {};
  Object.keys(sRaw).forEach(k => { sectorScores[k] = S_MAX[k] ? Math.round(Math.min(100, (sRaw[k] / S_MAX[k]) * 100)) : 0; });
  const epScore = Math.round(
    (pScores.RiskTaking * 0.25) + (pScores.Leadership * 0.20) + (pScores.Creativity * 0.20) +
    (pScores.ProblemSolving * 0.15) + (((cDims.entrepreneurship + cDims.commitment) / 2) / 5 * 100) * 0.20
  );
  return { pScores, sectorScores, cDims, epScore };
}

// ─── RECOMMENDATION ENGINE ────────────────────────────────────────────────────
// Weights: District Fit 35% | Sector Interest 35% | Archetype 15% | Budget pass/fail 15%

function scoreIdeas(archetype, secondaryArchetype, sectorScores, epScore, commitmentScore, districtOpTags, tier, budgetMax, problemKey) {
  const tierMod = TIER_BASE[tier] || TIER_BASE["Tier-2"];
  const probBoost = PROBLEM_SECTOR_BOOST[problemKey] || {};

  return IDEA_LIBRARY.map(idea => {
    // Budget hard filter
    if (idea.investRange[0] > budgetMax) return { ...idea, matchPct: 0, filtered: true };

    // District Fit (35%)
    const districtHits = idea.sectors.filter(s => districtOpTags.includes(s)).length;
    const districtBase = districtHits > 0 ? Math.round((districtHits / idea.sectors.length) * 100) : 20;
    const tierAvg = idea.sectors.reduce((sum, s) => sum + (tierMod[s] || 1.0), 0) / idea.sectors.length;
    const districtFit = Math.min(100, Math.round(districtBase * tierAvg));

    // Sector Interest (35%) with problem boost
    const rawSector = idea.sectors.reduce((sum, s) => sum + (sectorScores[s] || 0), 0) / idea.sectors.length;
    const boostFactor = idea.sectors.reduce((max, s) => Math.max(max, probBoost[s] || 1.0), 1.0);
    const sectorFit = Math.min(100, Math.round(rawSector * boostFactor));

    // Archetype (15%) — primary=100, secondary=40, none=0
    const archetypeFit = idea.archetypes.includes(archetype) ? 100
      : idea.archetypes.includes(secondaryArchetype) ? 40 : 0;

    // Composite
    let composite = (districtFit * 0.35) + (sectorFit * 0.35) + (archetypeFit * 0.15);
    if (epScore >= 71) composite += 5;
    else if (epScore >= 41) composite += 2;
    if (commitmentScore <= 2) composite -= 10;

    return { ...idea, matchPct: Math.min(98, Math.max(15, Math.round(composite))), filtered: false };
  })
  .filter(i => !i.filtered)
  .sort((a, b) => b.matchPct - a.matchPct)
  .slice(0, 5);
}

const CAREER_MAP = {
  Innovator:  ["Product Manager", "Startup Founder", "UX Designer", "Software Engineer", "Creative Director"],
  Leader:     ["Civil Services Officer", "Business Manager", "Entrepreneur", "Corporate Director", "Political Strategist"],
  Analyst:    ["Data Analyst", "Chartered Accountant", "Research Scientist", "Statistician", "Business Analyst"],
  Caregiver:  ["Doctor / Nurse", "Counsellor", "Social Worker", "NGO Leader", "Teacher"],
  Builder:    ["Civil Engineer", "Project Manager", "Operations Manager", "Manufacturing Head", "Logistics Manager"],
  Explorer:   ["Journalist", "Travel Consultant", "Event Manager", "Geographer", "Adventure Entrepreneur"],
  Researcher: ["Scientist", "Policy Analyst", "Medical Researcher", "PhD Academic", "Forensic Analyst"],
  Influencer: ["Marketing Manager", "Social Media Strategist", "PR Specialist", "Content Creator", "Brand Consultant"],
};
const COURSE_MAP = {
  Technology:   ["B.Tech CSE", "BCA", "B.Sc Data Science", "Diploma in IT", "B.Sc AI & ML"],
  Agriculture:  ["B.Sc Agriculture", "B.Tech Agri Engg", "Diploma Rural Dev", "B.Sc Horticulture", "Agri MBA"],
  Healthcare:   ["MBBS", "B.Pharmacy", "Nursing (B.Sc)", "Allied Health Sciences", "B.Sc Microbiology"],
  Education:    ["B.Ed", "D.El.Ed", "M.Ed", "BA Education", "Diploma Teacher Training"],
  Government:   ["BA Political Science", "B.Com (for banking)", "LLB", "Public Administration", "Defence B.Tech"],
  Finance:      ["B.Com Hons", "CA", "CFA Foundation", "BBA Finance", "B.Sc Statistics"],
  Food:         ["Hotel Management", "B.Sc Food Technology", "Culinary Arts Diploma", "Food Business Mgmt", "FSSAI Certification"],
  Manufacturing:["B.Tech Mechanical", "ITI Trade Certificate", "Diploma Production Engg", "Quality Management", "B.Tech Industrial"],
};
const EDU_FILTER = {
  0: c => c, 1: c => c, 2: c => c,
  3: c => c.filter(x => !x.startsWith("B.") && !x.startsWith("Diploma")),
  4: c => c.filter(x => x.includes("MBA") || x.includes("CA") || x.includes("CFA") || x.includes("M.")),
};

function getRecommendations(archetype, secondaryArchetype, sectorScores, epScore, cDims, districtOpTags, tier, budgetMax, educationIdx, problemKey) {
  const careers = (CAREER_MAP[archetype] || CAREER_MAP.Innovator).map((name, i) => ({ name, match: Math.max(60, 95 - i * 5) }));
  const topSectors = Object.entries(sectorScores).sort((a, b) => b[1] - a[1]).slice(0, 2).map(([k]) => k);
  const raw = [...new Set([...(COURSE_MAP[topSectors[0]] || []), ...(COURSE_MAP[topSectors[1]] || [])])];
  const filterFn = EDU_FILTER[educationIdx] || EDU_FILTER[0];
  const filtered = filterFn(raw);
  const courses = (filtered.length >= 3 ? filtered : raw).slice(0, 5).map((name, i) => ({ name, match: Math.max(60, 92 - i * 5) }));
  const ideas = scoreIdeas(archetype, secondaryArchetype, sectorScores, epScore, cDims.commitment, districtOpTags, tier, budgetMax, problemKey);
  return { careers, courses, ideas };
}

// Builds a prefilled /opportunities/new link for an idea + profile
function buildOpportunityLink(idea, profile) {
  const arch = ARCHETYPES[profile.archetype];
  const params = new URLSearchParams({
    title: `Looking for co-founders: ${idea.name}`,
    description: `I took the ValueWeave "Discover Yourself" assessment and "${idea.name}" matched my profile at ${idea.matchPct}%.\n\nMy archetype is ${profile.archetype} — I'd take the ${arch.founderRole} role. Planned investment: ${idea.investLabel}.\n\nLooking for collaborators in: ${idea.collab.join(", ")}.`,
    category: SECTOR_TO_CATEGORY[idea.sectors[0]] || "local-business",
    location: profile.district && profile.district !== "Unknown" ? `${profile.district}, ${profile.state}` : "",
    skills: idea.collab.join(", "),
    collab: "cofounder",
  });
  return `/opportunities/new?${params.toString()}`;
}

// ─── UI COMPONENTS ────────────────────────────────────────────────────────────

function TopBar() {
  return (
    <nav className="fixed top-0 inset-x-0 z-50 bg-cream/85 backdrop-blur-md border-b border-stone-200/60">
      <div className="max-w-6xl mx-auto h-16 px-4 sm:px-6 flex items-center justify-between gap-3">
        <Link href="/" className="flex items-center gap-2.5 min-h-[44px]">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500 to-yellow-400 flex items-center justify-center shadow-md shadow-amber-500/30">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 3L4 7.5V16.5L12 21L20 16.5V7.5L12 3Z" stroke="#fff" strokeWidth="2" strokeLinejoin="round"/><path d="M4 7.5L12 12M12 12L20 7.5M12 12V21" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>
          </div>
          <span className="font-display font-extrabold text-lg tracking-tight">Value<span className="text-amber-500">Weave</span></span>
        </Link>
        <span className="chip bg-teal-100 text-teal-700">🧭 Discover Yourself</span>
      </div>
    </nav>
  );
}

function ProgressHeader({ qIndex, total, block, onBack }) {
  const pct = Math.round((qIndex / total) * 100);
  const meta = { A: { label: "Personality", color: "#8B5CF6" }, B: { label: "Sector Fit", color: "#F59E0B" }, C: { label: "Your Context", color: "#0D9488" } };
  const { label, color } = meta[block] || meta.A;
  return (
    <div className="bg-cream/90 backdrop-blur-md border-b border-stone-200 px-4 py-3 sticky top-16 z-10">
      <div className="flex items-center gap-3 max-w-xl mx-auto">
        <button onClick={onBack} aria-label="Back" className="text-muted hover:text-ink text-lg w-8 transition-colors">←</button>
        <div className="flex-1">
          <div className="flex justify-between text-xs mb-1.5 font-display font-semibold">
            <span className="text-muted">{label} · Q{qIndex + 1} of {total}</span>
            <span style={{ color }}>{pct}%</span>
          </div>
          <div className="h-1.5 bg-stone-200 rounded-full overflow-hidden">
            <div className="h-full rounded-full transition-all duration-500"
              style={{ width: `${pct}%`, background: `linear-gradient(90deg,${color}88,${color})` }} />
          </div>
        </div>
      </div>
    </div>
  );
}

function MCQInput({ options, value, onChange }) {
  return (
    <div className="flex flex-col gap-2 mt-5">
      {options.map((opt, i) => (
        <button key={i} onClick={() => onChange(i)}
          className={`text-left px-4 py-3 rounded-xl border-2 text-sm font-medium transition-all duration-200 ${
            value === i
              ? "border-amber-500 bg-amber-50 text-amber-700 translate-x-1"
              : "border-stone-200 bg-white text-muted hover:border-amber-300 hover:text-ink"
          }`}>
          <span className="text-stone-400 mr-2.5 font-display font-bold text-xs">{String.fromCharCode(65 + i)}.</span>
          {opt.label}
        </button>
      ))}
    </div>
  );
}

function LikertInput({ value, onChange }) {
  const labels = ["Strongly\nDisagree", "Disagree", "Neutral", "Agree", "Strongly\nAgree"];
  return (
    <div className="flex gap-2 mt-5">
      {[1, 2, 3, 4, 5].map(v => (
        <button key={v} onClick={() => onChange(v)}
          className={`flex-1 py-3 rounded-xl border-2 flex flex-col items-center gap-1 transition-all duration-200 ${
            value === v
              ? "border-teal-500 bg-teal-50 -translate-y-0.5 shadow-md shadow-teal-500/10"
              : "border-stone-200 bg-white hover:border-teal-300"
          }`}>
          <span className={`text-lg font-bold font-display ${value === v ? "text-teal-600" : "text-stone-400"}`}>{v}</span>
          <span className={`text-center leading-tight whitespace-pre-line ${value === v ? "text-teal-600" : "text-stone-400"}`}
            style={{ fontSize: 9 }}>{labels[v - 1]}</span>
        </button>
      ))}
    </div>
  );
}

const TIER_COLORS = {
  "Metro":  "text-violet-700 bg-violet-100",
  "Tier-1": "text-blue-700 bg-blue-100",
  "Tier-2": "text-amber-700 bg-amber-100",
  "Tier-3": "text-orange-700 bg-orange-100",
  "Rural":  "text-emerald-700 bg-emerald-100",
};

function DistrictInput({ value, onChange }) {
  const [selState, setSelState] = useState(value?.state || "");
  const districts = selState ? getDistricts(selState) : [];
  function handleState(s) { setSelState(s); onChange(null); }
  function handleDistrict(d) { onChange({ state: selState, district: d.name, tier: d.tier, opTags: d.opTags }); }
  return (
    <div className="mt-5 flex flex-col gap-3">
      <div>
        <label className="label-display">State / UT</label>
        <select value={selState} onChange={e => handleState(e.target.value)} className="input-field">
          <option value="">Select your state…</option>
          <optgroup label="— Featured —">
            <option value="Telangana">Telangana</option>
            <option value="Andhra Pradesh">Andhra Pradesh</option>
          </optgroup>
          <optgroup label="— All States & UTs —">
            {INDIA_STATES_OTHER.map(s => <option key={s} value={s}>{s}</option>)}
          </optgroup>
        </select>
      </div>
      {selState && (
        <div>
          <label className="label-display">District</label>
          <div className="flex flex-col gap-2 max-h-56 overflow-y-auto pr-1">
            {districts.map(d => (
              <button key={d.name} onClick={() => handleDistrict(d)}
                className={`text-left px-4 py-2.5 rounded-xl border-2 text-sm font-medium transition-all duration-200 flex items-center justify-between ${
                  value?.district === d.name
                    ? "border-amber-500 bg-amber-50 text-amber-700"
                    : "border-stone-200 bg-white text-muted hover:border-amber-300"
                }`}>
                {d.name}
                <span className={`text-xs font-display font-semibold px-2 py-0.5 rounded-full ${TIER_COLORS[d.tier] || "text-stone-500 bg-stone-100"}`}>{d.tier}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ScoreBar({ label, value, color }) {
  return (
    <div className="mb-3">
      <div className="flex justify-between mb-1">
        <span className="text-muted text-xs">{label.replace(/([A-Z])/g, " $1").trim()}</span>
        <span className="text-xs font-display font-bold" style={{ color }}>{value}</span>
      </div>
      <div className="h-1.5 bg-stone-200 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-1000"
          style={{ width: `${value}%`, background: `linear-gradient(90deg,${color}55,${color})` }} />
      </div>
    </div>
  );
}

function EpRing({ score }) {
  const r = 52, cx = 64, cy = 64, sw = 8, circ = 2 * Math.PI * r, offset = circ - (score / 100) * circ;
  const cls = score >= 71 ? { label: "HIGH", color: "#0D9488" } : score >= 41 ? { label: "MODERATE", color: "#F97316" } : { label: "LOW", color: "#78716C" };
  return (
    <div className="flex flex-col items-center">
      <svg width={128} height={128}>
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#E7E5E4" strokeWidth={sw}/>
        <circle cx={cx} cy={cy} r={r} fill="none" stroke={cls.color} strokeWidth={sw}
          strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round"
          transform={`rotate(-90 ${cx} ${cy})`} style={{ transition: "stroke-dashoffset 1.2s ease" }}/>
        <text x={cx} y={cy - 8} textAnchor="middle" fill="#1C1917" fontSize={26} fontWeight={700}>{score}</text>
        <text x={cx} y={cy + 14} textAnchor="middle" fill={cls.color} fontSize={11} fontWeight={700}>{cls.label}</text>
      </svg>
      <span className="text-muted text-xs mt-1">Entrepreneurship Score</span>
    </div>
  );
}

// ─── MAIN PAGE ────────────────────────────────────────────────────────────────

export default function DiscoverYourselfPage() {
  const [screen, setScreen] = useState("welcome");
  const [qIndex, setQIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [profile, setProfile] = useState(null);
  const [activeTab, setActiveTab] = useState("ideas");

  const currentQ = QUESTIONS[qIndex];
  const totalQ = QUESTIONS.length;
  const currentAnswer = answers[currentQ?.id];
  const isAnswered = currentQ?.type === "district" ? currentAnswer?.district != null : currentAnswer != null;

  function handleAnswer(val) { setAnswers(prev => ({ ...prev, [currentQ.id]: val })); }

  function handleNext() {
    if (!isAnswered) return;
    if (qIndex < totalQ - 1) { setQIndex(qIndex + 1); return; }
    finish();
  }
  function handleBack() {
    if (qIndex > 0) { setQIndex(qIndex - 1); return; }
    setScreen("welcome");
  }
  function finish() {
    const { pScores, sectorScores, cDims, epScore } = calcScores(answers);
    const { primary, secondary } = determineArchetype(pScores);
    const distData = answers["C5"] || { state: "Unknown", district: "Unknown", tier: "Tier-2", opTags: [] };
    const budgetMax = answers["C7"] != null ? BUDGET_MAXES[answers["C7"]] : Infinity;
    const educationIdx = answers["C6"] ?? 0;
    const problemKey = answers["C8"] != null ? QUESTIONS.find(q => q.id === "C8").options[answers["C8"]].problem : null;
    const { careers, courses, ideas } = getRecommendations(
      primary, secondary, sectorScores, epScore, cDims,
      distData.opTags || [], distData.tier, budgetMax, educationIdx, problemKey
    );
    setProfile({
      archetype: primary, secondaryArchetype: secondary,
      pScores, sectorScores, cDims, epScore,
      careers, courses, ideas,
      state: distData.state, district: distData.district, tier: distData.tier,
      budgetLabel: answers["C7"] != null ? QUESTIONS.find(q => q.id === "C7").options[answers["C7"]].label : "—",
      educationLabel: answers["C6"] != null ? QUESTIONS.find(q => q.id === "C6").options[answers["C6"]].label : "—",
      problemLabel: answers["C8"] != null ? QUESTIONS.find(q => q.id === "C8").options[answers["C8"]].label : "—",
    });
    setScreen("results"); setActiveTab("ideas");
  }
  function reset() { setScreen("welcome"); setQIndex(0); setAnswers({}); setProfile(null); }

  // ── WELCOME ──────────────────────────────────────────────────────────────
  if (screen === "welcome") return (
    <div className="min-h-screen bg-cream font-body">
      <TopBar />
      <div className="min-h-screen flex flex-col items-center justify-center px-4 py-24">
        <div className="w-full max-w-sm text-center animate-fadeUp">
          <div className="text-6xl mb-4">🧭</div>
          <span className="chip bg-teal-100 text-teal-700 mb-4">POWERED BY VALUEWEAVE</span>
          <h1 className="h-hero mb-3">
            Discover<br />
            <span className="bg-gradient-to-r from-amber-500 via-yellow-400 to-teal-500 bg-clip-text text-transparent">Yourself</span>
          </h1>
          <p className="text-muted text-sm leading-relaxed mb-8">
            24 questions. Find your archetype, your founder role, and the right business idea for your district.
          </p>
          <div className="grid grid-cols-4 gap-2 mb-8">
            {[["🧠", "10 Q", "Personality"], ["💡", "6 Q", "Sector"], ["⚡", "4 Q", "Style"], ["📍", "4 Q", "Context"]].map(([icon, sub, label]) => (
              <div key={label} className="card-base p-3">
                <div className="text-xl mb-1">{icon}</div>
                <div className="text-amber-600 font-display font-bold text-xs">{sub}</div>
                <div className="text-muted text-xs font-semibold mt-0.5">{label}</div>
              </div>
            ))}
          </div>
          <button onClick={() => setScreen("assessment")} data-testid="discover-begin" className="btn-primary w-full !py-4 text-base">
            Begin →
          </button>
          <p className="text-stone-400 text-xs mt-4">~7 min · Designed for Indian students & builders</p>
        </div>
      </div>
    </div>
  );

  // ── ASSESSMENT ───────────────────────────────────────────────────────────
  if (screen === "assessment") return (
    <div className="min-h-screen bg-cream font-body flex flex-col">
      <TopBar />
      <div className="pt-16">
        <ProgressHeader qIndex={qIndex} total={totalQ} block={currentQ.block} onBack={handleBack}/>
      </div>
      <div className="flex-1 flex flex-col max-w-xl mx-auto w-full px-4 py-6 animate-fadeUp" key={currentQ.id}>
        <p className="text-ink text-base leading-relaxed font-display font-semibold">{currentQ.text}</p>
        {currentQ.type === "mcq" && <MCQInput options={currentQ.options} value={currentAnswer} onChange={handleAnswer}/>}
        {currentQ.type === "likert" && <LikertInput value={currentAnswer} onChange={handleAnswer}/>}
        {currentQ.type === "district" && <DistrictInput value={currentAnswer} onChange={handleAnswer}/>}
        <div className="mt-auto pt-8 pb-6">
          <button onClick={handleNext} disabled={!isAnswered}
            className={`w-full py-4 rounded-full font-display font-bold text-base transition-all duration-200 ${
              isAnswered
                ? "bg-amber-500 hover:bg-amber-600 text-white shadow-md shadow-amber-500/20 hover:-translate-y-0.5"
                : "bg-stone-200 text-stone-400 cursor-not-allowed"
            }`}>
            {qIndex === totalQ - 1 ? "See My Results 🎯" : "Next →"}
          </button>
        </div>
      </div>
    </div>
  );

  // ── RESULTS ──────────────────────────────────────────────────────────────
  if (screen === "results" && profile) {
    const arch = ARCHETYPES[profile.archetype];
    const sArch = ARCHETYPES[profile.secondaryArchetype];
    const tabs = [
      { id: "ideas", label: "Ideas", icon: "🚀" },
      { id: "network", label: "Network", icon: "🤝" },
      { id: "summary", label: "Profile", icon: "🎯" },
      { id: "careers", label: "Careers", icon: "💼" },
      { id: "courses", label: "Courses", icon: "🎓" },
    ];
    const epLabel = profile.epScore >= 71 ? "You're built to build. Start with the ideas below."
      : profile.epScore >= 41 ? "You have what it takes. The right idea and team will unlock you."
      : "Build your skills first — the right opportunity will become clear.";

    return (
      <div className="min-h-screen bg-cream font-body">
        <TopBar />

        {/* Hero */}
        <div className="px-4 pt-24 pb-5 border-b border-stone-200"
          style={{ background: `linear-gradient(160deg,#FFFBF5,${arch.color}14)` }}>
          <div className="max-w-xl mx-auto">
            <span className="chip bg-amber-100 text-amber-700 mb-4">🧭 DISCOVER YOURSELF · VALUEWEAVE</span>
            <div className="flex items-start gap-4 mb-3">
              <div className="text-5xl">{arch.icon}</div>
              <div>
                <p className="text-xs font-display font-bold mb-1" style={{ color: arch.color }}>YOUR ARCHETYPE</p>
                <h2 className="text-2xl font-display font-extrabold text-ink">{profile.archetype}</h2>
                <p className="text-xs text-muted mt-1">
                  <span style={{ color: sArch.color }}>{sArch.icon} {profile.secondaryArchetype}</span> secondary
                </p>
              </div>
            </div>
            {/* Founder role — prominent */}
            <div className="rounded-xl px-4 py-3 mb-3 border bg-white"
              style={{ borderColor: `${arch.color}55` }}>
              <p className="text-xs font-display font-bold mb-0.5" style={{ color: arch.color }}>YOUR FOUNDER ROLE</p>
              <p className="text-ink font-display font-bold text-sm">{arch.founderRole}</p>
              <p className="text-muted text-xs mt-0.5">{arch.roleDesc}</p>
            </div>
            <p className="text-muted text-sm leading-relaxed mb-3">{arch.desc}</p>
            {/* Context pills */}
            <div className="flex flex-wrap gap-2">
              {profile.district && profile.district !== "Unknown" && (
                <span className="chip bg-white border border-stone-200 text-ink">📍 {profile.district}, {profile.state}</span>
              )}
              <span className="chip bg-white border border-stone-200 text-ink">🎓 {profile.educationLabel}</span>
              <span className="chip bg-amber-100 text-amber-700">💰 {profile.budgetLabel}</span>
              {profile.problemLabel && profile.problemLabel !== "—" && (
                <span className="chip bg-teal-100 text-teal-700">🎯 {profile.problemLabel.split("—")[0].trim()}</span>
              )}
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-cream/90 backdrop-blur-md border-b border-stone-200 sticky top-16 z-10">
          <div className="max-w-xl mx-auto flex">
            {tabs.map(t => (
              <button key={t.id} onClick={() => setActiveTab(t.id)}
                className={`flex-1 py-3 flex flex-col items-center gap-0.5 text-xs font-display font-bold border-b-2 transition-all duration-200 ${
                  activeTab === t.id ? "border-amber-500 text-amber-600" : "border-transparent text-stone-400 hover:text-muted"
                }`}>
                <span className="text-base">{t.icon}</span>{t.label}
              </button>
            ))}
          </div>
        </div>

        <div className="max-w-xl mx-auto px-4 py-5 pb-16 animate-fadeUp">

          {/* IDEAS */}
          {activeTab === "ideas" && (
            <div className="flex flex-col gap-4">
              <p className="text-muted text-sm">
                Matched to <span className="text-amber-600 font-semibold">{profile.district}</span> · your sector interests · your budget:
              </p>
              {profile.ideas.length === 0 && (
                <div className="card-base p-6 text-center">
                  <p className="text-muted text-sm">No ideas match your current budget. Consider exploring the full Idea Library or increasing your investment range.</p>
                </div>
              )}
              {profile.ideas.map(idea => (
                <div key={idea.id} className="card-base p-4 hover:shadow-md transition-all">
                  {/* Founder role at top of each card */}
                  <div className="flex items-center justify-between mb-3 pb-3 border-b border-stone-100">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-lg flex items-center justify-center text-sm"
                        style={{ background: `${arch.color}22` }}>
                        {arch.icon}
                      </div>
                      <div>
                        <p className="text-xs font-display font-bold" style={{ color: arch.color }}>YOUR ROLE</p>
                        <p className="text-xs font-bold text-ink">{arch.founderRole}</p>
                      </div>
                    </div>
                    <span className="chip bg-teal-100 text-teal-700 font-display font-bold">{idea.matchPct}% match</span>
                  </div>
                  <p className="text-xs font-display font-bold text-teal-600 mb-1">BUSINESS IDEA</p>
                  <p className="text-ink font-display font-bold text-sm mb-2">{idea.name}</p>
                  <div className="flex flex-wrap gap-1 mb-3">
                    {idea.collab.map(c => (
                      <span key={c} className="text-xs px-2 py-0.5 rounded-full bg-stone-100 text-muted">{c}</span>
                    ))}
                  </div>
                  <div className="flex items-center justify-between pt-3 border-t border-stone-100">
                    <span className="text-amber-600 text-xs font-display font-bold">💰 {idea.investLabel}</span>
                    <Link href={buildOpportunityLink(idea, profile)}
                      className="text-xs font-display font-bold px-3.5 py-2 rounded-full bg-teal-500 hover:bg-teal-600 text-white hover:-translate-y-0.5 transition-all duration-200">
                      Create Opportunity →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* NETWORK — live marketplace matches */}
          {activeTab === "network" && <LiveMatches profile={profile} />}

          {/* PROFILE */}
          {activeTab === "summary" && (
            <div className="flex flex-col gap-4">
              <div className="card-base p-4 flex items-center gap-4">
                <EpRing score={profile.epScore}/>
                <p className="text-muted text-sm leading-relaxed flex-1">{epLabel}</p>
              </div>
              <div className="card-base p-4">
                <p className="text-xs font-display font-bold text-amber-600 mb-4">🧠 PERSONALITY DIMENSIONS</p>
                {Object.entries(profile.pScores).map(([k, v]) => <ScoreBar key={k} label={k} value={v} color="#F97316"/>)}
              </div>
              <div className="card-base p-4">
                <p className="text-xs font-display font-bold text-teal-600 mb-4">💡 SECTOR INTERESTS</p>
                {Object.entries(profile.sectorScores).sort((a, b) => b[1] - a[1]).map(([k, v]) => <ScoreBar key={k} label={k} value={v} color="#0D9488"/>)}
              </div>
              <div className="card-base p-4">
                <p className="text-xs font-display font-bold text-emerald-600 mb-4">⚡ WORKING STYLE</p>
                {[
                  { label: "Entrepreneurship Readiness", val: profile.cDims.entrepreneurship },
                  { label: "Collaboration", val: profile.cDims.collaboration },
                  { label: "Resilience", val: profile.cDims.resilience },
                  { label: "Long-term Commitment", val: profile.cDims.commitment },
                ].map(({ label, val }) => (
                  <div key={label} className="flex items-center justify-between mb-3">
                    <span className="text-muted text-xs">{label}</span>
                    <div className="flex gap-1">
                      {[1, 2, 3, 4, 5].map(n => (
                        <div key={n} className="w-5 h-5 rounded-md" style={{ background: n <= val ? "#0D9488" : "#E7E5E4" }}/>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* CAREERS */}
          {activeTab === "careers" && (
            <div className="flex flex-col gap-3">
              <p className="text-muted text-sm">Career paths suited to your <span style={{ color: arch.color }} className="font-bold">{profile.archetype}</span> archetype:</p>
              {profile.careers.map((c, i) => (
                <div key={i} className="card-base p-4">
                  <p className="text-xs font-display font-bold text-violet-600 mb-2">CAREER MATCH</p>
                  <p className="text-ink font-display font-bold text-sm mb-3">{c.name}</p>
                  <div className="flex items-center gap-3">
                    <div className="h-1.5 flex-1 bg-stone-200 rounded-full overflow-hidden">
                      <div className="h-full rounded-full bg-gradient-to-r from-amber-500 to-yellow-400" style={{ width: `${c.match}%` }}/>
                    </div>
                    <span className="text-amber-600 text-xs font-display font-bold">{c.match}%</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* COURSES */}
          {activeTab === "courses" && (
            <div className="flex flex-col gap-3">
              <p className="text-muted text-sm">Higher education paths based on your interests and stage:</p>
              {profile.courses.map((c, i) => (
                <div key={i} className="card-base p-4">
                  <p className="text-xs font-display font-bold text-teal-600 mb-2">HIGHER EDUCATION</p>
                  <p className="text-ink font-display font-bold text-sm mb-3">{c.name}</p>
                  <div className="flex items-center gap-3">
                    <div className="h-1.5 flex-1 bg-stone-200 rounded-full overflow-hidden">
                      <div className="h-full rounded-full bg-gradient-to-r from-teal-500 to-teal-600" style={{ width: `${c.match}%` }}/>
                    </div>
                    <span className="text-teal-600 text-xs font-display font-bold">{c.match}%</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="flex flex-col gap-3 mt-6">
            <Link href="/explore" className="btn-secondary w-full">Explore live opportunities →</Link>
            <button onClick={reset}
              className="w-full py-3.5 rounded-full bg-white border-2 border-stone-200 text-muted text-sm font-display font-semibold hover:text-ink hover:border-stone-300 transition-all duration-200">
              ↺ Retake Assessment
            </button>
          </div>
        </div>
      </div>
    );
  }
  return null;
}
