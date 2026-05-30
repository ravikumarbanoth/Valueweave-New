"use client";
import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase-browser";
import AppNavbar from "@/components/AppNavbar";
import ProfileView from "@/components/ProfileView";

export default function MyProfilePage() {
  const supabase = createClient();
  const [profile, setProfile] = useState(null);
  const [opps, setOpps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) { setLoading(false); return; }
      const { data } = await supabase.from("profiles").select("*").eq("id", user.id).single();
      setProfile(data);
      const { data: o } = await supabase.from("opportunities").select("*").eq("owner_id", user.id).order("created_at", { ascending: false });
      setOpps(o || []);
      setLoading(false);
    })();
  }, [supabase]);

  if (loading) return <Shell me={profile}><p>Loading…</p></Shell>;
  if (!profile) return <Shell me={null}><p>Profile not found.</p></Shell>;

  return (
    <Shell me={profile}>
      <ProfileView profile={profile} opps={opps} isMe />
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
