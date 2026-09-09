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
    'signin.welcome_back': 'Welcome back',
    'signin.desc': 'Sign in to your ValueWeave account to access your dashboard, connections, and opportunities.',
    'getstarted.title_1': 'What brings you to',
    'getstarted.title': 'What brings you to ValueWeave?',
    'getstarted.subtitle': 'An account is for working with people — collaborators, teams and posting your own ideas. Pick what fits best.',
    'getstarted.explore_free_title': 'Just want to look around?',
    'getstarted.explore_free_desc': 'Every skill, scheme, business idea and district is free to read — no account, no sign-in.',
    'getstarted.explore_free_cta': 'Explore without an account →',
    'getstarted.no_password': "We'll sign you in with Google. No password needed.",
    'onboarding.title_1': 'Tell us about',
    'onboarding.title_2': 'you',
    'onboarding.subtitle': 'Two minutes. We use this to suggest skills, schemes and businesses that fit you.',
    'onboarding.name_label': 'Your name',
    'onboarding.name_placeholder': 'e.g. Arjun Patil',
    'onboarding.city_label': 'City',
    'onboarding.city_placeholder': 'e.g. Hyderabad, Telangana',
    'onboarding.skills_label': 'Skills',
    'onboarding.skills_hint': 'What do you do best? Add 3–6 skills.',
    'onboarding.interests_label': 'Interests',
    'onboarding.interests_hint': "Domains you're excited about.",
    'onboarding.looking_for_label': "I'm here to…",
    'onboarding.bio_label': 'Short bio',
    'onboarding.bio_hint': 'One or two sentences about what you build.',
    'onboarding.bio_placeholder': 'e.g. Electronics diploma holder building EV charging stations in tier-2 cities.',
    'onboarding.add_btn': 'Add',
    'onboarding.type_and_press_enter': 'Type and press Enter',
    'audience_start.start_with': 'Start with one of these',
    'audience_start.or_search': 'Or search for something specific',
    'audience_start.not_quite_you': 'Not quite you?',
    'search.could_not_find': "We couldn't find",
    'search.result_one': 'result',
    'search.result_many': 'results',
    'search.for': 'for',
    'search.nearby_help': "That exact thing isn't in our research yet. Here's what is nearby — and if none of it helps, tell us and we'll go and find it.",
    'search.add_to_list': "That isn't in our research yet. Tell us what you were looking for and we'll add it to the list — we read every one of these.",
    'districts.intel_badge': 'DISTRICT INTELLIGENCE',
    'districts.index_title': 'Know Your District. Build with Confidence.',
    'districts.index_subtitle': "Deep-dive profiles on population, industries, schemes, opportunities, and skills demand — built for Bharat's builders.",
    'districts.hero_title': 'Discover Where Opportunities Exist',
    'districts.hero_desc': 'Start with where you already are. Every district here shows the industries around it, the businesses people start there, where to learn the skills, and which government schemes apply.',
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
    'search.read': 'Read',
    'search.matched': 'matched',
    'search.no_results_for': "We couldn't find",
    'search.in_scope': 'in',
    'search.not_in_research': "That exact thing isn't in our research yet. Here's what is nearby — and if none of it helps, tell us and we'll go and find it.",
    'search.not_in_research_empty': "That isn't in our research yet. Tell us what you were looking for and we'll add it to the list — we read every one of these.",
    'search.did_you_mean': 'Did you mean',
    'search.related': 'Related',
    'search.try_searching': 'Try searching',
    'search.request_topic_empty': 'Should we research “{query}”?',
    'search.request_topic_thin': 'Want more on “{query}”?',
    'search.ask_prompt': 'Ask for it and we will look into it. This is how most of what is on ValueWeave got here.',
    'search.coming_soon': 'Coming to search soon:',
    'search.browse_all': 'Or browse everything we have researched →',
    'search.request_topic_btn': 'Request this topic',

    // Knowledge Explorer
    'knowledge.title': 'Knowledge Explorer',
    'knowledge.explore_chip': 'Explore',
    'knowledge.search_results_chip': 'Search results',
    'knowledge.hero_heading': 'What would you like to explore?',
    'knowledge.hero_subheading': 'Districts to build in, businesses you could start, skills worth learning, government schemes you may qualify for and crops that grow well here — across Telangana and Andhra Pradesh. Everything here was checked against an official public source.',
    'knowledge.search_label': 'Search everything we have researched',
    'knowledge.search_placeholder': 'A district, a skill, a scheme, a business idea…',
    'knowledge.clear': 'Clear',
    'knowledge.all_knowledge': '← All knowledge',
    'knowledge.to_explore': 'to explore',
    'knowledge.written_profiles': 'written profiles',
    'knowledge.results': 'results',
    'knowledge.result': 'result',
    'knowledge.thin_summary': 'That is all we have researched on this so far. Here is what is nearby.',

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

    // Opportunities & Explore Page
    'opps.chip': 'LIVE NOW',
    'opps.title': 'Featured Opportunities',
    'opps.subtitle': 'Real business opportunities from across Telangana and Andhra Pradesh.',
    'opps.view_all': 'View All Opportunities →',
    'explore.title': 'Explore opportunities',
    'explore.subtitle': 'Browse what builders across Bharat are creating. Sign in to connect or post your own.',
    'explore.search_placeholder': 'Search opportunities…',
    'explore.cat_all': 'All',
    'explore.cat_healthcare': 'Healthcare',
    'explore.cat_education': 'Education',
    'explore.cat_agri': 'Agriculture',
    'explore.cat_technology': 'Technology',
    'explore.cat_manufacturing': 'Manufacturing',
    'explore.cat_local_business': 'Local Business',
    'explore.cat_ev_electronics': 'EV & Electronics',
    'explore.cat_drone': 'Drone',
    'explore.cat_student': 'Student',
    'explore.cat_trades': 'Trades',
    'explore.cat_digital': 'Digital',
    'explore.all_districts': 'All districts',
    'explore.no_opportunities': 'No opportunities yet',
    'explore.no_opps_sub': 'Be among the first builders to post an opportunity for your community.',
    'explore.post_first': 'Join & post the first →',
    'explore.like_what_see': 'Like what you see?',
    'explore.like_what_see_sub': 'Join ValueWeave free to send connection requests, post your own opportunities, and build with other Bharat builders.',

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
    'onboarding.step_chip': 'STEP 2 OF 3',
    'onboarding.tell_us_title': 'Tell us about you',
    'onboarding.tell_us_sub': 'Two minutes. We use this to suggest skills, schemes and businesses that fit you.',
    'onboarding.name': 'Your name',
    'onboarding.city': 'City',
    'onboarding.skills': 'Skills',
    'onboarding.skills_hint': 'What do you do best? Add 3–6 skills.',
    'onboarding.interests': 'Interests',
    'onboarding.interests_hint': "Domains you're excited about.",
    'onboarding.here_to': "I'm here to…",
    'onboarding.bio': 'Short bio',
    'onboarding.bio_hint': 'One or two sentences about what you build.',
    'onboarding.continue_dashboard': 'Continue to Dashboard →',
    'onboarding.add': 'Add',
    'onboarding.saving': 'Saving…',

    // Get Started
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
    'getstarted.selected': '✓ Selected',
    'intent.find_collaborators': 'Find Collaborators',
    'intent.find_collaborators_desc': 'Connect with people who complement your skills',
    'intent.start_business': 'Start a Business',
    'intent.start_business_desc': 'Build a local venture or startup from scratch',
    'intent.local_opportunities': 'Local Opportunities',
    'intent.local_opportunities_desc': 'Discover projects and businesses near you',
    'intent.find_cofounder': 'Find a Co-founder',
    'intent.find_cofounder_desc': 'Meet someone to build your dream with',
    'intent.join_startup': 'Join a Startup Team',
    'intent.join_startup_desc': 'Become part of an existing builder team',
    'intent.offer_skills': 'Offer My Skills',
    'intent.offer_skills_desc': 'Lend your expertise to meaningful projects',
    'intent.explore': 'Just Exploring',
    'intent.explore_desc': "See what's happening across Bharat",
    'intent.hire_collaborators': 'Hire Collaborators',
    'intent.hire_collaborators_desc': 'Bring talent for your existing project',

    // Sign In
    'signin.title': 'Welcome back',
    'signin.subtitle': 'Sign in to your ValueWeave account to access your dashboard, connections, and opportunities.',
    'signin.continue_google': 'Continue with Google',
    'signin.new_to_valueweave': 'New to ValueWeave?',
    'signin.create_profile': 'Create your profile →',
    'signin.checking_session': 'Checking your session…',

    // Audience Start Pages
    'audience_start.start_with_one': 'Start with one of these',
    'audience_start.search_specific': 'Or search for something specific',
    'audience_start.not_quite_you': 'Not quite you?',

    // Idea Library
    'ideas.badge': 'IDEA LIBRARY · BETA',
    'ideas.title': 'Start something real.',
    'ideas.subtitle': 'A growing library of practical, Bharat-grounded business ideas. Pick one that fits your district, skills, and budget — then post it as an opportunity and find collaborators.',
    'ideas.search_placeholder': 'Search ideas by title, skill, or tag…',
    'ideas.all_types': 'All types',
    'ideas.all_sectors': 'All sectors',
    'ideas.all_districts': 'All districts',
    'ideas.more_filters': 'More filters',
    'ideas.fewer_filters': 'Fewer filters',
    'ideas.invest_needed': 'Investment needed',
    'ideas.any_budget': 'Any budget',
    'ideas.tags': 'Tags',
    'ideas.all_tags': 'All tags',
    'ideas.beginner_friendly': 'Beginner friendly only',
    'ideas.sort': 'Sort',
    'ideas.sort_recommended': 'Recommended',
    'ideas.sort_invest_asc': 'Lowest investment',
    'ideas.sort_invest_desc': 'Highest investment',
    'ideas.sort_revenue_desc': 'Highest revenue',
    'ideas.sort_az': 'A–Z',
    'ideas.clear_all': 'Clear all',
    'ideas.no_match': 'No ideas match those filters',
    'ideas.no_match_sub': 'Try clearing a filter or widening your budget range.',
    'ideas.have_idea': "Have an idea that's not listed?",
    'ideas.have_idea_sub': 'Post it as an opportunity — other builders in your district can find and collaborate on it.',
    'ideas.post_cta': 'Post your idea →',
    'ideas.remote_possible': 'Remote possible',

    // Collaborators
    'collab.badge': 'COLLABORATOR MARKETPLACE',
    'collab.title': 'Find Your Co-Builder',
    'collab.subtitle': 'Builders, innovators, and operators across Telangana and Andhra Pradesh — profiled by the Discover Yourself assessment.',
    'collab.all_sectors': 'All sectors',
    'collab.be_first': 'Be the first collaborator in your district',
    'collab.be_first_sub': 'Take the 7-minute Discover Yourself assessment to create your collaborator profile — archetype, founder role, sectors, and budget — and get matched with opportunities.',
    'collab.take_assessment': 'Take the assessment',
    'collab.want_appear': 'Want to appear here?',
    'collab.want_appear_sub': 'Complete the assessment and publish your collaborator profile — opportunities and co-founders will find you.',
    'collab.browse_opps': 'Browse opportunities',

    // Districts
    'districts.badge': 'DISTRICT INTELLIGENCE',
    'districts.title': 'Know Your District. Build with Confidence.',
    'districts.subtitle': 'Deep-dive profiles on population, industries, schemes, opportunities, and skills demand — built for Bharat’s builders.',
    'districts.view_profile': 'View Profile →',
    'districts.open_module': 'Open district module →',
    'districts.every_researched': 'Every researched district',
    'districts.every_researched_sub': 'Population, area, literacy and headquarters for every district, plus the industries, businesses and schemes connected to each one.',

    // Common buttons
    'btn.next': 'Next →',
    'btn.back': '← Back',
    'btn.submit': 'Submit',
    'btn.close': 'Close',
    'btn.learn_more': 'Learn more',
    'btn.explore': 'Explore',
    'btn.view': 'View',
    'btn.get_started': 'Get Started',
    'btn.read': 'Read',

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
    'ui.back_home': 'Back home',

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
    'signin.welcome_back': 'స్వాగతం',
    'signin.desc': 'మీ డాష్\u200cబోర్డ్, కనెక్షన్\u200cలు మరియు అవకాశాలను యాక్సెస్ చేయడానికి మీ ValueWeave ఖాతాలోకి సైన్ ఇన్ చేయండి.',
    'getstarted.title_1': 'మీరు దేని కోసం',
    'getstarted.title': 'మీరు ValueWeave కు ఎందుకు వచ్చారు?',
    'getstarted.subtitle': 'ఇతరులతో కలిసి పనిచేయడానికి — సహకారులు, బృందాలు మరియు మీ స్వంత ఆలోచనలను పోస్ట్ చేయడానికి ఖాతా ఉపయోగపడుతుంది.',
    'getstarted.explore_free_title': 'కేవలం సమాచారం చూడాలనుకుంటున్నారా?',
    'getstarted.explore_free_desc': 'ప్రతి నైపుణ్యం, పథకం, వ్యాపార ఆలోచన మరియు జిల్లా వివరాలు ఉచితంగా చదవవచ్చు — ఖాతా లేదా సైన్ ఇన్ అవసరం లేదు.',
    'getstarted.explore_free_cta': 'ఖాతా లేకుండా అన్వేషించండి →',
    'getstarted.no_password': 'మేము మిమ్మల్ని గూగుల్ ద్వారా సైన్ ఇన్ చేస్తాము. పాస్\u200cవర్డ్ అవసరం లేదు.',
    'onboarding.title_1': 'మీ గురించి',
    'onboarding.title_2': 'చెప్పండి',
    'onboarding.subtitle': 'రెండు నిమిషాలు. మీకు సరిపోయే నైపుణ్యాలు, పథకాలు మరియు వ్యాపారాలను సూచించడానికి మేము దీన్ని ఉపయోగిస్తాము.',
    'onboarding.name_label': 'మీ పేరు',
    'onboarding.name_placeholder': 'ఉదా. అర్జున్ పాటిల్',
    'onboarding.city_label': 'నగరం / పట్టణం',
    'onboarding.city_placeholder': 'ఉదా. హైదరాబాద్, తెలంగాణ',
    'onboarding.skills_label': 'నైపుణ్యాలు',
    'onboarding.skills_hint': 'మీరు ఏ పని బాగా చేయగలరు? 3–6 నైపుణ్యాలు జోడించండి.',
    'onboarding.interests_label': 'ఆసక్తులు',
    'onboarding.interests_hint': 'మీకు ఆసక్తి ఉన్న రంగాలు.',
    'onboarding.looking_for_label': 'నా లక్ష్యం…',
    'onboarding.bio_label': 'చిన్న పరిచయం',
    'onboarding.bio_hint': 'మీరు ఏమి నిర్మిస్తున్నారో ఒకటి లేదా రెండు వాక్యాలు.',
    'onboarding.bio_placeholder': 'ఉదా. ఎలక్ట్రానిక్స్ డిప్లొమా పూర్తి చేసి ఈవీ ఛార్జింగ్ కేంద్రాలు నిర్మిస్తున్నాను.',
    'onboarding.add_btn': 'జోడించు',
    'onboarding.type_and_press_enter': 'టైప్ చేసి ఎంటర్ నొక్కండి',
    'audience_start.start_with': 'వీటిలో ఒకదానితో ప్రారంభించండి',
    'audience_start.or_search': 'లేదా నిర్దిష్టమైన దేనినైనా శోధించండి',
    'audience_start.not_quite_you': 'మీకు సరిపోలేదా?',
    'search.could_not_find': 'మేము కనుగొనలేకపోయాము',
    'search.result_one': 'ఫలితం',
    'search.result_many': 'ఫలితాలు',
    'search.for': 'కోసం',
    'search.nearby_help': 'ఈ ఖచ్చితమైన అంశం ఇంకా మా పరిశోధనలో లేదు. దీనికి దగ్గరగా ఉన్న వివరాలు ఇవి — ఇవి కాకుండా మరేదైనా కావాలంటే మాకు తెలపండి, మేము పరిశోధించి చేర్చుతాము.',
    'search.add_to_list': 'ఈ అంశం ఇంకా మా పరిశోధనలో లేదు. మీరు దేని కోసం వెతుకుతున్నారో మాకు తెలపండి, మేము దాన్ని పరిశోధన జాబితాలో చేర్చుతాము.',
    'districts.intel_badge': 'జిల్లా సమాచారం',
    'districts.index_title': 'మీ జిల్లాను తెలుసుకోండి. నమ్మకంతో నిర్మించండి.',
    'districts.index_subtitle': 'జనాభా, పరిశ్రమలు, పథకాలు, అవకాశాలు మరియు నైపుణ్యాల డిమాండ్ గురించిన సమగ్ర సమాచారం — భారత్ బిల్డర్ల కోసం.',
    'districts.hero_title': 'అవకాశాలు ఎక్కడ ఉన్నాయో కనుగొనండి',
    'districts.hero_desc': 'మీరున్న చోటు నుంచే ప్రారంభించండి. ప్రతి జిల్లాలోని పరిశ్రమలు, ప్రారంభించగల వ్యాపారాలు, నైపుణ్యాల శిక్షణ మరియు వర్తించే ప్రభుత్వ పథకాలు ఇక్కడ చూడండి.',
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
    'search.read': 'చదవండి',
    'search.matched': 'సరిపోలింది',
    'search.no_results_for': 'మేము కనుగొనలేకపోయాము',
    'search.in_scope': 'లో',
    'search.not_in_research': 'ఈ ఖచ్చితమైన అంశం ఇంకా మా పరిశోధనలో లేదు. దీనికి దగ్గరగా ఉన్న వివరాలు ఇవి — ఇవి కాకుండా మరేదైనా కావాలంటే మాకు తెలపండి, మేము పరిశోధించి చేర్చుతాము.',
    'search.not_in_research_empty': 'ఈ అంశం ఇంకా మా పరిశోధనలో లేదు. మీరు దేని కోసం వెతుకుతున్నారో మాకు తెలపండి, మేము దాన్ని పరిశోధన జాబితాలో చేర్చుతాము.',
    'search.did_you_mean': 'మీరు ఉద్దేశించినది ఇదేనా',
    'search.related': 'సంబంధిత',
    'search.try_searching': 'ఇలా శోధించి చూడండి',
    'search.request_topic_empty': '“{query}” గురించి మేము పరిశోధించాలా?',
    'search.request_topic_thin': '“{query}” గురించి మరింత సమాచారం కావాలా?',
    'search.ask_prompt': 'మీకు కావాల్సిన అంశాన్ని అడగండి, మేము పరిశోధిస్తాము. వేల్యూవీవ్‌లోని చాలా సమాచారం ఇలాగే చేర్చబడింది.',
    'search.coming_soon': 'త్వరలో శోధనలో రానున్నవి:',
    'search.browse_all': 'లేదా మేము పరిశోధించిన ప్రతిదాన్ని బ్రౌజ్ చేయండి →',
    'search.request_topic_btn': 'ఈ అంశాన్ని అభ్యర్థించండి',

    // Knowledge Explorer
    'knowledge.title': 'నాలెడ్జ్ ఎక్స్‌ప్లోరర్',
    'knowledge.explore_chip': 'అన్వేషించండి',
    'knowledge.search_results_chip': 'శోధన ఫలితాలు',
    'knowledge.hero_heading': 'మీరు ఏమి అన్వేషించాలనుకుంటున్నారు?',
    'knowledge.hero_subheading': 'తెలంగాణ మరియు ఆంధ్రప్రదేశ్ వ్యాప్తంగా వ్యాపారాలు ప్రారంభించడానికి అవకాశాలు, నైపుణ్యాలు, ప్రభుత్వ పథకాలు మరియు పంటల సమాచారం — అన్నీ అధికారిక ప్రభుత్వ వనరుల నుండి సేకరించబడినవి.',
    'knowledge.search_label': 'మేము పరిశోధించిన ప్రతిదాన్ని శోధించండి',
    'knowledge.search_placeholder': 'ఒక జిల్లా, నైపుణ్యం, పథకం, వ్యాపార ఆలోచన…',
    'knowledge.clear': 'క్లియర్',
    'knowledge.all_knowledge': '← అన్ని నాలెడ్జ్ విభాగాలు',
    'knowledge.to_explore': 'అన్వేషించడానికి',
    'knowledge.written_profiles': 'లిఖిత ప్రొఫైల్స్',
    'knowledge.results': 'ఫలితాలు',
    'knowledge.result': 'ఫలితం',
    'knowledge.thin_summary': 'ఈ అంశంపై ఇప్పటివరకు లభించిన పరిశోధన ఇది. దీనికి సంబంధించిన ఇతర వివరాలు ఇక్కడ ఉన్నాయి.',

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

    // Opportunities & Explore Page
    'opps.chip': 'ఇప్పుడు అందుబాటులో ఉంది',
    'opps.title': 'ప్రధాన అవకాశాలు',
    'opps.subtitle': 'తెలంగాణ మరియు ఆంధ్రప్రదేశ్ వ్యాప్తంగా ఉన్న నిజమైన వ్యాపార అవకాశాలు.',
    'opps.view_all': 'అన్ని అవకాశాలను చూడండి →',
    'explore.title': 'అవకాశాలను అన్వేషించండి',
    'explore.subtitle': 'భారత్ వ్యాప్తంగా బిల్డర్స్ సృష్టిస్తున్న వాటిని బ్రౌజ్ చేయండి. కనెక్ట్ అవ్వడానికి లేదా మీ స్వంత ప్రాజెక్ట్‌ను పోస్ట్ చేయడానికి సైన్ ఇన్ చేయండి.',
    'explore.search_placeholder': 'అవకాశాలను శోధించండి…',
    'explore.cat_all': 'అన్నీ',
    'explore.cat_healthcare': 'ఆరోగ్య సంరక్షణ',
    'explore.cat_education': 'విద్య',
    'explore.cat_agri': 'వ్యవసాయం',
    'explore.cat_technology': 'సాంకేతికత',
    'explore.cat_manufacturing': 'తయారీ రంగం',
    'explore.cat_local_business': 'స్థానిక వ్యాపారం',
    'explore.cat_ev_electronics': 'EV & ఎలక్ట్రానిక్స్',
    'explore.cat_drone': 'డ్రోన్',
    'explore.cat_student': 'విద్యార్థి',
    'explore.cat_trades': 'వృత్తి నైపుణ్యాలు',
    'explore.cat_digital': 'డిజిటల్',
    'explore.all_districts': 'అన్ని జిల్లాలు',
    'explore.no_opportunities': 'ఇంకా అవకాశాలు లేవు',
    'explore.no_opps_sub': 'మీ ప్రాంతంలో మొట్టమొదటి అవకాశాన్ని పోస్ట్ చేసే బిల్డర్‌గా ఉండండి.',
    'explore.post_first': 'చేరండి & మొదటిదాన్ని పోస్ట్ చేయండి →',
    'explore.like_what_see': 'మీకు ఇది నచ్చిందా?',
    'explore.like_what_see_sub': 'కనెక్షన్ అభ్యర్థనలు పంపడానికి, మీ అవకాశాలను పోస్ట్ చేయడానికి మరియు ఇతర భారత్ బిల్డర్లతో కలిసి పనిచేయడానికి వేల్యూవీవ్‌లో ఉచితంగా చేరండి.',

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
    'onboarding.step_chip': 'దశ 2 (3 లో)',
    'onboarding.tell_us_title': 'మీ గురించి మాకు చెప్పండి',
    'onboarding.tell_us_sub': 'రెండు నిమిషాలు. మీకు తగిన నైపుణ్యాలు, పథకాలు మరియు వ్యాపారాలను సూచించడానికి మేము దీన్ని ఉపయోగిస్తాము.',
    'onboarding.name': 'మీ పేరు',
    'onboarding.city': 'నగరం / గ్రామం',
    'onboarding.skills': 'నైపుణ్యాలు',
    'onboarding.skills_hint': 'మీరు ఏ పనిని ఉత్తమంగా చేయగలరు? 3–6 నైపుణ్యాలను జోడించండి.',
    'onboarding.interests': 'ఆసక్తులు',
    'onboarding.interests_hint': 'మీకు ఆసక్తి ఉన్న రంగాలు.',
    'onboarding.here_to': 'నేను ఇక్కడ చేయాలనుకుంటున్నది…',
    'onboarding.bio': 'సంక్షిప్త పరిచయం',
    'onboarding.bio_hint': 'మీరు ఏమి నిర్మిస్తున్నారో ఒకటి లేదా రెండు వాక్యాలలో రాయండి.',
    'onboarding.continue_dashboard': 'డాష్‌బోర్డ్‌కు కొనసాగించండి →',
    'onboarding.add': 'జోడించండి',
    'onboarding.saving': 'భద్రపరుస్తోంది…',

    // Get Started
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
    'getstarted.selected': '✓ ఎంచుకోబడింది',
    'intent.find_collaborators': 'సహకారులను కనుగొనండి',
    'intent.find_collaborators_desc': 'మీ నైపుణ్యాలకు తగిన వ్యక్తులతో కనెక్ట్ అవ్వండి',
    'intent.start_business': 'వ్యాపారాన్ని ప్రారంభించండి',
    'intent.start_business_desc': 'మొదటి నుండి స్థానిక వ్యాపారం లేదా స్టార్టప్‌ను నిర్మించండి',
    'intent.local_opportunities': 'స్థానిక అవకాశాలు',
    'intent.local_opportunities_desc': 'మీ దగ్గరలోని ప్రాజెక్ట్‌లు మరియు వ్యాపారాలను కనుగొనండి',
    'intent.find_cofounder': 'కో-ఫౌండర్‌ను కనుగొనండి',
    'intent.find_cofounder_desc': 'మీ కలల ప్రాజెక్ట్‌ను నిర్మించడానికి తోడ్పడే వ్యక్తిని కలవండి',
    'intent.join_startup': 'స్టార్టప్ బృందంలో చేరండి',
    'intent.join_startup_desc': 'ఇప్పటికే పనిచేస్తున్న బిల్డర్ బృందంలో భాగస్వామి అవ్వండి',
    'intent.offer_skills': 'నా నైపుణ్యాలను అందించడం',
    'intent.offer_skills_desc': 'మంచి ప్రాజెక్ట్‌లకు మీ నైపుణ్యాన్ని అందించండి',
    'intent.explore': 'కేవలం పరిశీలిస్తున్నాను',
    'intent.explore_desc': 'భారత్ వ్యాప్తంగా ఏమి జరుగుతుందో చూడండి',
    'intent.hire_collaborators': 'సహకారులను నియమించుకోండి',
    'intent.hire_collaborators_desc': 'మీ ప్రాజెక్ట్ కోసం నైపుణ్యం కలిగిన వారిని నియమించుకోండి',

    // Sign In
    'signin.title': 'స్వాగతం',
    'signin.subtitle': 'మీ డాష్‌బోర్డ్, కనెక్షన్‌లు మరియు అవకాశాలను యాక్సెస్ చేయడానికి మీ వాల్యూవీవ్ ఖాతాలోకి సైన్ ఇన్ చేయండి.',
    'signin.continue_google': 'గూగుల్‌తో కొనసాగించండి',
    'signin.new_to_valueweave': 'వాల్యూవీవ్‌కు కొత్తవా?',
    'signin.create_profile': 'మీ ప్రొఫైల్‌ను సృష్టించండి →',
    'signin.checking_session': 'మీ సెషన్‌ను తనిఖీ చేస్తోంది…',

    // Audience Start Pages
    'audience_start.start_with_one': 'వీటిలో ఒకదానితో ప్రారంభించండి',
    'audience_start.search_specific': 'లేదా ఏదైనా ప్రత్యేకమైన అంశాన్ని శోధించండి',
    'audience_start.not_quite_you': 'ఇది మీకు సరిపోలలేదా?',

    // Idea Library
    'ideas.badge': 'ఐడియా లైబ్రరీ · బీటా',
    'ideas.title': 'నిజమైన వ్యాపారాన్ని ప్రారంభించండి.',
    'ideas.subtitle': 'భారత్ ఆధారిత వ్యాపార ఆలోచనల సంకలనం. మీ జిల్లా, నైపుణ్యాలు మరియు బడ్జెట్‌కు తగినదాన్ని ఎంచుకోండి — అవకాశంగా పోస్ట్ చేసి సహకారులను కనుగొనండి.',
    'ideas.search_placeholder': 'శీర్షిక, నైపుణ్యం లేదా ట్యాగ్ ద్వారా ఆలోచనలను శోధించండి…',
    'ideas.all_types': 'అన్ని రకాలు',
    'ideas.all_sectors': 'అన్ని రంగాలు',
    'ideas.all_districts': 'అన్ని జిల్లాలు',
    'ideas.more_filters': 'మరిన్ని ఫిల్టర్లు',
    'ideas.fewer_filters': 'తక్కువ ఫిల్టర్లు',
    'ideas.invest_needed': 'అవసరమైన పెట్టుబడి',
    'ideas.any_budget': 'ఏ బడ్జెట్ అయినా',
    'ideas.tags': 'ట్యాగ్‌లు',
    'ideas.all_tags': 'అన్ని ట్యాగ్‌లు',
    'ideas.beginner_friendly': 'ప్రారంభకులకు అనుకూలమైనవి మాత్రమే',
    'ideas.sort': 'క్రమబద్ధీకరించండి',
    'ideas.sort_recommended': 'సిఫార్సు చేయబడినవి',
    'ideas.sort_invest_asc': 'తక్కువ పెట్టుబడి',
    'ideas.sort_invest_desc': 'ఎక్కువ పెట్టుబడి',
    'ideas.sort_revenue_desc': 'ఎక్కువ ఆదాయం',
    'ideas.sort_az': 'A–Z',
    'ideas.clear_all': 'అన్నీ క్లియర్ చేయండి',
    'ideas.no_match': 'ఆ ఫిల్టర్లకు సరిపోలే ఆలోచనలు లేవు',
    'ideas.no_match_sub': 'ఫిల్టర్‌ను క్లియర్ చేసి లేదా బడ్జెట్ పరిధిని విస్తరించి ప్రయత్నించండి.',
    'ideas.have_idea': 'ఇక్కడ లేని మరో ఆలోచన మీ దగ్గర ఉందా?',
    'ideas.have_idea_sub': 'దాన్ని ఒక అవకాశంగా పోస్ట్ చేయండి — మీ జిల్లాలోని ఇతర బిల్డర్స్ కలిసి పనిచేయడానికి సంప్రదిస్తారు.',
    'ideas.post_cta': 'మీ ఆలోచనను పోస్ట్ చేయండి →',
    'ideas.remote_possible': 'రిమోట్ అవకాశం ఉంది',

    // Collaborators
    'collab.badge': 'సహకారుల మార్కెట్‌ప్లేస్',
    'collab.title': 'మీ కో-బిల్డర్‌ను కనుగొనండి',
    'collab.subtitle': 'తెలంగాణ మరియు ఆంధ్రప్రదేశ్ వ్యాప్తంగా బిల్డర్లు, ఇన్నోవేటర్లు — డిస్కవర్ యువర్‌సెల్ఫ్ అసెస్‌మెంట్ ద్వారా నమోదైనవారు.',
    'collab.all_sectors': 'అన్ని రంగాలు',
    'collab.be_first': 'మీ జిల్లాలో మొదటి సహకారిగా ఉండండి',
    'collab.be_first_sub': 'మీ సహకార ప్రొఫైల్‌ను సృష్టించడానికి 7 నిమిషాల డిస్కవర్ అసెస్‌మెంట్ పూర్తి చేయండి మరియు అవకాశాలతో సరిపోల్చబడండి.',
    'collab.take_assessment': 'అసెస్‌మెంట్ తీసుకోండి',
    'collab.want_appear': 'మీరు ఇక్కడ కనిపించాలనుకుంటున్నారా?',
    'collab.want_appear_sub': 'అసెస్‌మెంట్ పూర్తి చేసి మీ ప్రొఫైల్‌ను ప్రచురించండి — అవకాశాలు మరియు సహ-వ్యవస్థాపకులు మిమ్మల్ని కనుగొంటారు.',
    'collab.browse_opps': 'అవకాశాలను బ్రౌజ్ చేయండి',

    // Districts
    'districts.badge': 'జిల్లా సమాచారం',
    'districts.title': 'మీ జిల్లాను తెలుసుకోండి. ఆత్మవిశ్వాసంతో నిర్మించండి.',
    'districts.subtitle': 'జనాభా, పరిశ్రమలు, పథకాలు, అవకాశాలు మరియు నైపుణ్యాల సమాచారం — భారత్ బిల్డర్స్ కోసం రూపొందించబడింది.',
    'districts.view_profile': 'ప్రొఫైల్ చూడండి →',
    'districts.open_module': 'జిల్లా మాడ్యూల్ తెరవండి →',
    'districts.every_researched': 'పరిశోధించబడిన ప్రతి జిల్లా',
    'districts.every_researched_sub': 'ప్రతి జిల్లా జనాభా, విస్తీర్ణం, అక్షరాస్యత మరియు కేంద్రంతో పాటు వాటికి సంబంధించిన పరిశ్రమలు మరియు పథకాలు.',

    // Common buttons
    'btn.next': 'తరువాత →',
    'btn.back': '← వెనుకకు',
    'btn.submit': 'సమర్పించండి',
    'btn.close': 'మూయండి',
    'btn.learn_more': 'మరిన్ని తెలుసుకోండి',
    'btn.explore': 'అన్వేషించండి',
    'btn.view': 'చూడండి',
    'btn.get_started': 'ప్రారంభించండి',
    'btn.read': 'చదవండి',

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
    'ui.back_home': 'హోమ్‌కు వెళ్లండి',

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
