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
      {/* PX Phase 10. Phase 9 began storing something on the reader's device
          and this page did not say so. It is one word, it never leaves the
          browser, and there is a button that deletes it — but a policy that
          omits a thing because the thing is small is still a policy that
          omits it. */}
      <p>
        If you tell us who you are on the home page — student, farmer,
        entrepreneur and so on — we keep that one word in your own browser so
        we can greet you and put matching results nearer the top. It is not
        sent to us, it is not linked to any account, and nothing is ever
        hidden from you because of it. &ldquo;Forget me&rdquo; on the home page
        deletes it.
      </p>
      <p>For any data-related question, write to <a href="mailto:valueweave.team@gmail.com" className="text-amber-600 font-semibold">valueweave.team@gmail.com</a>.</p>
    </LegalShell>
  );
}
