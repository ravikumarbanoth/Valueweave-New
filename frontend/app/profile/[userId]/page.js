"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { createClient } from "@/lib/supabase-browser";
import AppNavbar from "@/components/AppNavbar";
import ShareButton from "@/components/ShareButton";
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
    <div className="min-h-screen bg-cream pb-24 md:pb-12">
      <AppNavbar initialProfile={me} />
      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        {loading ? (
          <div className="card-base p-6 md:p-8">
            <div className="flex gap-5 items-center">
              <div className="skeleton w-24 h-24 !rounded-full" />
              <div className="flex-1">
                <div className="skeleton h-7 w-40 mb-2" />
                <div className="skeleton h-4 w-24" />
              </div>
            </div>
          </div>
        ) : !profile ? (
          <div className="card-base p-10 text-center" data-testid="profile-not-found">
            <div className="text-5xl mb-3">🔍</div>
            <h2 className="font-display font-bold text-xl mb-2">Profile not found</h2>
            <Link href={me ? "/dashboard" : "/"} className="btn-primary">Back to {me ? "feed" : "home"}</Link>
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between flex-wrap gap-3 mb-4">
              <Link href={me ? "/dashboard" : "/"} className="text-sm font-display font-semibold text-muted hover:text-ink">
                ← {me ? "Back to feed" : "Back to home"}
              </Link>
              <ShareButton url={`/profile/${profile.id}`} title={`${profile.name} on ValueWeave`} />
            </div>
            <ProfileView profile={profile} opps={opps} isMe={me?.id === profile.id} />
            {!me && (
              <div className="mt-6 bg-amber-50 border border-amber-200 rounded-2xl p-5 text-center">
                <p className="text-sm text-muted mb-3">Want to connect with {profile.name?.split(" ")[0]} or post your own opportunity?</p>
                <Link href="/get-started" className="btn-primary">Join ValueWeave →</Link>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
