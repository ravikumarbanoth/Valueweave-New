"use client";

import { useLanguage } from "@/lib/language";

export default function FooterFounder() {
  const { t } = useLanguage();
  return (
    <span data-testid="footer-founder">
      {t("footer.founded_by", "Founded by Ravi Kumar Banoth")}
    </span>
  );
}
