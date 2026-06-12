// ValueWeave — system-seeded opportunity generator.
// Deterministically generates migrations/003_seed_opportunities.sql:
// 100 opportunities × 5 sectors = 500 rows across the 22 marketplace
// districts. Re-run with `node scripts/generate-opportunity-seeds.mjs`
// after editing templates; the SQL is idempotent (deletes previous seeds).

import fs from "fs";

const DISTRICTS = [
  ["Hyderabad", "Telangana"], ["Rangareddy", "Telangana"], ["Medchal", "Telangana"],
  ["Medak", "Telangana"], ["Sangareddy", "Telangana"], ["Warangal", "Telangana"],
  ["Karimnagar", "Telangana"], ["Nizamabad", "Telangana"], ["Khammam", "Telangana"],
  ["Mahabubnagar", "Telangana"], ["Siddipet", "Telangana"], ["Nalgonda", "Telangana"],
  ["Visakhapatnam", "Andhra Pradesh"], ["Vijayawada", "Andhra Pradesh"], ["Guntur", "Andhra Pradesh"],
  ["Tirupati", "Andhra Pradesh"], ["Kurnool", "Andhra Pradesh"], ["Nellore", "Andhra Pradesh"],
  ["Kakinada", "Andhra Pradesh"], ["Anantapur", "Andhra Pradesh"], ["Rajahmundry", "Andhra Pradesh"],
  ["Kadapa", "Andhra Pradesh"],
];

