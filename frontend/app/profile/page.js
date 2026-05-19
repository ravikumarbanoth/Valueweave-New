"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase-browser";
import AppNavbar from "@/components/AppNavbar";

export default function MyProfilePage() {
  const supabase = createClient();
  const [profile, setProfile] = useState(null);
  const [opps, setOpps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;
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

export function ProfileView({ profile, opps, isMe }) {
  return (
    <>
      <div className="card-base p-6 md:p-8 mb-6">
        <div className="flex flex-wrap gap-5 items-center">
          {profile.picture ? (
            <img src={profile.picture} alt="" className="w-24 h-24 rounded-full border-4 border-amber-200" />
          ) : (
            <div className="w-24 h-24 rounded-full bg-amber-200 text-amber-700 flex items-center justify-center font-bold text-4xl">{(profile.name || "?")[0]}</div>
          )}
          <div className="flex-1 min-w-[200px]">
            <h1 data-testid="profile-name" className="font-display font-extrabold text-2xl tracking-tight mb-1">{profile.name}</h1>
            {profile.city && <p className="text-muted text-sm mb-2">📍 {profile.city}</p>}
            {profile.looking_for && <span className="chip bg-teal-100 text-teal-700">Looking for: {profile.looking_for.replace(/-/g, " ")}</span>}
          </div>
          {isMe && <Link href="/onboarding" data-testid="edit-profile" className="btn-secondary !py-2 !px-4 text-xs">Edit profile</Link>}
        </div>
        {profile.bio && <p className="mt-5 text-ink leading-relaxed">{profile.bio}</p>}
        {profile.skills?.length > 0 && (
          <div className="mt-5">
            <h3 className="label-display">Skills</h3>
            <div className="flex flex-wrap gap-1.5">
              {profile.skills.map(s => <span key={s} className="chip bg-stone-100 text-stone-700">{s}</span>)}
            </div>
          </div>
        )}
        {profile.interests?.length > 0 && (
          <div className="mt-4">
            <h3 className="label-display">Interests</h3>
            <div className="flex flex-wrap gap-1.5">
              {profile.interests.map(s => <span key={s} className="chip bg-teal-50 text-teal-600">{s}</span>)}
            </div>
          </div>
        )}
      </div>

      <h2 className="font-display font-extrabold text-xl mb-3">
        {isMe ? "My opportunities" : `${profile.name?.split(" ")[0]}'s opportunities`} ({opps.length})
      </h2>
      {opps.length === 0 ? (
        <div data-testid="profile-no-opps" className="card-base !border-dashed !border-2 p-9 text-center text-muted">No opportunities posted yet.</div>
      ) : (
        <div className="grid gap-3">
          {opps.map((o) => (
            <Link key={o.id} href={`/opportunities/${o.id}`} className="card-base p-4 hover:border-amber-300 transition-colors">
              <h3 className="font-display font-bold">{o.title}</h3>
              <p className="text-sm text-muted">{o.category} · {o.location}</p>
            </Link>
          ))}
        </div>
      )}
    </>
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
