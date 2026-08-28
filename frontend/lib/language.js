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

    // Home & Audiences / Goals
    'home.welcome_back': 'Welcome back',
    'home.popular_goals': 'Popular goals',
    'home.tell_us_who': 'Or tell us who you are',
    'home.who_are_you': 'Who are you now?',
    'home.change': 'Change',
    'home.forget_me': 'Forget me',
    'home.pickup_left': 'Pick up where you left off →',

    // Onboarding / Get Started
    'onboarding.title': 'What are you here to do?',
    'onboarding.student': 'I want to learn a skill',
    'onboarding.entrepreneur': 'I want to start a business',
    'onboarding.job_seeker': "I'm looking for work",
    'onboarding.farmer': "I'm in agriculture",
    'onboarding.corporate': "I'm building a team",

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

    // Home & Audiences / Goals
    'home.welcome_back': 'స్వాగతం',
    'home.popular_goals': 'ప్రజాదరణ పొందిన లక్ష్యాలు',
    'home.tell_us_who': 'లేదా మీ గురించి చెప్పండి',
    'home.who_are_you': 'మీరు ప్రస్తుతం ఎవరు?',
    'home.change': 'మార్చు',
    'home.forget_me': 'గుర్తుంచుకోవద్దు',
    'home.pickup_left': 'ఆపిన చోటు నుండి కొనసాగించండి →',

    // Onboarding / Get Started
    'onboarding.title': 'మీరు ఇక్కడ ఏ పనిని చేయవాలనుకుంటున్నారు?',
    'onboarding.student': 'నేను కౌశల్యం నేర్చుకోవాలనుకుంటున్నాను',
    'onboarding.entrepreneur': 'నేను ఒక వ్యాపారాన్ని ప్రారంభించాలనుకుంటున్నాను',
    'onboarding.job_seeker': 'నేను ఉద్యోగం కోసం చూస్తున్నాను',
    'onboarding.farmer': 'నేను వ్యవసాయంలో ఉన్నాను',
    'onboarding.corporate': 'నేను ఒక జట్టును నిర్మించటానికి ఉన్నాను',

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
