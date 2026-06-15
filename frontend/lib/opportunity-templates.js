// ValueWeave — Deterministic opportunity generation templates.
// Used by the Admin Bulk Opportunity Generator to produce structured
// opportunity records without calling any external AI API.

export const SECTOR_TEMPLATES = {
  healthcare: {
    label: "Healthcare",
    businessTypes: ["Diagnostic Center", "Pharmacy Chain", "Home Healthcare", "Dental Clinic", "Physiotherapy Center", "Ayurvedic Wellness Center", "Medical Equipment Rental", "Mental Health Clinic"],
    skills: ["medical knowledge", "patient management", "healthcare compliance", "clinical operations", "digital health"],
    collaboratorRoles: ["Medical Professional", "Healthcare Operations Manager", "Medical Tech Expert", "Finance & Compliance"],
    founderRole: "Healthcare Operator",
    descTemplate: (title, district, investment) =>
      `${title} in ${district} addresses the growing demand for accessible, quality healthcare services in Telangana & AP. With investment of ${investment}, this opportunity targets the underserved segments seeking reliable diagnostic, therapeutic, or wellness solutions. The business model focuses on service quality, trust-building, and community outreach to establish a strong local presence.`,
  },
  education: {
    label: "Education",
    businessTypes: ["Coaching Center", "EdTech Platform", "Skill Training Institute", "Preschool & Daycare", "Language Academy", "Computer Training Center", "Vocational Training", "Online Tutoring"],
    skills: ["curriculum design", "teaching methodology", "LMS platforms", "content creation", "student engagement"],
    collaboratorRoles: ["Academic Expert", "EdTech Developer", "Business Operations", "Marketing Specialist"],
    founderRole: "Education Entrepreneur",
    descTemplate: (title, district, investment) =>
      `${title} in ${district} leverages the rising demand for quality education and skill development. With investment of ${investment}, this opportunity creates a learning institution that bridges the gap between traditional education and market-relevant skills. Focus areas include digital integration, experienced faculty, and placement support to build long-term credibility.`,
  },
  agriculture: {
    label: "Agriculture",
    businessTypes: ["Organic Farm", "Cold Storage Facility", "Agri-Input Dealer", "Dairy Farm", "Food Processing Unit", "Drip Irrigation Service", "Agri Export Business", "Farmer Producer Company"],
    skills: ["agronomy", "supply chain management", "food safety standards", "cold chain logistics", "market linkages"],
    collaboratorRoles: ["Agricultural Expert", "Supply Chain Manager", "Technology Partner", "Export Specialist"],
    founderRole: "Agripreneur",
    descTemplate: (title, district, investment) =>
      `${title} in ${district} capitalizes on the rich agricultural ecosystem of the region. With investment of ${investment}, this agribusiness addresses value chain gaps from farm to fork — improving farmer incomes while meeting urban demand for quality produce. Government subsidies and APMC reforms create favorable conditions for this sector.`,
  },
  manufacturing: {
    label: "Manufacturing",
    businessTypes: ["Garment Manufacturing", "Food Processing Unit", "Packaging Solutions", "Auto Components", "Furniture Manufacturing", "Chemical Manufacturing", "Electronics Assembly", "Plastic Products"],
    skills: ["production management", "quality control", "supply chain", "machinery operation", "export compliance"],
    collaboratorRoles: ["Manufacturing Expert", "Quality Manager", "Export & Logistics", "Finance & Compliance"],
    founderRole: "Manufacturing Entrepreneur",
    descTemplate: (title, district, investment) =>
      `${title} in ${district} taps into the industrial growth corridors supported by Telangana's TS-iPASS and AP's investment incentives. With investment of ${investment}, this manufacturing unit targets domestic and export markets, leveraging local raw material availability and skilled labor. Government incentives for industrial units provide additional ROI advantage.`,
  },
  technology: {
    label: "Technology",
    businessTypes: ["SaaS Platform", "AI Consulting", "Mobile App Development", "Cybersecurity Firm", "IoT Solutions", "Digital Marketing Agency", "E-commerce Platform", "Data Analytics Service"],
    skills: ["software development", "AI/ML", "cloud computing", "product management", "digital marketing"],
    collaboratorRoles: ["Tech Founder/CTO", "Product Manager", "Business Developer", "UX/UI Designer"],
    founderRole: "Tech Entrepreneur",
    descTemplate: (title, district, investment) =>
      `${title} in ${district} addresses the growing digital transformation needs of businesses across Telangana & AP. With investment of ${investment}, this tech venture targets SMBs and enterprises seeking affordable digital solutions. The HITEC City and Amaravati tech ecosystems provide talent access, while pan-India remote delivery expands the addressable market.`,
  },
  retail: {
    label: "Retail",
    businessTypes: ["Supermarket", "Fashion Boutique", "Electronics Store", "Home Décor Store", "Organic Grocery", "Sports Goods Store", "Toy Store", "Pet Shop"],
    skills: ["retail operations", "inventory management", "customer service", "visual merchandising", "digital commerce"],
    collaboratorRoles: ["Retail Operations Expert", "Category Manager", "Marketing Lead", "Tech & E-commerce"],
    founderRole: "Retail Entrepreneur",
    descTemplate: (title, district, investment) =>
      `${title} in ${district} leverages rising consumer spending and the shift toward organized retail. With investment of ${investment}, this retail venture aims to capture local market share through quality assortment, competitive pricing, and seamless online-offline integration. District-level retail gaps provide first-mover advantage for well-executed operators.`,
  },
  hospitality: {
    label: "Hospitality",
    businessTypes: ["Cloud Kitchen", "Restaurant", "Hotel/Guest House", "Event Venue", "Catering Service", "Food Truck", "Café", "Wedding Planning"],
    skills: ["hospitality management", "food & beverage operations", "event management", "customer experience", "vendor management"],
    collaboratorRoles: ["Chef/Food Expert", "Operations Manager", "Marketing & Social Media", "Finance Manager"],
    founderRole: "Hospitality Entrepreneur",
    descTemplate: (title, district, investment) =>
      `${title} in ${district} serves the growing demand for quality food, accommodation, and event experiences. With investment of ${investment}, this hospitality business targets the expanding middle class, business travelers, and event markets. Local cuisine, quality service, and digital ordering/booking integration differentiate this offering in the competitive hospitality landscape.`,
  },
  logistics: {
    label: "Logistics",
    businessTypes: ["Last-Mile Delivery", "Warehouse & Storage", "Transport Fleet", "Cold Chain Logistics", "E-commerce Fulfillment", "Courier Service", "Freight Forwarding", "Vehicle Leasing"],
    skills: ["fleet management", "route optimization", "warehouse operations", "technology integration", "customs & compliance"],
    collaboratorRoles: ["Logistics Operations Expert", "Technology Partner", "Fleet Manager", "Finance & Compliance"],
    founderRole: "Logistics Entrepreneur",
    descTemplate: (title, district, investment) =>
      `${title} in ${district} addresses the infrastructure needs of the booming e-commerce and manufacturing sectors. With investment of ${investment}, this logistics business fills critical gaps in last-mile connectivity, warehousing capacity, or cold chain infrastructure. The district's industrial growth and connectivity improvements create sustained demand for reliable logistics partners.`,
  },
};

