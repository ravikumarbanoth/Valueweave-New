'use client';

import { useLanguage } from '@/lib/language';
import { Globe } from 'lucide-react';

/**
 * Global persistent floating language switcher.
 * Provides a compact, discoverable EN | తెలుగు pill fixed at the bottom-right.
 * Positioned above the Feedback widget, clear of all primary navigation and actions.
 */
export default function LanguageSelector() {
  const { language, setLanguage } = useLanguage();

  return (
    <aside
      aria-label="Language selection"
      className="fixed bottom-[4.75rem] right-4 sm:bottom-20 sm:right-5 z-40 select-none"
      data-testid="floating-language-switcher"
    >
      <div
        role="group"
        aria-label="Language switcher"
        className="flex items-center p-1 rounded-full bg-white/95 backdrop-blur-md border border-stone-200/90 shadow-lg shadow-stone-900/10 text-xs font-display font-bold transition-all hover:border-amber-300"
      >
        <div className="flex items-center pl-2 pr-1 text-stone-400" aria-hidden="true">
          <Globe size={13} />
        </div>
        <button
          type="button"
          onClick={() => setLanguage('en')}
          data-testid="language-toggle-en"
          aria-pressed={language === 'en'}
          aria-label="Switch to English"
          className={`px-3 py-1.5 rounded-full transition-all min-h-[44px] flex items-center justify-center ${
            language === 'en'
              ? 'bg-amber-500 text-white shadow-sm shadow-amber-500/30'
              : 'text-stone-600 hover:text-ink hover:bg-stone-100'
          }`}
        >
          EN
        </button>
        <span className="text-stone-300 text-[10px] mx-0.5" aria-hidden="true">
          |
        </span>
        <button
          type="button"
          onClick={() => setLanguage('te')}
          data-testid="language-toggle-te"
          aria-pressed={language === 'te'}
          aria-label="తెలుగు భాషకు మార్చండి (Switch to Telugu)"
          className={`px-3 py-1.5 rounded-full transition-all min-h-[44px] flex items-center justify-center font-medium ${
            language === 'te'
              ? 'bg-amber-500 text-white shadow-sm shadow-amber-500/30'
              : 'text-stone-600 hover:text-ink hover:bg-stone-100'
          }`}
        >
          తెలుగు
        </button>
      </div>
    </aside>
  );
}
