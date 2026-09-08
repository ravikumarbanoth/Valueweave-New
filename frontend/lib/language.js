"use client";

import { useEffect, useState } from 'react';

/**
 * Lightweight UI language support.
 *
 * English is the default. Telugu can be selected.
 * Language preference is persisted in localStorage.
 * Translations are applied to UI labels only, not to factual knowledge.
 * document.lang is updated to reflect the current language.
 *
 * Fallback hierarchy:
 *   1. Telugu translation (if selected)
 *   2. English translation
 *   3. Human-readable fallback string (if provided) or cleanly formatted key
 *   NEVER: raw i18n key with namespace prefix
 */

const SUPPORTED_LANGUAGES = ['en', 'te'];
export { SUPPORTED_LANGUAGES };
export const DEFAULT_LANGUAGE = 'en';
const STORAGE_KEY = 'vw_ui_language';
const LANGUAGE_EVENT = 'vw:language-change';

/**
 * Get the current UI language from localStorage or return default.
 * Only returns a supported language; unknown values default to English.
 */
export function getStoredLanguage() {
  if (typeof window === 'undefined') return DEFAULT_LANGUAGE;
  const stored = localStorage.getItem(STORAGE_KEY);
  return SUPPORTED_LANGUAGES.includes(stored) ? stored : DEFAULT_LANGUAGE;
}

/**
 * Set and persist the UI language. Updates document.lang.
 */
export function setLanguage(lang) {
  if (!SUPPORTED_LANGUAGES.includes(lang)) return;
  if (typeof window !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, lang);
    document.documentElement.lang = lang;
    window.dispatchEvent(new CustomEvent(LANGUAGE_EVENT, { detail: lang }));
  }
}

export function useLanguage() {
  const [language, setCurrentLanguage] = useState(DEFAULT_LANGUAGE);

  useEffect(() => {
    const updateLanguage = () => setCurrentLanguage(getStoredLanguage());
    updateLanguage();
    window.addEventListener(LANGUAGE_EVENT, updateLanguage);
    return () => window.removeEventListener(LANGUAGE_EVENT, updateLanguage);
  }, []);

  return {
    language,
    setLanguage,
    t: (key, fallback = null) => t(key, language, fallback),
  };
}

/**
 * Get the label for a language code. Used in the language selector.
 */
export function getLanguageLabel(lang) {
  return {
    en: 'English',
    te: 'తెలుగు',
  }[lang] || lang;
}

/**
 * Format a missing key into a clean, human-readable string.
 * Strips namespace prefix (e.g., "nav.", "btn.") and converts kebab/snake_case to Title Case.
 */
