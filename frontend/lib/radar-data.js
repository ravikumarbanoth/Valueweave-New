// ValueWeave — Opportunity Radar engine.
// Static ranked dataset. `ideaSlug` references real Idea Library entries;
// `researchSlug` references content/research/*.mdx articles;
// `districtSuitability` uses slugs from lib/districts-data.js only.

export const RADAR_OPPORTUNITIES = [
  // ── TELANGANA ──
  { id: "ts-01", title: "Micro Cold Storage & Agri Logistics", sector: "Logistics", fitScore: 91, investmentRange: "₹8L–₹15L", investmentMin: 800000, investmentMax: 1500000, demandScore: 93, districtSuitability: ["medak", "nizamabad", "khammam"], stateTag: "Telangana", segment: "telangana", ideaSlug: "micro-cold-storage-as-a-service", trending: true },
  { id: "ts-02", title: "EV Charging Station Network", sector: "Energy", fitScore: 88, investmentRange: "₹8L–₹25L", investmentMin: 800000, investmentMax: 2500000, demandScore: 90, districtSuitability: ["warangal", "karimnagar", "nizamabad"], stateTag: "Telangana", segment: "telangana", ideaSlug: "ev-charging-hub", researchSlug: "ev-charging-business-telangana", trending: true },
  { id: "ts-03", title: "Turmeric Value-Addition Unit", sector: "Food Processing", fitScore: 93, investmentRange: "₹10L–₹40L", investmentMin: 1000000, investmentMax: 4000000, demandScore: 95, districtSuitability: ["nizamabad", "karimnagar"], stateTag: "Telangana", segment: "telangana" },
  { id: "ts-04", title: "Industrial B2B Services (Patancheru Belt)", sector: "Services", fitScore: 84, investmentRange: "₹2L–₹10L", investmentMin: 200000, investmentMax: 1000000, demandScore: 86, districtSuitability: ["sangareddy", "medak"], stateTag: "Telangana", segment: "telangana", ideaSlug: "industrial-energy-audit-service" },
  { id: "ts-05", title: "Rural Diagnostic Collection Network", sector: "Healthcare", fitScore: 84, investmentRange: "₹1L–₹3L", investmentMin: 100000, investmentMax: 300000, demandScore: 87, districtSuitability: ["medak", "siddipet", "khammam"], stateTag: "Telangana", segment: "telangana", ideaSlug: "diagnostic-sample-collection-hub", researchSlug: "rural-diagnostic-centers-india" },
  // ── ANDHRA PRADESH ──
  { id: "ap-01", title: "Chilli & Spice Value Chain", sector: "Food Processing", fitScore: 94, investmentRange: "₹5L–₹25L", investmentMin: 500000, investmentMax: 2500000, demandScore: 96, districtSuitability: ["guntur", "vijayawada"], stateTag: "Andhra Pradesh", segment: "andhra-pradesh", ideaSlug: "cold-pressed-oil-unit", trending: true },
  { id: "ap-02", title: "Rural Micro-Fulfilment & 3PL", sector: "Logistics", fitScore: 90, investmentRange: "₹8L–₹18L", investmentMin: 800000, investmentMax: 1800000, demandScore: 92, districtSuitability: ["vijayawada", "guntur", "nellore"], stateTag: "Andhra Pradesh", segment: "andhra-pradesh", ideaSlug: "rural-micro-fulfilment-centre" },
  { id: "ap-03", title: "Battery Recycling Unit", sector: "Recycling", fitScore: 83, investmentRange: "₹15L–₹60L", investmentMin: 1500000, investmentMax: 6000000, demandScore: 85, districtSuitability: ["guntur", "visakhapatnam"], stateTag: "Andhra Pradesh", segment: "andhra-pradesh", researchSlug: "battery-recycling-business-india" },
  { id: "ap-04", title: "Aqua Inputs & Water Testing Services", sector: "Aquaculture", fitScore: 87, investmentRange: "₹2L–₹15L", investmentMin: 200000, investmentMax: 1500000, demandScore: 91, districtSuitability: ["nellore", "guntur"], stateTag: "Andhra Pradesh", segment: "andhra-pradesh", ideaSlug: "water-quality-testing-service", trending: true },
  { id: "ap-05", title: "Pilgrim Services & Tour Tech", sector: "Tourism", fitScore: 86, investmentRange: "₹2L–₹10L", investmentMin: 200000, investmentMax: 1000000, demandScore: 89, districtSuitability: ["tirupati", "visakhapatnam"], stateTag: "Andhra Pradesh", segment: "andhra-pradesh", ideaSlug: "temple-town-tour-guide-app" },
  // ── STUDENTS / YOUTH ──
  { id: "st-01", title: "Competitive Exam Coaching Centre", sector: "Education", fitScore: 85, investmentRange: "₹2L–₹5L", investmentMin: 200000, investmentMax: 500000, demandScore: 88, districtSuitability: ["warangal", "karimnagar", "vijayawada"], stateTag: "Telangana", segment: "students", ideaSlug: "competitive-exam-coaching-centre" },
  { id: "st-02", title: "Handloom D2C Brand", sector: "Retail", fitScore: 91, investmentRange: "₹3L–₹7L", investmentMin: 300000, investmentMax: 700000, demandScore: 89, districtSuitability: ["warangal", "siddipet"], stateTag: "Telangana", segment: "students", ideaSlug: "handloom-weaver-aggregation-platform", trending: true },
  { id: "st-03", title: "Digital Marketing Agency (Local SMBs)", sector: "Technology", fitScore: 88, investmentRange: "₹50K–₹2L", investmentMin: 50000, investmentMax: 200000, demandScore: 87, districtSuitability: ["hyderabad", "warangal", "vijayawada"], stateTag: "Telangana", segment: "students", ideaSlug: "seo-local-marketing-agency" },
  { id: "st-04", title: "Vernacular AI Chatbot Agency", sector: "Technology", fitScore: 86, investmentRange: "₹3L–₹7L", investmentMin: 300000, investmentMax: 700000, demandScore: 86, districtSuitability: ["hyderabad", "visakhapatnam"], stateTag: "Telangana", segment: "students", ideaSlug: "vernacular-ai-chatbot-agency", trending: true },
  { id: "st-05", title: "Hyperlocal District News Portal", sector: "Media", fitScore: 82, investmentRange: "₹2L–₹6L", investmentMin: 200000, investmentMax: 600000, demandScore: 81, districtSuitability: ["karimnagar", "kurnool", "nellore"], stateTag: "Telangana", segment: "students", ideaSlug: "hyperlocal-district-news-portal" },
  // ── HEALTHCARE ──
  { id: "hc-01", title: "Rural Diagnostic Centre", sector: "Healthcare", fitScore: 87, investmentRange: "₹8L–₹20L", investmentMin: 800000, investmentMax: 2000000, demandScore: 90, districtSuitability: ["medak", "kurnool", "khammam"], stateTag: "Telangana", segment: "healthcare", researchSlug: "rural-diagnostic-centers-india", trending: true },
  { id: "hc-02", title: "Tele-health Facilitation Centre", sector: "Healthcare", fitScore: 85, investmentRange: "₹2L–₹5L", investmentMin: 200000, investmentMax: 500000, demandScore: 88, districtSuitability: ["kurnool", "khammam", "siddipet"], stateTag: "Andhra Pradesh", segment: "healthcare", ideaSlug: "tele-health-facilitation-centre" },
  { id: "hc-03", title: "Elder Care Home Assistance", sector: "Healthcare", fitScore: 84, investmentRange: "₹2L–₹5L", investmentMin: 200000, investmentMax: 500000, demandScore: 87, districtSuitability: ["hyderabad", "vijayawada", "visakhapatnam"], stateTag: "Telangana", segment: "healthcare", ideaSlug: "elder-care-home-assistance-service" },
  { id: "hc-04", title: "Physiotherapy & Rehab Clinic", sector: "Healthcare", fitScore: 82, investmentRange: "₹3L–₹7L", investmentMin: 300000, investmentMax: 700000, demandScore: 84, districtSuitability: ["warangal", "guntur", "tirupati"], stateTag: "Telangana", segment: "healthcare", ideaSlug: "physiotherapy-and-rehab-clinic" },
  // ── AGRICULTURE ──
  { id: "ag-01", title: "Farm Input Subscription Box", sector: "Agriculture", fitScore: 88, investmentRange: "₹2L–₹5L", investmentMin: 200000, investmentMax: 500000, demandScore: 90, districtSuitability: ["siddipet", "guntur", "kurnool"], stateTag: "Telangana", segment: "agriculture", ideaSlug: "farm-input-subscription-box", trending: true },
  { id: "ag-02", title: "Drone Crop Spraying Service", sector: "AgriTech", fitScore: 86, investmentRange: "₹10L–₹20L", investmentMin: 1000000, investmentMax: 2000000, demandScore: 87, districtSuitability: ["warangal", "nizamabad", "guntur"], stateTag: "Telangana", segment: "agriculture", ideaSlug: "drone-spraying-service" },
  { id: "ag-03", title: "Agri Waste to Biochar Unit", sector: "Agriculture", fitScore: 83, investmentRange: "₹6L–₹12L", investmentMin: 600000, investmentMax: 1200000, demandScore: 84, districtSuitability: ["nizamabad", "karimnagar", "guntur"], stateTag: "Telangana", segment: "agriculture", ideaSlug: "agri-waste-to-biochar-unit" },
  { id: "ag-04", title: "Ready-to-Cook Millet Products", sector: "Food Processing", fitScore: 85, investmentRange: "₹4L–₹10L", investmentMin: 400000, investmentMax: 1000000, demandScore: 86, districtSuitability: ["kurnool", "hyderabad", "warangal"], stateTag: "Andhra Pradesh", segment: "agriculture", ideaSlug: "ready-to-cook-millet-products" },
  // ── UNDER 5 LAKHS ──
  { id: "u5-01", title: "GST Filing & Compliance Service", sector: "Finance", fitScore: 87, investmentRange: "₹1L–₹3L", investmentMin: 100000, investmentMax: 300000, demandScore: 86, districtSuitability: ["warangal", "guntur", "nellore"], stateTag: "Telangana", segment: "under-5-lakhs", ideaSlug: "gst-filing-and-compliance-service", trending: true },
  { id: "u5-02", title: "Diagnostic Sample Collection Hub", sector: "Healthcare", fitScore: 85, investmentRange: "₹1L–₹3L", investmentMin: 100000, investmentMax: 300000, demandScore: 87, districtSuitability: ["medak", "siddipet", "kurnool"], stateTag: "Telangana", segment: "under-5-lakhs", ideaSlug: "diagnostic-sample-collection-hub" },
  { id: "u5-03", title: "Mobile Beauty Service for Women", sector: "Services", fitScore: 83, investmentRange: "₹1L–₹3L", investmentMin: 100000, investmentMax: 300000, demandScore: 82, districtSuitability: ["hyderabad", "warangal", "vijayawada"], stateTag: "Telangana", segment: "under-5-lakhs", ideaSlug: "mobile-beauty-service-for-women" },
  { id: "u5-04", title: "Agri Produce Transport Aggregator", sector: "Logistics", fitScore: 82, investmentRange: "₹2L–₹5L", investmentMin: 200000, investmentMax: 500000, demandScore: 84, districtSuitability: ["nizamabad", "guntur", "nellore"], stateTag: "Andhra Pradesh", segment: "under-5-lakhs", ideaSlug: "agri-produce-transport-aggregator" },
  { id: "u5-05", title: "Competitive Exam Coaching", sector: "Education", fitScore: 85, investmentRange: "₹2L–₹5L", investmentMin: 200000, investmentMax: 500000, demandScore: 88, districtSuitability: ["warangal", "karimnagar"], stateTag: "Telangana", segment: "under-5-lakhs", ideaSlug: "competitive-exam-coaching-centre" },
];

export function getRadarBySegment(segment) {
  return RADAR_OPPORTUNITIES
    .filter((o) => o.segment === segment)
    .sort((a, b) => b.fitScore - a.fitScore);
}

export function getAllSegments() {
  return ["telangana", "andhra-pradesh", "students", "healthcare", "agriculture", "under-5-lakhs"];
}

export const SEGMENT_LABELS = {
  "telangana": "Telangana",
  "andhra-pradesh": "Andhra Pradesh",
  "students": "Students & Youth",
  "healthcare": "Healthcare",
  "agriculture": "Agriculture",
  "under-5-lakhs": "Under ₹5 Lakhs",
};
