"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { createClient } from "@/lib/supabase-browser";
import AppNavbar from "@/components/AppNavbar";
import ProfileView from "@/components/ProfileView";

export default function PublicProfilePage() {
  const { id } = useParams();
  const [me, setMe] = useState(null);
  const [profile, setProfile] = useState(null);
  const [opps, setOpps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const supabase = createClient();
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        const { data: myProfile } = await supabase.from("profiles").select("*").eq("id", user.id).single();
        setMe(myProfile);
      }

      const { data: profileData } = await supabase.from("profiles").select("*").eq("id", id).single();
      setProfile(profileData);

      if (profileData) {
        const { data: posted } = await supabase
          .from("opportunities")
          .select("*")
          .eq("owner_id", id)
          .order("created_at", { ascending: false });
        setOpps(posted || []);
      }
      setLoading(false);
    })();
  }, [id]);

  if (loading) return <Shell me={me}><p>Loading…</p></Shell>;

  if (!profile) {
    return (
      <Shell me={me}>
        <div className="card-base p-10 text-center" data-testid="profile-public-not-found">
          <div className="text-5xl mb-3">🔍</div>
          <h1 className="font-display font-bold text-xl mb-2">Profile not found</h1>
          <p className="text-muted text-sm mb-5">This profile may have been removed or is unavailable.</p>
          <Link href={me ? "/dashboard" : "/"} className="btn-primary">Back to {me ? "feed" : "home"}</Link>
        </div>
      </Shell>
    );
  }

  return (
    <Shell me={me}>
      <ProfileView profile={profile} opps={opps} isMe={me?.id === profile.id} />
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