// 5 templates per sector × 22 districts = 110 combos; first 100 used.
const SECTORS = {
  healthcare: [
    { t: "Rural Diagnostic Collection Center", role: "Operations & Delivery Lead", collab: "cofounder", commit: "full-time", inv: "₹1L – ₹3L",
      d: (dist, st) => `Set up a last-mile diagnostic sample collection point in ${dist} partnered with major pathology labs. Patients in ${dist}'s mandals currently travel hours for routine blood tests. Looking for a hands-on partner to run daily operations, phlebotomist hiring, and lab tie-ups. Commission-based revenue with PMJAY empanelment upside.`,
      skills: ["Lab Operations", "Customer Handling", "Field Marketing"] },
    { t: "Telemedicine Support Partner", role: "Community & Impact Lead", collab: "partner", commit: "part-time", inv: "₹2L – ₹5L",
      d: (dist, st) => `Launch a telemedicine facilitation kiosk in ${dist} with basic diagnostics (BP, SpO2, glucose) and video consultations with ${st === "Telangana" ? "Hyderabad" : "Vijayawada"} doctors at ₹50–100 per visit. Need a partner with healthcare or community background to manage the kiosk and build trust with local families.`,
      skills: ["Customer Handling", "Operations Coordination", "Health Worker (ANM/GNM)"] },
    { t: "Mobile Health Screening Unit", role: "Operations & Delivery Lead", collab: "cofounder", commit: "full-time", inv: "₹5L – ₹12L",
      d: (dist, st) => `Run a van-based preventive screening service (diabetes, hypertension, anaemia, eye checks) covering villages and schools across ${dist}. Corporate CSR and government screening contracts provide anchor revenue. Seeking a co-founder for route operations and medical staffing.`,
      skills: ["Operations Coordination", "Team Management", "Field Marketing"] },
    { t: "Pharmacy Franchise Partner", role: "Finance & Research Lead", collab: "partner", commit: "full-time", inv: "₹8L – ₹15L",
      d: (dist, st) => `Open a branded generic-medicine pharmacy in ${dist} under an established franchise. Generic medicines cut patient costs 40–70% and footfall in ${dist} town is strong. Need a partner to co-invest and manage inventory, compliance, and billing.`,
      skills: ["Inventory Management", "Accounting", "Customer Handling"] },
    { t: "Elder Care Service Partner", role: "Community & Impact Lead", collab: "cofounder", commit: "part-time", inv: "₹2L – ₹5L",
      d: (dist, st) => `Build a trained-caregiver service for elders in ${dist} — daily living support, medication reminders, and doctor-visit escorts on monthly subscriptions. Children working in cities pay reliably for parent care back home. Looking for an empathetic operator to recruit and manage caregivers.`,
      skills: ["Caregiving", "Team Management", "Customer Handling"] },
  ],
  education: [
    { t: "Skill Development Center", role: "Operations & Delivery Lead", collab: "cofounder", commit: "full-time", inv: "₹3L – ₹7L",
      d: (dist, st) => `Start an NCVT-aligned vocational skills lab in ${dist} — electrician, plumbing, and AC technician bridge courses with contractor placement tie-ups. ${st} construction demand is starved of certified tradespeople. Need a partner for batches, trainers, and placement relationships.`,
      skills: ["Teaching", "Operations Coordination", "Team Management"] },
    { t: "Competitive Exam Academy", role: "Product & Strategy Lead", collab: "cofounder", commit: "full-time", inv: "₹2L – ₹5L",
      d: (dist, st) => `Affordable group coaching in ${dist} for ${st === "Telangana" ? "TSPSC, SSC, and constable" : "APPSC, SSC, and constable"} exams with printed material and weekly mock tests. Lakhs of aspirants in the district can't afford city coaching. Seeking a subject-expert co-founder to own curriculum and test series.`,
      skills: ["Teaching", "Content Writing", "Counselling"] },
    { t: "Spoken English Institute", role: "Marketing & Sales Lead", collab: "partner", commit: "part-time", inv: "₹1L – ₹3L",
      d: (dist, st) => `Six-week evening spoken-English and digital-literacy batches in ${dist} for students, job-seekers, and homemakers. English fluency gates most private jobs here. Need a partner to drive admissions through schools, colleges, and WhatsApp communities.`,
      skills: ["Teaching", "Social Media Management", "Local Sales"] },
    { t: "Coding Training Center", role: "Product & Strategy Lead", collab: "cofounder", commit: "full-time", inv: "₹2L – ₹5L",
      d: (dist, st) => `Twelve-week Python, web development, and freelancing bootcamp for ${dist} youth — online delivery with an offline support centre. Rural students have the aptitude but no structured path into tech careers. Looking for a developer co-founder to lead instruction.`,
      skills: ["Web Development", "Teaching", "Community Management"] },
    { t: "Play School & Activity Centre Partner", role: "Community & Impact Lead", collab: "partner", commit: "full-time", inv: "₹3L – ₹8L",
      d: (dist, st) => `Launch a bilingual early-childhood activity centre in ${dist} with structured kits and parent engagement. Quality preschool education barely exists outside cities in ${st}. Seeking a Montessori-trained or education-passionate partner to run the centre.`,
      skills: ["Teaching", "Customer Handling", "Operations Coordination"] },
  ],
  agri: [
    { t: "Organic Produce Aggregator", role: "Business Development Lead", collab: "cofounder", commit: "full-time", inv: "₹4L – ₹10L",
      d: (dist, st) => `Aggregate certified-organic vegetables and grains from ${dist} farmers and supply urban subscription customers and premium stores. Affluent buyers want traceable organic food; ${dist} farmers want better prices. Need a co-founder for farmer onboarding and quality control.`,
      skills: ["Organic Farming", "Vendor Management", "Logistics"] },
    { t: "Farmer Advisory Service", role: "R&D & Quality Lead", collab: "partner", commit: "part-time", inv: "₹50K – ₹2L",
      d: (dist, st) => `Subscription agri-advisory for ${dist} farmers — soil-test-based fertiliser plans, pest alerts, and crop planning over WhatsApp and field visits. Wrong input use burns farmer margins every season. Looking for an agriculture graduate partner for the advisory content.`,
      skills: ["Agriculture", "Soil Testing", "Field Marketing"] },
    { t: "Cold Storage Partnership", role: "Operations & Delivery Lead", collab: "cofounder", commit: "full-time", inv: "₹8L – ₹15L",
      d: (dist, st) => `Shared micro cold-storage units (2–5 ton) at ${dist} mandis, rented hourly or daily so small farmers stop losing 30% of harvests to spoilage. Proven model in other districts; land options identified. Need an operations co-founder and co-investor.`,
      skills: ["Operations Coordination", "Electrical Work", "Vendor Management"] },
    { t: "Agri Export Facilitation", role: "Finance & Research Lead", collab: "partner", commit: "part-time", inv: "₹2L – ₹6L",
      d: (dist, st) => `Help ${dist} FPOs and processors reach export buyers — APEDA registration, quality certification, documentation, and buyer matchmaking on a success-fee model. ${st} produce sells at a fraction of export value for lack of paperwork support. Seeking an EXIM-savvy partner.`,
      skills: ["Export Documentation", "Sales", "Quality Control"] },
    { t: "Farm Input Subscription Service", role: "Business Development Lead", collab: "team-member", commit: "full-time", inv: "₹2L – ₹5L",
      d: (dist, st) => `Monthly curated input boxes (seeds, nutrients, bio-pesticides) delivered to registered farmers across ${dist} with WhatsApp ordering. Counterfeit inputs are rampant in the district. Need a field-sales lead to build the farmer subscriber base mandal by mandal.`,
      skills: ["Field Marketing", "Inventory Management", "Customer Handling"] },
  ],
  "ai-tech": [
    { t: "Digital Marketing Agency", role: "Marketing & Sales Lead", collab: "cofounder", commit: "full-time", inv: "₹50K – ₹2L",
      d: (dist, st) => `Run Google and Meta campaigns, WhatsApp Business setup, and content for ${dist} shops, hospitals, and coaching centres. Thousands of local businesses in ${dist} have zero digital presence. Looking for a co-founder to own client acquisition while I handle delivery.`,
      skills: ["Digital Marketing", "Graphic Design", "Sales"] },
    { t: "AI Automation Consultant", role: "Product & Strategy Lead", collab: "partner", commit: "part-time", inv: "₹50K – ₹2L",
      d: (dist, st) => `Build WhatsApp chatbots, billing automations, and AI assistants in Telugu for ${dist} businesses — clinics, schools, and traders at ₹15K–50K per deployment. Local SMBs lose customers who message after hours. Need a technical partner who can ship fast.`,
      skills: ["AI Engineering", "Web Development", "Content Writing"] },
    { t: "Website Development Studio", role: "Operations & Delivery Lead", collab: "team-member", commit: "project-based", inv: "₹50K – ₹1L",
      d: (dist, st) => `₹5K–15K websites plus monthly SEO retainers for ${dist} schools, clinics, and mandal-level enterprises. 10,000+ undigitised SMBs in the district. Seeking a developer teammate for build-out while founders run field sales.`,
      skills: ["Web Development", "SEO", "Graphic Design"] },
    { t: "Local Business SaaS Partner", role: "Product & Strategy Lead", collab: "cofounder", commit: "full-time", inv: "₹3L – ₹8L",
      d: (dist, st) => `Subscription HR/billing software for ${dist} factories, schools, and hospitals with 20–200 employees — PF/ESI compliance built in. Mid-size employers here still run payroll on paper. Need a SaaS engineer co-founder; distribution network already mapped.`,
      skills: ["Web Development", "Sales", "Accounting"] },
    { t: "CCTV & Smart Systems Installer", role: "Operations & Delivery Lead", collab: "partner", commit: "full-time", inv: "₹2L – ₹6L",
      d: (dist, st) => `Design, install, and maintain CCTV, access control, and alarm systems for ${dist} commercial premises with recurring AMC income. Security spend in ${st} towns is rising fast. Looking for a technician partner with electrical experience.`,
      skills: ["CCTV Installation", "Electrical Work", "Local Sales"] },
  ],
  manufacturing: [
    { t: "Furniture Unit Partner", role: "Operations & Delivery Lead", collab: "cofounder", commit: "full-time", inv: "₹5L – ₹12L",
      d: (dist, st) => `Set up a wooden furniture workshop in ${dist} serving schools, hostels, and offices plus a retail showroom. Institutions currently truck furniture from cities at a premium. Need a master-carpenter or operations co-founder to run production.`,
      skills: ["Carpentry", "Team Management", "Sales"] },
    { t: "Solar Installation Business", role: "Operations & Delivery Lead", collab: "cofounder", commit: "full-time", inv: "₹2L – ₹8L",
      d: (dist, st) => `Rooftop solar EPC for homes and shops across ${dist} riding the PM Surya Ghar subsidy wave, plus agri pump-set installs. Leads are inbound; execution capacity is the bottleneck. Seeking an electrician-led partner to build the install crew.`,
      skills: ["Solar Installation", "Electrical Work", "Field Marketing"] },
    { t: "Packaging Unit Partner", role: "Finance & Research Lead", collab: "partner", commit: "full-time", inv: "₹4L – ₹10L",
      d: (dist, st) => `Machine-made paper bags and eco-packaging for ${dist} supermarkets, pharmacies, and food brands — plastic-ban compliance is forcing the switch. Machinery shortlisted; need a co-investing partner to own B2B sales and accounts.`,
      skills: ["Packaging", "B2B Sales", "Inventory Management"] },
    { t: "Small Food Processing Unit", role: "Operations & Delivery Lead", collab: "cofounder", commit: "full-time", inv: "₹4L – ₹10L",
      d: (dist, st) => `FSSAI-registered unit in ${dist} processing local produce into packaged products — millet mixes, cold-pressed oils, or spice powders depending on the local crop. PMFME gives 35% subsidy. Need a production-minded co-founder; distribution channels in place.`,
      skills: ["Food Processing", "Quality Control", "Operations Coordination"] },
    { t: "Agri Tool Fabrication Workshop", role: "Operations & Delivery Lead", collab: "partner", commit: "full-time", inv: "₹3L – ₹8L",
      d: (dist, st) => `Fabricate and repair farm tools, gates, and trailers for ${dist} farmers with government scheme procurement upside. Local machinery sits idle for weeks waiting on distant workshops. Seeking a welder/fabricator partner for the shop floor.`,
      skills: ["Welding", "Mechanical Work", "Local Sales"] },
  ],
};

