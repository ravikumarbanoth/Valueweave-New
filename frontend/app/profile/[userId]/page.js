"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { createClient } from "@/lib/supabase-browser";
import AppNavbar from "@/components/AppNavbar";
import { ProfileView } from "../page";

export default function UserProfilePage() {
  const supabase = createClient();
  const { userId } = useParams();
  const [me, setMe] = useState(null);
  const [profile, setProfile] = useState(null);
  const [opps, setOpps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        const { data: myProfile } = await supabase.from("profiles").select("*").eq("id", user.id).single();
        setMe(myProfile);
      }
      const { data } = await supabase.from("profiles").select("*").eq("id", userId).single();
      setProfile(data);
      const { data: o } = await supabase.from("opportunities").select("*").eq("owner_id", userId).order("created_at", { ascending: false });
      setOpps(o || []);
      setLoading(false);
    })();
  }, [supabase, userId]);

  return (
    <div className="min-h-screen bg-cream pb-20 md:pb-0">
      <AppNavbar initialProfile={me} />
      <main className="max-w-3xl mx-auto px-6 py-8">
        {loading ? <p>Loading…</p> : !profile ? <p>User not found.</p> : (
          <ProfileView profile={profile} opps={opps} isMe={me?.id === profile.id} />
        )}
      </main>
    </div>
  );
}
