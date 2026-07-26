"use client";
import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase-browser";
import AppNavbar from "@/components/AppNavbar";
import ProfileView from "@/components/ProfileView";
import IntelligencePanel from "@/components/knowledge/IntelligencePanel";
import {
  getBusinessProfile,
  getLearningProfile,
  getSkillProfile,
  intelligenceState,
} from "@/lib/intelligence";

export default function MyProfilePage() {
  const [profile, setProfile] = useState(null);
  const [opps, setOpps] = useState([]);
  const [loading, setLoading] = useState(true);
  // Phase 3 — the four intelligence tables, read not computed.
  const [intel, setIntel] = useState(null);

  useEffect(() => {
    (async () => {
      const supabase = createClient();
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) { setLoading(false); return; }
      const { data } = await supabase.from("profiles").select("*").eq("id", user.id).single();
      setProfile(data);
      const { data: o } = await supabase.from("opportunities").select("*").eq("owner_id", user.id).order("created_at", { ascending: false });
      setOpps(o || []);
      setLoading(false);

      // Loaded after the profile renders, so an absent projection never blocks
      // the page the user came for.
      const state = await intelligenceState(user.id);
      const [skill, business, learning] = state.available
        ? await Promise.all([
            getSkillProfile(user.id),
            getBusinessProfile(user.id),
            getLearningProfile(user.id),
          ])
        : [null, null, null];
      setIntel({ state, skill, business, learning });
    })();
  }, []);

  if (loading) return <Shell me={profile}><p>Loading…</p></Shell>;
  if (!profile) return <Shell me={null}><p>Profile not found.</p></Shell>;

  return (
    <Shell me={profile}>
      <ProfileView profile={profile} opps={opps} isMe />
      {intel && (
        <IntelligencePanel
          state={intel.state}
          skill={intel.skill}
          business={intel.business}
          learning={intel.learning}
          isMe
        />
      )}
    </Shell>
  );
}

function Shell({ me, children }) {
  return (
    <div className="min-h-screen bg-cream pb-20 md:pb-0">
      <AppNavbar initialProfile={me} />
      <main className="max-w-3xl mx-auto px-6 py-8">{children}</main>
    </div>
  );
}