export const INVESTMENT_RANGES = [
  "Under ₹2L",
  "₹2L – ₹5L",
  "₹5L – ₹10L",
  "₹10L – ₹25L",
  "₹25L – ₹50L",
  "₹50L – ₹1Cr",
  "Above ₹1Cr",
];

export const FOUNDER_ROLES = [
  "Entrepreneur",
  "Healthcare Operator",
  "Education Entrepreneur",
  "Agripreneur",
  "Manufacturing Entrepreneur",
  "Tech Entrepreneur",
  "Retail Entrepreneur",
  "Hospitality Entrepreneur",
  "Logistics Entrepreneur",
  "Investor/Funder",
];

export function generateOpportunityRecord({ sector, businessType, district, state, investmentRange, founderRole, index }) {
  const template = SECTOR_TEMPLATES[sector];
  if (!template) return null;

  const title = businessType || template.businessTypes[index % template.businessTypes.length];
  const description = template.descTemplate(title, district, investmentRange);
  const skills = template.skills;
  const collaboratorRoles = template.collaboratorRoles;

  return {
    title: `${title} — ${district}`,
    description,
    category: sector,
    district,
    state,
    investment_range: investmentRange,
    founder_role: founderRole || template.founderRole,
    skills_needed: skills,
    location: district,
    collaboration_type: "co-founder",
    commitment: "full-time",
    status: "open",
    created_by: "system_seed",
    owner_id: null,
    _meta: { collaboratorRoles },
  };
}