export function humanizeKey(key) {
  if (!key || typeof key !== 'string') return '';
  const stripped = key.replace(/^[a-zA-Z0-9_-]+\./, '');
  return stripped
    .replace(/[-_.]+/g, ' ')
    .trim()
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Translate a key using the requested or current language.
 *
 * Fallback hierarchy:
 *   1. Translation in active language
 *   2. Translation in English
 *   3. Explicit fallback string (if provided)
 *   4. Clean humanized label (never raw namespace key)
 */
export function t(key, language = null, fallback = null) {
  if (!key) return '';
  const lang = language || getStoredLanguage();
  const translations = TRANSLATION_DICTIONARY[lang];
  if (translations && translations[key]) {
    return translations[key];
  }
  // Fallback to English
  const english = TRANSLATION_DICTIONARY[DEFAULT_LANGUAGE];
  if (english && english[key]) {
    return english[key];
  }
  // Fallback to provided human-readable string or clean formatted key
  if (fallback && typeof fallback === 'string') {
    return fallback;
  }
  return humanizeKey(key);
}

/**
 * Curated translations for ValueWeave UI.
 * Only UI labels and reusable strings.
 * Factual knowledge (skills, schemes, districts, etc.) are NOT translated.
 */
export const TRANSLATION_DICTIONARY = {
  en: {
    // Navigation
    'nav.discover': 'Discover',
    'nav.districts': 'Districts',
    'nav.district': 'Districts',
    'nav.readiness': 'Industrial Readiness',
    'nav.industrial-readiness': 'Industrial Readiness',
    'nav.industrial_readiness': 'Industrial Readiness',
    'nav.manufacturing': 'Manufacturing',
    'nav.scale': 'Scale',
    'nav.network': 'Network',
    'nav.ai': 'AI',
    'nav.home': 'Home',
    'nav.about': 'About',
    'nav.ideas': 'Idea Library',
    'nav.research': 'Research',
    'nav.opportunity-radar': 'Opportunity Radar',
    'nav.opportunity_radar': 'Opportunity Radar',
    'nav.collaborators': 'Collaborators',
    'nav.explore': 'Explore',
    'nav.privacy': 'Privacy',
    'nav.terms': 'Terms',
    'nav.signin': 'Sign in',
    'nav.join': 'Join ValueWeave →',
    'nav.join_short': 'Join',
    'nav.join_full': 'Join ValueWeave',
    'nav.join_arrow': 'Join ValueWeave →',
    'nav.feed': 'Feed',
    'nav.post': 'Post',
    'nav.inbox': 'Inbox',
    'nav.profile': 'Profile',
    'nav.me': 'Me',
    'nav.signout': 'Sign out',
    'nav.my_profile': 'My Profile',
    'nav.connections': 'Connections',
    'nav.all_knowledge': 'All knowledge',
    'nav.back_to_home': 'Back to home',
    'nav.back_home': 'Back home',

    // Search
    'search.hero_label': 'What opportunity are you looking for today?',
    'search.placeholder': 'What do you want to learn, build or earn?',
    'search.no_results': "We couldn't find what you're looking for.",
    'search.try_different': 'Try a different search',
    'search.search_everything': 'Search everything',
    'search.button': 'Search',
    'search.try': 'Try:',
    'search.suggestions': 'Suggestions',
    'search.see_all': 'See everything for',
    'search.understood_as': 'Understood as',
    'search.results_for': 'results for',
    'search.result_for': 'result for',
    'search.showing': 'showing',
    'search.of': 'of',
    'search.clear': 'Clear',
    'search.detected_intent': 'Detected intent:',
    'search.learning_training': 'a learning or training search',
    'search.jobs_employment': 'a jobs and employment search',
    'search.service_repair': 'a service or repair search',
    'search.question': 'a question',
    'search.results_outside': 'results outside',
    'search.search_everything_arrow': 'search everything →',

    // Home & Audiences / Goals
    'home.bharat_edition': 'Now Open · Bharat Edition',
    'home.google_auth': 'Google-authenticated profiles',
    'home.mobile_first': 'Mobile-first',
    'home.free_to_join': 'Free to join',
    'home.welcome_back': 'Welcome back',
    'home.welcome_context_prefix': 'You were here as a',
    'home.welcome_context_suffix': 'so we nudge matching results up. Nothing is hidden.',
    'home.popular_goals': 'Popular goals',
    'home.tell_us_who': 'Or tell us who you are',
    'home.who_are_you': 'Who are you now?',
    'home.change': 'Change',
    'home.forget_me': 'Forget me',
    'home.pickup_left': 'Pick up where you left off →',
    'home.cta_discover': 'Discover Yourself',
    'home.cta_ideas': 'Explore Ideas',
    'home.cta_network': 'Find Collaborators',

    // Audiences
    'audience.student': 'Student',
    'audience.job-seeker': 'Job Seeker',
    'audience.entrepreneur': 'Entrepreneur',
    'audience.farmer': 'Farmer',
    'audience.skilled-worker': 'Skilled Worker',
    'audience.business-owner': 'Business Owner',

    // Goals
    'goal.looking_for_a_job': 'Looking for a job',
    'goal.start_a_business': 'Start a business',
    'goal.learn_a_skill': 'Learn a skill',
    'goal.government_schemes': 'Government schemes',
    'goal.agriculture': 'Agriculture',
    'goal.ai_careers': 'AI careers',
    'goal.manufacturing': 'Manufacturing',
    'goal.my_district': 'My district',
    'goal.explore_everything': 'Explore everything',

    // Why We Built This & Gaps
    'home.why_chip': 'WHY WE BUILT THIS',
    'home.why_title_1': 'Skill is not the problem.',
    'home.why_title_2': 'Knowing where to take it is.',
    'home.why_desc': 'Plenty of people can do the work. Far fewer know which scheme applies to them, who is hiring nearby, or what it costs to start on their own.',
    'home.why_summary': 'So we researched it and put it in one place: what to learn, what to start, which schemes apply, and who is nearby.',
    'home.gap_1_title': 'Talent without visibility',
    'home.gap_1_desc': 'An electrician in Warangal, a coder in Vizag, a baker in Guntur. Good at the work, unknown to the people who would hire or partner with them.',
    'home.gap_2_title': 'Ideas without teams',
    'home.gap_2_desc': 'You can have a good idea and still not know a single person nearby who can help you build it.',
    'home.gap_3_title': 'Trust without proof',
    'home.gap_3_desc': 'Job sites reward job titles. Freelance sites reward the lowest bid. Neither shows you what someone can actually do.',

    // Discover Yourself Section
    'home.discover_chip': 'FREE ASSESSMENT',
    'home.discover_heading_1': 'Not sure what suits you?',
    'home.discover_heading_2': 'Answer a few questions.',
    'home.discover_desc': 'Seven minutes, free. Tell us your district, what you are interested in and what you could invest, and we will suggest business ideas that fit.',
    'home.discover_bullet_1': 'Which kind of work suits you — building, leading, selling or planning',
    'home.discover_bullet_2': 'Business ideas that suit your district',
    'home.discover_bullet_3': 'Only ideas you could actually afford, from ₹30,000 upwards',
    'home.discover_bullet_4': 'Post your best idea and let people ask to join you',
    'home.take_assessment': 'Take the free assessment →',

    // Archetypes
    'archetype.innovator': 'Innovator',
    'archetype.innovator_desc': 'Product & Strategy Lead — spots opportunities others miss.',
    'archetype.leader': 'Leader',
    'archetype.leader_desc': 'CEO / Managing Director — sets direction and owns outcomes.',
    'archetype.builder': 'Builder',
    'archetype.builder_desc': 'Operations & Delivery Lead — makes things actually run.',
    'archetype.influencer': 'Influencer',
    'archetype.influencer_desc': 'Marketing & Sales Lead — tells the story, builds the brand.',

    // Built for India's Builders
    'home.fits_chip': 'WHATEVER YOU DO',
    'home.fits_title_1': 'Whatever you already do,',
    'home.fits_title_2': 'it fits here.',
    'sector.ai_tech': 'AI & Tech',
    'sector.local_biz': 'Local Biz',
    'sector.ev_tech': 'EV Tech',
    'sector.drone': 'Drone',
    'sector.agriculture': 'Agriculture',
    'sector.student': 'Student',
    'sector.trades': 'Trades',
    'sector.digital': 'Digital',
    'home.explore_opps': 'Explore opportunities →',

    // Final CTA
    'home.ready_chip': 'READY?',
    'home.step_heading_1': 'Take the first step',
    'home.step_heading_2': 'from where you are.',
    'home.step_subheading': 'Free. Sign in with Google — no password to remember.',
    'home.join_sparkle': 'Join ValueWeave ✨',

    // Stats
    'stats.who_is_here': 'Who is here so far',
    'stats.visitors': 'Visitors',
    'stats.assessments': 'Discover Profiles',
    'stats.opportunities': 'Open Opportunities',
    'stats.collaborators': 'Collaborators',
    'stats.districts': 'Districts Covered',
    'stats.launching_soon': 'Platform launching soon — be among the first to join.',

    // How It Works
    'how_it_works.chip': 'FIVE STEPS',
    'how_it_works.title': 'How this works',
    'how_it_works.subtitle': 'Five steps from self-discovery to launching your venture.',
    'step.step1_title': 'Discover Yourself',
    'step.step1_desc': 'Find your founder archetype and strengths',
    'step.step2_title': 'Get Personalized Ideas',
    'step.step2_desc': 'Business ideas matched to your district and budget',
    'step.step3_title': 'Explore District Opportunities',
    'step.step3_desc': 'Real opportunities in your own district',
    'step.step4_title': 'Find Collaborators',
    'step.step4_desc': 'Connect with co-founders and partners',
    'step.step5_title': 'Build Your Venture',
    'step.step5_desc': 'Launch your project from your hometown',

    // Journey & Milestones
    'journey.chip': 'STEP BY STEP',
    'journey.title': 'What to do next',
    'journey.subtitle': "From first click to funded venture — here's the roadmap.",
    'milestone.day1_period': 'Day 1',
    'milestone.day1_title': 'Answer a few questions',
    'milestone.day1_desc': 'Answer a few questions and we will suggest ideas that suit you.',
    'milestone.week1_period': 'Week 1',
    'milestone.week1_title': 'Look around',
    'milestone.week1_desc': 'Browse business ideas matched to your district, your budget and what you can do.',
    'milestone.week2_period': 'Week 2',
    'milestone.week2_title': 'Find people nearby',
    'milestone.week2_desc': 'Find people nearby who have the skills you do not.',
    'milestone.month1_period': 'Month 1',
    'milestone.month1_title': 'Post what you are building',
    'milestone.month1_desc': 'Post what you are building, and let people ask to join you.',
    'milestone.month3_period': 'Month 3',
    'milestone.month3_title': 'Grow it',
    'milestone.month3_desc': 'Work out where to sell, what it costs to grow, and who can fund it.',

    // Opportunities
    'opps.chip': 'LIVE NOW',
    'opps.title': 'Featured Opportunities',
    'opps.subtitle': 'Real business opportunities from across Telangana and Andhra Pradesh.',
    'opps.view_all': 'View All Opportunities →',

    // Activity
    'activity.chip': 'LIVE ACTIVITY',
    'activity.title': "What's Happening Now",
    'activity.subtitle': 'Anonymous activity from ValueWeave builders across India.',

    // Onboarding / Get Started
    'onboarding.title': 'What are you here to do?',
    'onboarding.student': 'I want to learn a skill',
    'onboarding.entrepreneur': 'I want to start a business',
    'onboarding.job_seeker': "I'm looking for work",
    'onboarding.farmer': "I'm in agriculture",
    'onboarding.corporate': "I'm building a team",
    'getstarted.chip': 'CREATING AN ACCOUNT',
    'getstarted.heading_1': 'What brings you to',
    'getstarted.subheading': 'An account is for working with people — collaborators, teams and posting your own ideas. Pick what fits best.',
    'getstarted.look_around_title': 'Just want to look around?',
    'getstarted.look_around_desc': 'Every skill, scheme, business idea and district is free to read — no account, no sign-in.',
    'getstarted.explore_free': 'Explore without an account →',
    'getstarted.already_member': 'Already a member?',
    'getstarted.signin_link': 'Sign in →',
    'getstarted.continue_google': 'Continue with Google →',
    'getstarted.google_note': "We'll sign you in with Google. No password needed.",
    'getstarted.redirecting': 'Redirecting…',

    // Sign In
    'signin.title': 'Welcome back',
    'signin.subtitle': 'Sign in to your ValueWeave account to access your dashboard, connections, and opportunities.',
    'signin.continue_google': 'Continue with Google',
    'signin.new_to_valueweave': 'New to ValueWeave?',
    'signin.create_profile': 'Create your profile →',

    // Common buttons
    'btn.next': 'Next →',
    'btn.back': '← Back',
    'btn.submit': 'Submit',
    'btn.close': 'Close',
    'btn.learn_more': 'Learn more',
    'btn.explore': 'Explore',
    'btn.view': 'View',
    'btn.get_started': 'Get Started',

    // Language selector
    'language.select': 'Language',
    'language.english': 'English',
    'language.telugu': 'తెలుగు',

    // Common UI
    'ui.menu': 'Menu',
    'ui.close_menu': 'Close menu',
    'ui.open_menu': 'Open menu',
    'ui.loading': 'Loading...',
    'ui.error': 'Something went wrong',
    'ui.try_again': 'Try again',
    'ui.back_to_home': 'Back to home',

    // Footer
    'footer.founded_by': 'Founded by Ravi Kumar Banoth',
    'footer.built_in_bharat': 'Built in Bharat.',
    'footer.contact': 'Contact',
    'footer.follow_title': 'Follow ValueWeave',
    'footer.follow_sub': "Follow the journey of Bharat's next builders.",

    // Founder / Attribution
    'founder.title': 'Founder, ValueWeave',
    'founder.founder': 'Founder',
    'founder.founded_by': 'Founded by Ravi Kumar Banoth',
    'about.founder_name': 'Ravi Kumar Banoth',
    'about.founder_title': 'Founder, ValueWeave',
    'about.founder_bio': 'ValueWeave was founded by Ravi Kumar Banoth with a vision to make information about careers, skills, businesses, government schemes, industries and local opportunities easier to discover and act upon.',
  },
  te: {
    // Navigation
    'nav.discover': 'కనుగొనండి',
    'nav.districts': 'జిల్లాలు',
    'nav.district': 'జిల్లాలు',
    'nav.readiness': 'పారిశ్రామిక సంసిద్ధత',
    'nav.industrial-readiness': 'పారిశ్రామిక సంసిద్ధత',
    'nav.industrial_readiness': 'పారిశ్రామిక సంసిద్ధత',
    'nav.manufacturing': 'తయారీ',
    'nav.scale': 'స్కేల్',
    'nav.network': 'నెట్‌వర్క్',
    'nav.ai': 'ఏఐ',
    'nav.home': 'హోమ్',
    'nav.about': 'గురించి',
    'nav.ideas': 'ఐడియా లైబ్రరీ',
    'nav.research': 'పరిశోధన',
    'nav.opportunity-radar': 'అవకాశ రాడార్',
    'nav.opportunity_radar': 'అవకాశ రాడార్',
    'nav.collaborators': 'సహకారులు',
    'nav.explore': 'అన్వేషించండి',
    'nav.privacy': 'గోప్యత',
    'nav.terms': 'నిబంధనలు',
    'nav.signin': 'సైన్ ఇన్',
    'nav.join': 'వాల్యూవీవ్‌కు చేరండి →',
    'nav.join_short': 'చేరండి',
    'nav.join_full': 'వాల్యూవీవ్‌కు చేరండి',
    'nav.join_arrow': 'వాల్యూవీవ్‌కు చేరండి →',
    'nav.feed': 'ఫీడ్',
    'nav.post': 'పోస్ట్',
    'nav.inbox': 'ఇన్‌బాక్స్',
    'nav.profile': 'ప్రొఫైల్',
    'nav.me': 'నేను',
    'nav.signout': 'సైన్ అవుట్',
    'nav.my_profile': 'నా ప్రొఫైల్',
    'nav.connections': 'కనెక్షన్‌లు',
    'nav.all_knowledge': 'అన్ని అంశాలు',
    'nav.back_to_home': 'హోమ్‌కు తిరిగి వెళ్లండి',
    'nav.back_home': 'హోమ్‌కు వెళ్లండి',

    // Search
    'search.hero_label': 'మీరు ఈరోజు ఏ అవకాశాన్ని వెతుకుతున్నారు?',
    'search.placeholder': 'మీరు ఏమి నేర్చుకోవాలి, నిర్మించాలి లేదా సంపాదించాలనుకుంటున్నారు?',
    'search.no_results': 'మీరు చేసిన శోధన కోసం ఫలితాలు లేవు.',
    'search.try_different': 'వేరే శోధన ప్రయత్నించండి',
    'search.search_everything': 'అన్నిటిని శోధించండి',
    'search.button': 'శోధించండి',
    'search.try': 'ప్రయత్నించండి:',
    'search.suggestions': 'సూచనలు',
    'search.see_all': 'వీటి కోసం అన్నింటినీ చూడండి',
    'search.understood_as': 'ఇలా అర్థం చేసుకున్నాము',
    'search.results_for': 'ఫలితాలు',
    'search.result_for': 'ఫలితం',
    'search.showing': 'చూపిస్తున్నవి',
    'search.of': 'మొత్తం',
    'search.clear': 'క్లియర్',
    'search.detected_intent': 'గుర్తించిన ఉద్దేశం:',
    'search.learning_training': 'నేర్చుకోవడం లేదా శిక్షణ శోధన',
    'search.jobs_employment': 'ఉద్యోగాలు మరియు ఉపాధి శోధన',
    'search.service_repair': 'సర్వీస్ లేదా మరమ్మత్తు శోధన',
    'search.question': 'ఒక ప్రశ్న',
    'search.results_outside': 'బయట ఉన్న ఫలితాలు',
    'search.search_everything_arrow': 'అన్నీ శోధించండి →',

    // Home & Audiences / Goals
    'home.bharat_edition': 'ఇప్పుడు అందుబాటులో ఉంది · భారత్ ఎడిషన్',
    'home.google_auth': 'గూగుల్ ధృవీకరించిన ప్రొఫైల్స్',
    'home.mobile_first': 'మొబైల్-ఫస్ట్ డిజైన్',
    'home.free_to_join': 'చేరడం పూర్తిగా ఉచితం',
    'home.welcome_back': 'స్వాగతం',
    'home.welcome_context_prefix': 'మీరు ఇంతకుముందు',
    'home.welcome_context_suffix': 'గా చూశారు, కాబట్టి తగిన ఫలితాలు ముందు చూపిస్తున్నాము. ఏదీ దాచబడలేదు.',
    'home.popular_goals': 'ప్రజాదరణ పొందిన లక్ష్యాలు',
    'home.tell_us_who': 'లేదా మీ గురించి చెప్పండి',
    'home.who_are_you': 'మీరు ప్రస్తుతం ఎవరు?',
    'home.change': 'మార్చు',
    'home.forget_me': 'గుర్తుంచుకోవద్దు',
    'home.pickup_left': 'ఆపిన చోటు నుండి కొనసాగించండి →',
    'home.cta_discover': 'మిమ్మల్ని మీరు తెలుసుకోండి',
    'home.cta_ideas': 'ఆలోచనలను అన్వేషించండి',
    'home.cta_network': 'సహకారులను కనుగొనండి',

    // Audiences
    'audience.student': 'విద్యార్థి',
    'audience.job-seeker': 'ఉద్యోగార్ధి',
    'audience.entrepreneur': 'వ్యాపారవేత్త',
    'audience.farmer': 'రైతు',
    'audience.skilled-worker': 'నైపుణ్యం కలిగిన వర్కర్',
    'audience.business-owner': 'వ్యాపార యజమాని',

    // Goals
    'goal.looking_for_a_job': 'ఉద్యోగం కోసం చూస్తున్నారా',
    'goal.start_a_business': 'వ్యాపారం ప్రారంభించండి',
    'goal.learn_a_skill': 'నైపుణ్యం నేర్చుకోండి',
    'goal.government_schemes': 'ప్రభుత్వ పథకాలు',
    'goal.agriculture': 'వ్యవసాయం',
    'goal.ai_careers': 'ఏఐ కెరీర్లు',
    'goal.manufacturing': 'తయారీ రంగం',
    'goal.my_district': 'నా జిల్లా',
    'goal.explore_everything': 'అన్నీ అన్వేషించండి',

    // Why We Built This & Gaps
    'home.why_chip': 'మేము దీన్ని ఎందుకు నిర్మించాము',
    'home.why_title_1': 'నైపుణ్యం సమస్య కాదు.',
    'home.why_title_2': 'దాన్ని ఎక్కడికి తీసుకెళ్లాలో తెలుసుకోవడమే ముఖ్యం.',
    'home.why_desc': 'పని చేయగల సామర్థ్యం చాలామందికి ఉంది. కానీ ఏ పథకం వర్తిస్తుందో, సమీపంలో ఎవరు రిక్రూట్ చేసుకుంటున్నారో లేదా స్వంతంగా ప్రారంభించడానికి ఎంత ఖర్చవుతుందో కొద్దిమందికే తెలుసు.',
    'home.why_summary': 'అందుకే మేము పరిశోధించి అన్నింటినీ ఒకే చోట చేర్చాము: ఏమి నేర్చుకోవాలి, ఏమి ప్రారంభించాలి, ఏ పథకాలు వర్తిస్తాయి మరియు సమీపంలో ఎవరు ఉన్నారు.',
    'home.gap_1_title': 'గుర్తింపు లేని ప్రతిభ',
    'home.gap_1_desc': 'వరంగల్‌లో ఎలక్ట్రీషియన్, వైజాగ్‌లో కోడర్, గుంటూరులో బేకర్. పనిలో నిపుణులు కానీ నియామకం లేదా భాగస్వామ్యం చేసేవారికి వీరి వివరాలు తెలియవు.',
    'home.gap_2_title': 'టీమ్ లేని ఆలోచనలు',
    'home.gap_2_desc': 'మంచి ఆలోచన ఉన్నప్పటికీ దాన్ని నిర్మించడంలో సహాయపడే ఒక్క వ్యక్తి కూడా సమీపంలో తెలియకపోవచ్చు.',
    'home.gap_3_title': 'ధృవీకరణ లేని నమ్మకం',
    'home.gap_3_desc': 'ఉద్యోగ పోర్టల్‌లు హోదాలకు ప్రాధాన్యతనిస్తాయి. ఫ్రీలాన్స్ సైట్లు తక్కువ బిడ్‌కు ప్రాధాన్యతనిస్తాయి. ఎవరూ ఒకరి నిజమైన సామర్థ్యాన్ని చూపించలేరు.',

    // Discover Yourself Section
    'home.discover_chip': 'ఉచిత అంచనా',
    'home.discover_heading_1': 'మీకు ఏది సరిపోతుందో తెలియదా?',
    'home.discover_heading_2': 'కొన్ని ప్రశ్నలకు సమాధానం ఇవ్వండి.',
    'home.discover_desc': 'ఏడు నిమిషాలు, పూర్తిగా ఉచితం. మీ జిల్లా, ఆసక్తులు మరియు పెట్టుబడి సామర్థ్యం తెలియజేయండి, మీకు తగిన వ్యాపార ఆలోచనలను మేము సూచిస్తాము.',
    'home.discover_bullet_1': 'మీకు ఎలాంటి పని సరిపోతుంది — నిర్మాణం, నాయకత్వం, విక్రయం లేదా ప్రణాళిక',
    'home.discover_bullet_2': 'మీ జిల్లాకు అనువైన వ్యాపార ఆలోచనలు',
    'home.discover_bullet_3': '₹30,000 నుండి మీ బడ్జెట్‌కు తగిన వ్యాపార ఆలోచనలు మాత్రమే',
    'home.discover_bullet_4': 'మీ ఆలోచనను పోస్ట్ చేయండి మరియు ఇతరులు మీతో చేరేలా చేయండి',
    'home.take_assessment': 'ఉచిత అంచనాను ప్రారంభించండి →',

    // Archetypes
    'archetype.innovator': 'ఆవిష్కర్త',
    'archetype.innovator_desc': 'ఉత్పత్తి & వ్యూహ రూపకర్త — ఇతరులు గుర్తించని అవకాశాలను గుర్తిస్తారు.',
    'archetype.leader': 'నాయకుడు',
    'archetype.leader_desc': 'నాయకత్వం వహించి లక్ష్యాలను సాధిస్తారు.',
    'archetype.builder': 'నిర్మాత',
    'archetype.builder_desc': 'కార్యకలాపాలను సమర్థవంతంగా నడిపిస్తారు.',
    'archetype.influencer': 'ఇన్‌ఫ్లుయెన్సర్',
    'archetype.influencer_desc': 'మార్కెటింగ్ & బ్రాండ్ నిర్మాణంలో ముందుంటారు.',

    // Built for India's Builders
    'home.fits_chip': 'మీ రంగం ఏదైనా',
    'home.fits_title_1': 'మీరు ప్రస్తుతం ఏ పని చేస్తున్నా,',
    'home.fits_title_2': 'ఇక్కడ మీకు స్థానం ఉంది.',
    'sector.ai_tech': 'ఏఐ & టెక్నాలజీ',
    'sector.local_biz': 'స్థానిక వ్యాపారం',
    'sector.ev_tech': 'ఈవీ టెక్నాలజీ',
    'sector.drone': 'డ్రోన్ టెక్నాలజీ',
    'sector.agriculture': 'వ్యవసాయం',
    'sector.student': 'విద్యార్థి',
    'sector.trades': 'వృత్తి నైపుణ్యాలు',
    'sector.digital': 'డిజిటల్ సేవలు',
    'home.explore_opps': 'అవకాశాలను అన్వేషించండి →',

    // Final CTA
    'home.ready_chip': 'సిద్ధంగా ఉన్నారా?',
    'home.step_heading_1': 'మొదటి అడుగు వేయండి',
    'home.step_heading_2': 'మీరున్న చోటు నుంచే ప్రారంభించండి.',
    'home.step_subheading': 'పూర్తిగా ఉచితం. గూగుల్ ద్వారా సులభంగా సైన్ ఇన్ అవ్వండి — పాస్‌వర్డ్ అవసరం లేదు.',
    'home.join_sparkle': 'వాల్యూవీవ్‌లో చేరండి ✨',

    // Stats
    'stats.who_is_here': 'ఇప్పటివరకు చేరిన వారు',
    'stats.visitors': 'సందర్శకులు',
    'stats.assessments': 'డిస్కవర్ ప్రొఫైల్స్',
    'stats.opportunities': 'అందుబాటులో ఉన్న అవకాశాలు',
    'stats.collaborators': 'సహకారులు',
    'stats.districts': 'కవర్ చేయబడిన జిల్లాలు',
    'stats.launching_soon': 'ప్లాట్‌ఫారమ్ త్వరలో ప్రారంభం కానుంది — మొదట చేరే వారిలో ఉండండి.',

    // How It Works
    'how_it_works.chip': 'ఐదు దశలు',
    'how_it_works.title': 'ఇది ఎలా పనిచేస్తుంది',
    'how_it_works.subtitle': 'స్వయం అన్వేషణ నుండి మీ వ్యాపారాన్ని ప్రారంభించే వరకు 5 దశలు.',
    'step.step1_title': 'మిమ్మల్ని మీరు తెలుసుకోండి',
    'step.step1_desc': 'మీ వ్యవస్థాపక శైలి మరియు బలాలు గుర్తించండి',
    'step.step2_title': 'వ్యక్తిగత ఆలోచనలు పొందండి',
    'step.step2_desc': 'మీ జిల్లా మరియు బడ్జెట్‌కు సరిపోయే వ్యాపార ఆలోచనలు',
    'step.step3_title': 'జిల్లా అవకాశాలు అన్వేషించండి',
    'step.step3_desc': 'మీ జిల్లాలో నిజమైన అవకాశాలు',
    'step.step4_title': 'సహకారులను కనుగొనండి',
    'step.step4_desc': 'సహ-వ్యవస్థాపకులు మరియు భాగస్వాములతో కనెక్ట్ అవ్వండి',
    'step.step5_title': 'మీ వెంచర్‌ను నిర్మించండి',
    'step.step5_desc': 'మీ సొంత పట్టణం నుంచే ప్రాజెక్ట్ ప్రారంభించండి',

    // Journey & Milestones
    'journey.chip': 'దశలవారీగా',
    'journey.title': 'తరువాత ఏమి చేయాలి',
    'journey.subtitle': 'మొదటి క్లిక్ నుండి నిధుల సేకరణ వరకు రోడ్‌మ్యాప్.',
    'milestone.day1_period': '1వ రోజు',
    'milestone.day1_title': 'కొన్ని ప్రశ్నలకు సమాధానం ఇవ్వండి',
    'milestone.day1_desc': 'కొన్ని ప్రశ్నలకు సమాధానం ఇవ్వండి, మీకు సరిపోయే ఆలోచనలను మేము సూచిస్తాము.',
    'milestone.week1_period': '1వ వారం',
    'milestone.week1_title': 'పరిశీలించండి',
    'milestone.week1_desc': 'మీ జిల్లా, బడ్జెట్ మరియు నైపుణ్యాలకు సరిపోయే వ్యాపార ఆలోచనలను బ్రౌజ్ చేయండి.',
    'milestone.week2_period': '2వ వారం',
    'milestone.week2_title': 'సమీపంలోని వ్యక్తులను కనుగొనండి',
    'milestone.week2_desc': 'మీకు లేని నైపుణ్యాలు కలిగిన వ్యక్తులను సమీపంలో కనుగొనండి.',
    'milestone.month1_period': '1వ నెల',
    'milestone.month1_title': 'మీ ప్రాజెక్ట్‌ను పోస్ట్ చేయండి',
    'milestone.month1_desc': 'మీరు నిర్మిస్తున్న దాన్ని పోస్ట్ చేయండి మరియు ఇతరులు మీతో చేరడానికి అడగనివ్వండి.',
    'milestone.month3_period': '3వ నెల',
    'milestone.month3_title': 'విస్తరించండి',
    'milestone.month3_desc': 'ఎక్కడ విక్రయించాలి, విస్తరణకు ఎంత ఖర్చవుతుంది మరియు ఎవరు నిధులు సమకూరుస్తారో తెలుసుకోండి.',

    // Opportunities
    'opps.chip': 'ఇప్పుడు అందుబాటులో ఉంది',
    'opps.title': 'ప్రధాన అవకాశాలు',
    'opps.subtitle': 'తెలంగాణ మరియు ఆంధ్రప్రదేశ్ వ్యాప్తంగా ఉన్న నిజమైన వ్యాపార అవకాశాలు.',
    'opps.view_all': 'అన్ని అవకాశాలను చూడండి →',

    // Activity
    'activity.chip': 'లైవ్ యాక్టివిటీ',
    'activity.title': 'ప్రస్తుతం ఏమి జరుగుతోంది',
    'activity.subtitle': 'భారతదేశ వ్యాప్తంగా వాల్యూవీవ్ బిల్డర్స్ చేస్తున్న కార్యకలాపాలు.',

    // Onboarding / Get Started
    'onboarding.title': 'మీరు ఇక్కడ ఏ పనిని చేయవాలనుకుంటున్నారు?',
    'onboarding.student': 'నేను కౌశల్యం నేర్చుకోవాలనుకుంటున్నాను',
    'onboarding.entrepreneur': 'నేను ఒక వ్యాపారాన్ని ప్రారంభించాలనుకుంటున్నాను',
    'onboarding.job_seeker': 'నేను ఉద్యోగం కోసం చూస్తున్నాను',
    'onboarding.farmer': 'నేను వ్యవసాయంలో ఉన్నాను',
    'onboarding.corporate': 'నేను ఒక జట్టును నిర్మించటానికి ఉన్నాను',
    'getstarted.chip': 'ఖాతా సృష్టి',
    'getstarted.heading_1': 'వాల్యూవీవ్‌కు మిమ్మల్ని ఏది',
    'getstarted.subheading': 'సహకారులు, బృందాలతో కలిసి పనిచేయడానికి మరియు మీ ఆలోచనలను పోస్ట్ చేయడానికి ఖాతా అవసరం. మీకు తగినది ఎంచుకోండి.',
    'getstarted.look_around_title': 'కేవలం పరిశీలించాలనుకుంటున్నారా?',
    'getstarted.look_around_desc': 'ప్రతి నైపుణ్యం, పథకం, వ్యాపార ఆలోచన మరియు జిల్లా సమాచారం చదవడానికి ఉచితం — ఖాతా లేదా సైన్ ఇన్ అవసరం లేదు.',
    'getstarted.explore_free': 'ఖాతా లేకుండానే అన్వేషించండి →',
    'getstarted.already_member': 'ఇప్పటికే సభ్యులా?',
    'getstarted.signin_link': 'సైన్ ఇన్ చేయండి →',
    'getstarted.continue_google': 'గూగుల్‌తో కొనసాగించండి →',
    'getstarted.google_note': 'మేము మిమ్మల్ని గూగుల్ ద్వారా సైన్ ఇన్ చేస్తాము. పాస్‌వర్డ్ అవసరం లేదు.',
    'getstarted.redirecting': 'దారి మళ్లిస్తోంది…',

    // Sign In
    'signin.title': 'స్వాగతం',
    'signin.subtitle': 'మీ డాష్‌బోర్డ్, కనెక్షన్‌లు మరియు అవకాశాలను యాక్సెస్ చేయడానికి మీ వాల్యూవీవ్ ఖాతాలోకి సైన్ ఇన్ చేయండి.',
    'signin.continue_google': 'గూగుల్‌తో కొనసాగించండి',
    'signin.new_to_valueweave': 'వాల్యూవీవ్‌కు కొత్తవా?',
    'signin.create_profile': 'మీ ప్రొఫైల్‌ను సృష్టించండి →',

    // Common buttons
    'btn.next': 'తరువాత →',
    'btn.back': '← వెనుకకు',
    'btn.submit': 'సమర్పించండి',
    'btn.close': 'మూయండి',
    'btn.learn_more': 'మరిన్ని తెలుసుకోండి',
    'btn.explore': 'అన్వేషించండి',
    'btn.view': 'చూడండి',
    'btn.get_started': 'ప్రారంభించండి',

    // Language selector
    'language.select': 'భాష',
    'language.english': 'English',
    'language.telugu': 'తెలుగు',

    // Common UI
    'ui.menu': 'మెను',
    'ui.close_menu': 'మెను మూయండి',
    'ui.open_menu': 'మెను తెరండి',
    'ui.loading': 'లోడ్ చేస్తోంది...',
    'ui.error': 'ఏదో విషయం సరిగా లేదు',
    'ui.try_again': 'మళ్లీ ప్రయత్నించండి',
    'ui.back_to_home': 'హోమ్‌కు తిరిగి వెళ్లండి',

    // Footer
    'footer.founded_by': 'రవి కుమార్ బానోత్ చే స్థాపించబడింది',
    'footer.built_in_bharat': 'భారత్‌లో నిర్మించబడింది.',
    'footer.contact': 'సంప్రదించండి',
    'footer.follow_title': 'వాల్యూవీవ్‌ను ఫాలో అవ్వండి',
    'footer.follow_sub': 'భారత్ తదుపరి బిల్డర్ల ప్రయాణాన్ని అనుసరించండి.',

    // Founder / Attribution
    'founder.title': 'వ్యవస్థాపకుడు, వేల్యూవీవ్',
    'founder.founder': 'వ్యవస్థాపకుడు',
    'founder.founded_by': 'రవి కుమార్ బానోత్ చే స్థాపించబడింది',
    'about.founder_name': 'రవి కుమార్ బానోత్',
    'about.founder_title': 'వ్యవస్థాపకుడు, వేల్యూవీవ్',
    'about.founder_bio': 'కెరీర్లు, నైపుణ్యాలు, వ్యాపారాలు, ప్రభుత్వ పథకాలు, పరిశ్రమలు మరియు స్థానిక అవకాశాల గురించిన సమాచారాన్ని సులభంగా కనుగొనడానికి మరియు ఉపయోగించుకోవడానికి రవి కుమార్ బానోత్ ద్వారా వేల్యూవీవ్ స్థాపించబడింది.',
  },
};

/**
 * Restore language preference on page load.
 * Must be called early in client-side initialization.
 */
export function restoreLanguagePreference() {
  if (typeof window === 'undefined') return;
  const lang = getStoredLanguage();
  document.documentElement.lang = lang;
}
