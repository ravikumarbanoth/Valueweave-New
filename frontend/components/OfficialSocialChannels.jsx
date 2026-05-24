import SocialLinks from "@/components/SocialLinks";

// Drop-in block for the About / Contact page. Self-contained card matching the
// existing card-base / font-display system. Usage: <OfficialSocialChannels />
export default function OfficialSocialChannels() {
  return (
    <section className="card-base p-6" data-testid="official-social-channels">
      <h2 className="font-display font-bold text-lg mb-1">Official Social Channels</h2>
      <p className="text-sm text-muted mb-4 max-w-md">
        Follow the journey of Bharat&apos;s next builders — updates, stories, and opportunities from the ValueWeave community.
      </p>
      <SocialLinks variant="icon" />
    </section>
  );
}