const esc = (s) => String(s).replace(/'/g, "''");

const rows = [];
for (const [category, templates] of Object.entries(SECTORS)) {
  for (let i = 0; i < 100; i++) {
    const [dist, state] = DISTRICTS[i % DISTRICTS.length];
    const tpl = templates[Math.floor(i / DISTRICTS.length)];
    rows.push(
      `('${esc(tpl.t)} — ${esc(dist)}', '${esc(tpl.d(dist, state))}', '${category}', ` +
      `array[${tpl.skills.map((s) => `'${esc(s)}'`).join(",")}], '${esc(dist)}, ${esc(state)}', ` +
      `'${tpl.collab}', '${tpl.commit}', '${esc(dist)}', '${esc(state)}', '${esc(tpl.role)}', ` +
      `'${esc(tpl.inv)}', 'open', 'system_seed')`
    );
  }
}

const sql = `-- ValueWeave — system-seeded opportunity base (generated file).
-- Source: frontend/scripts/generate-opportunity-seeds.mjs — edit the
-- templates there and re-run; do not hand-edit this file.
-- 500 opportunities: 100 each in healthcare, education, agri (Agriculture),
-- ai-tech (Technology), manufacturing — across 22 TS/AP districts.
-- Idempotent: previous system seeds are replaced. Run AFTER
-- 002_collaboration_marketplace.sql.

delete from public.opportunities where created_by = 'system_seed';

insert into public.opportunities
  (title, description, category, skills_needed, location,
   collaboration_type, commitment, district, state, founder_role,
   investment_range, status, created_by)
values
${rows.join(",\n")};
`;

fs.writeFileSync(new URL("../migrations/003_seed_opportunities.sql", import.meta.url), sql);
console.log(`OK: wrote ${rows.length} seed rows to migrations/003_seed_opportunities.sql`);
