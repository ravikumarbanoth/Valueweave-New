import { LegalShell } from "../about/page";

export const metadata = { title: "Terms — ValueWeave" };

export default function TermsPage() {
  return (
    <LegalShell title="Terms of Service">
      <p>By using ValueWeave, users agree to:</p>
      <ul className="list-disc pl-6 text-ink leading-relaxed space-y-2 mb-5">
        <li>provide accurate information,</li>
        <li>avoid spam or misuse,</li>
        <li>respect other users,</li>
        <li>avoid fraudulent opportunities or harmful content.</li>
      </ul>
      <p>
        ValueWeave reserves the right to moderate content and suspend abusive accounts.
      </p>
      <p>
        Questions about these terms? Reach out at <a href="mailto:valueweave.team@gmail.com" className="text-amber-600 font-semibold">valueweave.team@gmail.com</a>.
      </p>
    </LegalShell>
  );
}
