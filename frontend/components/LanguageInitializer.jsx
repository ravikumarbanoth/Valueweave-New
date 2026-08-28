'use client';

import { useEffect } from 'react';
import { restoreLanguagePreference } from '@/lib/language';

/**
 * Initialize language preference on app load.
 * Must be rendered high in the component tree, before any translations are used.
 */
export default function LanguageInitializer() {
  useEffect(() => {
    restoreLanguagePreference();
  }, []);

  return null; // No UI output
}
