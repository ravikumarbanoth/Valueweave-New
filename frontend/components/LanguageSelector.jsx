'use client';

import { useEffect, useState } from 'react';
import { useLanguage, getLanguageLabel, SUPPORTED_LANGUAGES } from '@/lib/language';
import { Globe } from 'lucide-react';

export default function LanguageSelector() {
  const [isOpen, setIsOpen] = useState(false);
  const { language: currentLanguage, setLanguage } = useLanguage();

  const handleSelectLanguage = (lang) => {
    if (lang !== currentLanguage) {
      setLanguage(lang);
    }
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Select language"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        className="flex items-center gap-1.5 px-2 py-1.5 rounded-lg text-sm font-display font-semibold text-muted hover:text-ink hover:bg-stone-100 transition-colors min-h-[44px]"
        data-testid="language-selector-button"
      >
        <Globe size={15} />
        <span className="hidden sm:inline">{getLanguageLabel(currentLanguage)}</span>
        <span className="inline sm:hidden">{currentLanguage.toUpperCase()}</span>
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-30"
            onClick={() => setIsOpen(false)}
            aria-hidden="true"
          />
          <div
            className="absolute right-0 mt-1 bg-white border border-stone-200 rounded-lg shadow-lg z-40 min-w-max"
            role="listbox"
            data-testid="language-dropdown"
          >
            {SUPPORTED_LANGUAGES.map((lang) => (
              <button
                key={lang}
                onClick={() => handleSelectLanguage(lang)}
                className={`w-full text-left px-4 py-3 text-sm font-semibold transition-colors min-h-[44px] flex items-center ${
                  lang === currentLanguage
                    ? 'bg-amber-50 text-amber-700'
                    : 'text-ink hover:bg-stone-50'
                }`}
                aria-selected={lang === currentLanguage}
                role="option"
                data-testid={`language-option-${lang}`}
              >
                {getLanguageLabel(lang)}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
