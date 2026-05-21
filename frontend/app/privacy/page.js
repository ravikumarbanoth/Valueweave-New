import LegalShell from "@/components/LegalShell";

export const metadata = { title: "Privacy — ValueWeave" };

export default function PrivacyPage() {
  return (
    <LegalShell title="Privacy Policy">
      <p>
        We collect only essential information required to operate the platform, including profile details and authentication data. We do not sell personal information.
      </p>
      <p>
        Public profile and opportunity visibility is controlled through platform settings and policies. You can choose what to share in your profile and remove your opportunities at any time.
      </p>
      <p>
        Authentication is handled through Google OAuth via Supabase. We store your email, name, and profile picture (provided by Google) along with the information you add during onboarding (skills, interests, city, bio).
      </p>
      <p>For any data-related question, write to <a href="mailto:valueweave.team@gmail.com" className="text-amber-600 font-semibold">valueweave.team@gmail.com</a>.</p>
    </LegalShell>
  );
}
