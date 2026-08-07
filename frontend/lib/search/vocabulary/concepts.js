// The multilingual vocabulary map. DATA, not code — see README.md before editing.
//
// One object per CONCEPT. A concept is a thing a person can want, named once in
// English and then written down every way somebody might type it: English
// synonyms, Telugu script, and Tanglish (Telugu sounds in Latin letters).
//
//   id            stable key, lower-case, hyphenated. Never reuse or rename.
//   en_canonical  what we call it back to the user, and the term the ranker
//                 receives as though it had been typed.
//   en            English synonyms and trade names.
//   te            Telugu script. Also indexed under its transliteration, so
//                 the Latin spelling is free and must not be repeated below.
//   tanglish      romanised Telugu that does NOT fall out of transliteration —
//                 whole different words (raitu for farmer), not spellings of
//                 the same one (medak). Spelling variance is handled by the
//                 phonetic key; do not enumerate it.
//   expands_to    English terms to ALSO search for. Every one of these must
//                 match at least one live entity — tests/test_multilingual_search
//                 fails the build otherwise. An expansion that matches nothing
//                 costs a query and returns silence.
//
// Districts, states and any other proper noun spelled the same way in both
// scripts are deliberately absent. Telugu -> Latin transliteration reaches all
// 61 districts with no rows at all, and a row per district would be 61 places
// for the next district to be forgotten.
//
// Frozen so a caller cannot mutate the shared table by accident.

export default Object.freeze({
  "version": "1.0.0",
  "languages": [
    "en",
    "te",
    "tanglish"
  ],
  "concepts": [
    {
      "id": "electrician",
      "en_canonical": "electrician",
      "en": [
        "electrical services",
        "wireman",
        "domestic wiring",
        "electrical contractor",
        "electrical technician",
        "house wiring",
        "domestic electrician",
        "panel wiring",
        "electrical supervisor"
      ],
      "te": [
        "ఎలక్ట్రిషియన్",
        "వైర్‌మ్యాన్",
        "విద్యుత్ పనులు",
        "కరెంట్ పని"
      ],
      "tanglish": [
        "current pani"
      ],
      "expands_to": [
        "electrical",
        "wiring",
        "wireman",
        "domestic wiring",
        "power distribution",
        "electrical panel",
        "industrial electrician"
      ]
    },
    {
      "id": "plumber",
      "en_canonical": "plumber",
      "en": [
        "plumbing",
        "pipe fitting",
        "sanitary work",
        "pipe fitter",
        "sanitary installer",
        "plumbing technician",
        "steam fitter",
        "plumer",
        "plummer"
      ],
      "te": [
        "ప్లంబర్",
        "పైపు పని",
        "నల్లా పని"
      ],
      "tanglish": [],
      "expands_to": [
        "plumbing"
      ]
    },
    {
      "id": "carpenter",
      "en_canonical": "carpenter",
      "en": [
        "carpentry",
        "wood work",
        "furniture making",
        "woodworker",
        "joiner",
        "furniture carpenter",
        "wood turner"
      ],
      "te": [
        "వడ్రంగి",
        "కార్పెంటర్",
        "కలప పని"
      ],
      "tanglish": [],
      "expands_to": [
        "carpentry"
      ]
    },
    {
      "id": "welder",
      "en_canonical": "welder",
      "en": [
        "welding",
        "metal fabrication",
        "fabricator",
        "arc welder",
        "mig welder",
        "tig welder",
        "coded welder",
        "fitter welder",
        "sheet metal worker",
        "structural fabricator",
        "welda"
      ],
      "te": [
        "వెల్డర్",
        "వెల్డింగ్",
        "ఇనుప పని"
      ],
      "tanglish": [],
      "expands_to": [
        "welding",
        "fabrication",
        "metal fabrication"
      ]
    },
    {
      "id": "mason",
      "en_canonical": "mason",
      "en": [
        "masonry",
        "brickwork",
        "building work",
        "brick mason",
        "construction mason",
        "bricklayer",
        "plasterer",
        "steel fixer",
        "bar bender",
        "rebar fixer",
        "scaffolder"
      ],
      "te": [
        "తాపీ మేస్త్రి",
        "తాపీ పని",
        "ఇటుక పని"
      ],
      "tanglish": [
        "mestri"
      ],
      "expands_to": [
        "masonry",
        "brickwork",
        "construction"
      ]
    },
    {
      "id": "tiles",
      "en_canonical": "tiles fixing",
      "en": [
        "tile mason",
        "tile fitting",
        "flooring",
        "tiling",
        "tile setter",
        "flooring technician",
        "marble polisher",
        "tiles fitter",
        "granite cutter"
      ],
      "te": [
        "టైల్స్",
        "టైల్స్ పని"
      ],
      "tanglish": [
        "tiles pani"
      ],
      "expands_to": [
        "tiles fixing",
        "masonry",
        "brickwork",
        "construction",
        "skilled trades"
      ]
    },
    {
      "id": "painter",
      "en_canonical": "painter",
      "en": [
        "painting",
        "wall painting",
        "house painting",
        "building painter",
        "decorative painter",
        "industrial painter",
        "wall putty applicator"
      ],
      "te": [
        "పెయింటర్",
        "రంగులు వేయడం",
        "పెయింటింగ్"
      ],
      "tanglish": [],
      "expands_to": [
        "painting"
      ]
    },
    {
      "id": "hvac",
      "en_canonical": "HVAC technician",
      "en": [
        "ac repair",
        "air conditioning",
        "refrigeration",
        "ac mechanic",
        "rac mechanic",
        "cooling system technician",
        "fridge mechanic",
        "ac technician",
        "refrigeration mechanic",
        "vrf technician"
      ],
      "te": [
        "ఏసీ రిపేర్",
        "ఎయిర్ కండిషనింగ్"
      ],
      "tanglish": [
        "ac repair pani"
      ],
      "expands_to": [
        "hvac",
        "hvac technician"
      ]
    },
    {
      "id": "stitching",
      "en_canonical": "garment manufacturing",
      "en": [
        "tailoring",
        "tailor",
        "sewing",
        "stitching",
        "boutique"
      ],
      "te": [
        "కుట్టు పని",
        "దుస్తుల తయారీ",
        "టైలరింగ్"
      ],
      "tanglish": [],
      "expands_to": [
        "garment",
        "stitching",
        "sewing",
        "apparel",
        "textiles"
      ]
    },
    {
      "id": "artificial-intelligence",
      "en_canonical": "artificial intelligence",
      "en": [
        "ai",
        "machine learning",
        "generative ai",
        "chatgpt",
        "ai tools"
      ],
      "te": [
        "కృత్రిమ మేధస్సు",
        "ఆర్టిఫిషియల్ ఇంటెలిజెన్స్"
      ],
      "tanglish": [],
      "expands_to": [
        "artificial intelligence",
        "machine learning",
        "ai tooling",
        "ai model training",
        "computer vision",
        "chatbot"
      ]
    },
    {
      "id": "robotics",
      "en_canonical": "robotics",
      "en": [
        "robot",
        "industrial robotics",
        "automation",
        "robotic process automation",
        "robot programmer",
        "robotics service engineer",
        "robotics technician",
        "cobot",
        "robot maintenance"
      ],
      "te": [
        "రోబోటిక్స్",
        "రోబో"
      ],
      "tanglish": [],
      "expands_to": [
        "robotics",
        "industrial robotics",
        "automation"
      ]
    },
    {
      "id": "software",
      "en_canonical": "software development",
      "en": [
        "coding",
        "programming",
        "web development",
        "app development",
        "developer"
      ],
      "te": [
        "సాఫ్ట్‌వేర్",
        "కంప్యూటర్ ప్రోగ్రామింగ్"
      ],
      "tanglish": [
        "computer pani"
      ],
      "expands_to": [
        "software",
        "web development",
        "mobile app development",
        "programming",
        "python"
      ]
    },
    {
      "id": "digital-marketing",
      "en_canonical": "digital marketing",
      "en": [
        "online marketing",
        "social media marketing",
        "seo",
        "ads"
      ],
      "te": [
        "డిజిటల్ మార్కెటింగ్"
      ],
      "tanglish": [],
      "expands_to": [
        "digital marketing",
        "seo",
        "content marketing",
        "social media"
      ]
    },
    {
      "id": "drone",
      "en_canonical": "drone piloting",
      "en": [
        "drone",
        "uav",
        "drone spraying",
        "drone services"
      ],
      "te": [
        "డ్రోన్"
      ],
      "tanglish": [],
      "expands_to": [
        "drone",
        "drone piloting",
        "drone services",
        "drone based spraying"
      ]
    },
    {
      "id": "farmer",
      "en_canonical": "farmer",
      "en": [
        "kisan",
        "cultivator",
        "farming"
      ],
      "te": [
        "రైతు",
        "వ్యవసాయదారుడు"
      ],
      "tanglish": [],
      "expands_to": [
        "agriculture",
        "farming",
        "crop",
        "kisan",
        "farmer producer"
      ]
    },
    {
      "id": "agriculture",
      "en_canonical": "agriculture",
      "en": [
        "agri",
        "cultivation",
        "agri business"
      ],
      "te": [
        "వ్యవసాయం",
        "సాగు"
      ],
      "tanglish": [],
      "expands_to": [
        "agriculture",
        "farming",
        "agritech",
        "agro processing"
      ]
    },
    {
      "id": "dairy",
      "en_canonical": "dairy farming",
      "en": [
        "dairy",
        "milk business",
        "milk",
        "cattle rearing",
        "buffalo"
      ],
      "te": [
        "పాడి పరిశ్రమ",
        "పాల పరిశ్రమ",
        "పాల వ్యాపారం",
        "డైరీ",
        "పశుపోషణ"
      ],
      "tanglish": [
        "paala parishrama",
        "paadi parishrama",
        "paala vyaparam"
      ],
      "expands_to": [
        "cattle"
      ]
    },
    {
      "id": "organic-farming",
      "en_canonical": "organic farming",
      "en": [
        "organic",
        "natural farming",
        "vermicompost",
        "bio fertiliser"
      ],
      "te": [
        "సేంద్రియ వ్యవసాయం",
        "ప్రకృతి వ్యవసాయం"
      ],
      "tanglish": [],
      "expands_to": [
        "organic farming",
        "vermicompost",
        "bio fertiliser"
      ]
    },
    {
      "id": "irrigation",
      "en_canonical": "irrigation",
      "en": [
        "drip irrigation",
        "micro irrigation",
        "sprinkler",
        "water"
      ],
      "te": [
        "నీటిపారుదల",
        "డ్రిప్ ఇరిగేషన్"
      ],
      "tanglish": [
        "neetiparudala"
      ],
      "expands_to": [
        "irrigation",
        "micro irrigation",
        "drip"
      ]
    },
    {
      "id": "millet",
      "en_canonical": "millet",
      "en": [
        "millets",
        "siridhanya",
        "ragi",
        "jowar",
        "bajra"
      ],
      "te": [
        "చిరుధాన్యాలు",
        "రాగులు",
        "జొన్న"
      ],
      "tanglish": [],
      "expands_to": [
        "millet",
        "finger millet",
        "foxtail millet",
        "pearl millet",
        "sorghum"
      ]
    },
    {
      "id": "paddy",
      "en_canonical": "rice",
      "en": [
        "paddy",
        "rice milling",
        "dhan"
      ],
      "te": [
        "వరి",
        "బియ్యం",
        "ధాన్యం"
      ],
      "tanglish": [],
      "expands_to": [
        "rice",
        "paddy",
        "rice mill"
      ]
    },
    {
      "id": "cotton",
      "en_canonical": "cotton",
      "en": [
        "kapas",
        "cotton farming"
      ],
      "te": [
        "పత్తి"
      ],
      "tanglish": [],
      "expands_to": [
        "cotton",
        "textiles"
      ]
    },
    {
      "id": "turmeric",
      "en_canonical": "turmeric",
      "en": [
        "haldi",
        "turmeric powder"
      ],
      "te": [
        "పసుపు"
      ],
      "tanglish": [],
      "expands_to": [
        "turmeric",
        "spice",
        "powder"
      ]
    },
    {
      "id": "chilli",
      "en_canonical": "chilli",
      "en": [
        "mirchi",
        "red chilli",
        "chilli powder"
      ],
      "te": [
        "మిరప",
        "మిరపకాయ"
      ],
      "tanglish": [],
      "expands_to": [
        "chilli",
        "spice",
        "powder"
      ]
    },
    {
      "id": "maize",
      "en_canonical": "maize",
      "en": [
        "corn"
      ],
      "te": [
        "మొక్కజొన్న"
      ],
      "tanglish": [],
      "expands_to": [
        "maize"
      ]
    },
    {
      "id": "groundnut",
      "en_canonical": "groundnut",
      "en": [
        "peanut",
        "oil seed",
        "sesame"
      ],
      "te": [
        "వేరుశనగ",
        "పల్లీలు"
      ],
      "tanglish": [],
      "expands_to": [
        "groundnut",
        "oil",
        "cold pressed",
        "oil expeller"
      ]
    },
    {
      "id": "mango",
      "en_canonical": "mango",
      "en": [
        "mango pulp",
        "aam"
      ],
      "te": [
        "మామిడి"
      ],
      "tanglish": [
        "maamidi"
      ],
      "expands_to": [
        "mango",
        "fruit"
      ]
    },
    {
      "id": "vegetables",
      "en_canonical": "vegetables",
      "en": [
        "vegetable farming",
        "horticulture"
      ],
      "te": [
        "కూరగాయలు"
      ],
      "tanglish": [
        "kooragayalu"
      ],
      "expands_to": [
        "vegetables",
        "horticulture"
      ]
    },
    {
      "id": "food-processing",
      "en_canonical": "food processing",
      "en": [
        "food industry",
        "agro processing",
        "pickle",
        "avakaya",
        "masala",
        "bakery"
      ],
      "te": [
        "ఆహార శుద్ధి",
        "ఫుడ్ ప్రాసెసింగ్",
        "ఆవకాయ"
      ],
      "tanglish": [
        "aahara suddhi"
      ],
      "expands_to": [
        "food processing",
        "agro processing",
        "millet",
        "bakery",
        "masala",
        "oil"
      ]
    },
    {
      "id": "business",
      "en_canonical": "business",
      "en": [
        "enterprise",
        "entrepreneurship",
        "startup",
        "self employment",
        "own business"
      ],
      "te": [
        "వ్యాపారం",
        "సొంత వ్యాపారం",
        "పరిశ్రమ"
      ],
      "tanglish": [
        "parishrama"
      ],
      "expands_to": [
        "business",
        "entrepreneurship",
        "msme",
        "enterprise"
      ]
    },
    {
      "id": "msme",
      "en_canonical": "MSME",
      "en": [
        "micro small and medium enterprises",
        "small industry",
        "small business"
      ],
      "te": [
        "సూక్ష్మ చిన్న మధ్య తరహా పరిశ్రమలు",
        "చిన్న పరిశ్రమ"
      ],
      "tanglish": [
        "chinna parishrama"
      ],
      "expands_to": [
        "msme",
        "enterprise",
        "small industries"
      ]
    },
    {
      "id": "loan",
      "en_canonical": "loan",
      "en": [
        "credit",
        "finance",
        "bank loan",
        "mudra"
      ],
      "te": [
        "రుణం",
        "అప్పు",
        "బ్యాంకు రుణం"
      ],
      "tanglish": [
        "banku runam"
      ],
      "expands_to": [
        "loan",
        "credit",
        "mudra",
        "bank",
        "margin money"
      ]
    },
    {
      "id": "subsidy",
      "en_canonical": "subsidy",
      "en": [
        "grant",
        "financial assistance",
        "margin money"
      ],
      "te": [
        "సబ్సిడీ",
        "రాయితీ",
        "ఆర్థిక సహాయం"
      ],
      "tanglish": [],
      "expands_to": [
        "subsidy",
        "margin money",
        "government scheme"
      ]
    },
    {
      "id": "government-scheme",
      "en_canonical": "government scheme",
      "en": [
        "scheme",
        "yojana",
        "sarkari scheme",
        "government support"
      ],
      "te": [
        "ప్రభుత్వ పథకం",
        "పథకం",
        "ప్రభుత్వ సహాయం"
      ],
      "tanglish": [
        "prabhutva padhakam",
        "padhakam",
        "sarkari padhakam"
      ],
      "expands_to": [
        "government scheme",
        "subsidy",
        "yojana"
      ]
    },
    {
      "id": "job",
      "en_canonical": "job",
      "en": [
        "employment",
        "work",
        "vacancy",
        "career"
      ],
      "te": [
        "ఉద్యోగం",
        "పని",
        "కొలువు"
      ],
      "tanglish": [],
      "expands_to": [
        "employment",
        "skill"
      ]
    },
    {
      "id": "skill",
      "en_canonical": "skill",
      "en": [
        "skills",
        "trade",
        "vocational"
      ],
      "te": [
        "నైపుణ్యం",
        "నైపుణ్యాలు"
      ],
      "tanglish": [],
      "expands_to": [
        "skill",
        "training",
        "certification"
      ]
    },
    {
      "id": "training",
      "en_canonical": "training",
      "en": [
        "course",
        "class",
        "coaching",
        "learn",
        "apprenticeship"
      ],
      "te": [
        "శిక్షణ",
        "కోర్సు",
        "నేర్చుకోవడం"
      ],
      "tanglish": [
        "shikshana"
      ],
      "expands_to": [
        "training",
        "skill",
        "certification",
        "training provider",
        "iti"
      ]
    },
    {
      "id": "certification",
      "en_canonical": "certification",
      "en": [
        "certificate",
        "licence",
        "qualification",
        "nsqf"
      ],
      "te": [
        "సర్టిఫికెట్",
        "ధృవీకరణ పత్రం"
      ],
      "tanglish": [],
      "expands_to": [
        "certification",
        "certificate",
        "training"
      ]
    },
    {
      "id": "iti",
      "en_canonical": "industrial training institute",
      "en": [
        "iti",
        "polytechnic",
        "technical school"
      ],
      "te": [
        "ఐటీఐ",
        "పారిశ్రామిక శిక్షణ సంస్థ"
      ],
      "tanglish": [],
      "expands_to": [
        "industrial training institute",
        "training",
        "polytechnic",
        "certification"
      ]
    },
    {
      "id": "education",
      "en_canonical": "education",
      "en": [
        "college",
        "university",
        "degree",
        "study",
        "institution"
      ],
      "te": [
        "విద్య",
        "కళాశాల",
        "చదువు",
        "విశ్వవిద్యాలయం"
      ],
      "tanglish": [
        "vishwavidyalayam"
      ],
      "expands_to": [
        "university",
        "institute",
        "college",
        "polytechnic"
      ]
    },
    {
      "id": "solar",
      "en_canonical": "solar",
      "en": [
        "solar panel",
        "rooftop solar",
        "renewable energy",
        "surya ghar",
        "solar technician",
        "rooftop solar installer",
        "solar installer",
        "pv system integrator",
        "suryamitra",
        "solar pv"
      ],
      "te": [
        "సౌర విద్యుత్",
        "సోలార్"
      ],
      "tanglish": [],
      "expands_to": [
        "solar",
        "solar panel",
        "renewable energy",
        "rooftop"
      ]
    },
    {
      "id": "electric-vehicle",
      "en_canonical": "electric vehicle",
      "en": [
        "ev",
        "e vehicle",
        "ev charging",
        "ev repair",
        "ev technician",
        "ev service technician",
        "electric vehicle mechanic",
        "ev repair specialist",
        "battery technician",
        "ev mechanic"
      ],
      "te": [
        "ఎలక్ట్రిక్ వాహనం",
        "ఈవీ"
      ],
      "tanglish": [
        "electric vahanam"
      ],
      "expands_to": [
        "electric vehicle",
        "ev",
        "charging",
        "battery"
      ]
    },
    {
      "id": "battery",
      "en_canonical": "battery",
      "en": [
        "batteries",
        "battery recycling",
        "cell",
        "lithium"
      ],
      "te": [
        "బ్యాటరీ"
      ],
      "tanglish": [],
      "expands_to": [
        "battery",
        "electric vehicle",
        "recycling"
      ]
    },
    {
      "id": "manufacturing",
      "en_canonical": "manufacturing",
      "en": [
        "factory",
        "production",
        "unit",
        "making"
      ],
      "te": [
        "తయారీ",
        "ఉత్పత్తి",
        "కర్మాగారం"
      ],
      "tanglish": [],
      "expands_to": [
        "manufacturing",
        "fabrication",
        "production",
        "unit"
      ]
    },
    {
      "id": "construction",
      "en_canonical": "construction",
      "en": [
        "building",
        "civil work",
        "contractor",
        "skilled trades"
      ],
      "te": [
        "నిర్మాణం",
        "భవన నిర్మాణం"
      ],
      "tanglish": [],
      "expands_to": [
        "construction",
        "skilled trades",
        "masonry",
        "real estate"
      ]
    },
    {
      "id": "textiles",
      "en_canonical": "textiles",
      "en": [
        "textile",
        "apparel",
        "handloom",
        "fabric"
      ],
      "te": [
        "వస్త్ర పరిశ్రమ",
        "చేనేత"
      ],
      "tanglish": [
        "vastra parishrama"
      ],
      "expands_to": [
        "textiles",
        "apparel",
        "garment"
      ]
    },
    {
      "id": "tourism",
      "en_canonical": "tourism",
      "en": [
        "homestay",
        "hospitality",
        "travel",
        "guest house"
      ],
      "te": [
        "పర్యాటకం",
        "హోమ్‌స్టే"
      ],
      "tanglish": [],
      "expands_to": [
        "tourism",
        "hospitality",
        "homestay"
      ]
    },
    {
      "id": "export",
      "en_canonical": "export",
      "en": [
        "exports",
        "foreign market",
        "shipping abroad"
      ],
      "te": [
        "ఎగుమతి",
        "ఎగుమతులు"
      ],
      "tanglish": [],
      "expands_to": [
        "export",
        "export channel"
      ]
    },
    {
      "id": "market",
      "en_canonical": "market",
      "en": [
        "mandi",
        "selling",
        "buyers",
        "market channel"
      ],
      "te": [
        "మార్కెట్",
        "మార్కెటింగ్",
        "అమ్మకం"
      ],
      "tanglish": [],
      "expands_to": [
        "market",
        "marketplace",
        "retail"
      ]
    },
    {
      "id": "bank",
      "en_canonical": "bank",
      "en": [
        "banking",
        "financial institution",
        "cooperative bank"
      ],
      "te": [
        "బ్యాంకు",
        "బ్యాంక్"
      ],
      "tanglish": [
        "banku"
      ],
      "expands_to": [
        "bank",
        "financial institution",
        "credit"
      ]
    },
    {
      "id": "district",
      "en_canonical": "district",
      "en": [
        "districts",
        "area",
        "region",
        "place"
      ],
      "te": [
        "జిల్లా",
        "జిల్లాలు",
        "ప్రాంతం"
      ],
      "tanglish": [],
      "expands_to": [
        "district"
      ]
    },
    {
      "id": "machinery",
      "en_canonical": "machinery",
      "en": [
        "machine",
        "equipment",
        "plant"
      ],
      "te": [
        "యంత్రం",
        "యంత్రాలు",
        "పరికరాలు"
      ],
      "tanglish": [],
      "expands_to": [
        "machinery",
        "equipment",
        "machine"
      ]
    },
    {
      "id": "china",
      "en_canonical": "China-inspired opportunity",
      "en": [
        "chinese model",
        "china business model",
        "china inspired"
      ],
      "te": [
        "చైనా"
      ],
      "tanglish": [],
      "expands_to": [
        "live selling",
        "group buying",
        "creator commerce",
        "social marketplace commerce",
        "digital catalog",
        "dress rental",
        "homestay",
        "odop",
        "farmer producer"
      ]
    },
    {
      "id": "women-entrepreneur",
      "en_canonical": "women entrepreneur",
      "en": [
        "woman entrepreneur",
        "mahila",
        "self help group",
        "shg"
      ],
      "te": [
        "మహిళా పారిశ్రామికవేత్త",
        "మహిళలు",
        "స్వయం సహాయక సంఘం"
      ],
      "tanglish": [
        "mahila",
        "swayam sahayaka sangam"
      ],
      "expands_to": [
        "women",
        "mahila",
        "entrepreneurship"
      ]
    },
    {
      "id": "cnc",
      "en_canonical": "cnc",
      "en": [
        "cnc operator",
        "cnc machinist",
        "vmc operator",
        "turn mill operator",
        "cnc programming",
        "lathe operator"
      ],
      "te": [
        "సీఎన్‌సీ ఆపరేటర్"
      ],
      "tanglish": [],
      "expands_to": [
        "cnc machine operator",
        "lathe operation",
        "machinery"
      ]
    },
    {
      "id": "industrial-electrician",
      "en_canonical": "industrial electrician",
      "en": [
        "factory electrician",
        "maintenance electrician",
        "plant electrician",
        "electrical fitter",
        "motor control",
        "switchgear"
      ],
      "te": [],
      "tanglish": [],
      "expands_to": [
        "industrial electrician",
        "electrician",
        "power distribution"
      ]
    },
    {
      "id": "plc-automation",
      "en_canonical": "plc automation",
      "en": [
        "plc",
        "plc programmer",
        "scada",
        "automation technician",
        "hmi",
        "control systems",
        "industrial automation technician"
      ],
      "te": [],
      "tanglish": [],
      "expands_to": [
        "plc programming",
        "industrial automation",
        "automation"
      ]
    },
    {
      "id": "false-ceiling",
      "en_canonical": "false ceiling",
      "en": [
        "pop ceiling",
        "gypsum board",
        "gypsum",
        "drywall",
        "ceiling technician",
        "pop plasterer",
        "gypsum finisher",
        "suspended ceiling"
      ],
      "te": [],
      "tanglish": [],
      "expands_to": [
        "false ceiling",
        "masonry"
      ]
    },
    {
      "id": "aluminium-fabrication",
      "en_canonical": "aluminium fabrication",
      "en": [
        "aluminium fabricator",
        "aluminium fitter",
        "upvc window",
        "fenestration",
        "glazier",
        "glass installer",
        "window fitter",
        "facade glass"
      ],
      "te": [],
      "tanglish": [],
      "expands_to": [
        "aluminium fabrication",
        "fabrication"
      ]
    },
    {
      "id": "borewell",
      "en_canonical": "borewell",
      "en": [
        "borewell technician",
        "rig operator",
        "groundwater drilling",
        "driller",
        "bore well"
      ],
      "te": [],
      "tanglish": [],
      "expands_to": [
        "borewell",
        "borewell drilling"
      ]
    },
    {
      "id": "pump-technician",
      "en_canonical": "pump technician",
      "en": [
        "submersible pump",
        "water pump mechanic",
        "pump fitter",
        "motor winder",
        "pump repair"
      ],
      "te": [],
      "tanglish": [],
      "expands_to": [
        "submersible pump",
        "pump"
      ]
    },
    {
      "id": "heavy-equipment-operator",
      "en_canonical": "heavy equipment operator",
      "en": [
        "crane operator",
        "excavator operator",
        "jcb",
        "jcb driver",
        "earthmover",
        "road roller",
        "paver operator",
        "grader operator",
        "backhoe",
        "tower crane",
        "rigging"
      ],
      "te": [],
      "tanglish": [],
      "expands_to": [
        "material handling",
        "construction"
      ]
    },
    {
      "id": "waterproofing",
      "en_canonical": "waterproofing",
      "en": [
        "waterproofing technician",
        "leakage treatment",
        "damp proofing",
        "terrace waterproofing"
      ],
      "te": [],
      "tanglish": [],
      "expands_to": [
        "painting",
        "construction"
      ]
    },
    {
      "id": "modular-kitchen",
      "en_canonical": "modular kitchen",
      "en": [
        "modular kitchen installer",
        "cabinetry technician",
        "kitchen carpenter",
        "modular furniture fitter"
      ],
      "te": [],
      "tanglish": [],
      "expands_to": [
        "carpentry"
      ]
    },
    {
      "id": "roofing",
      "en_canonical": "roofing",
      "en": [
        "roofing technician",
        "sheet roofing",
        "industrial shed erector",
        "roofing fabricator"
      ],
      "te": [],
      "tanglish": [],
      "expands_to": [
        "construction",
        "fabrication"
      ]
    }
  ]
});
