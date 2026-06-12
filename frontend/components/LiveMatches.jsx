"use client";
// Discover Yourself → marketplace bridge (Phase 3 + 4).
// After the assessment, shows live opportunities matched to the user's
// district + archetype, recommended collaborators, and lets a signed-in
// user publish their collaborator profile to the marketplace.

import { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase-browser";
import OpportunityCard from "@/components/OpportunityCard";
import CollaboratorCard from "@/components/CollaboratorCard";
import {
  ARCHETYPE_CATEGORY_MAP,
  ARCHETYPE_FOUNDER_ROLE,
  COMPLEMENTARY_ARCHETYPES,
} from "@/lib/collab";

// Assessment sector dimensions → marketplace category ids
const SECTOR_TO_CATEGORY = {
  Technology: "ai-tech",
  Agriculture: "agri",
  Healthcare: "healthcare",
  Education: "education",
  Manufacturing: "manufacturing",
  Food: "local-business",
  Finance: "local-business",
  Government: "education",
};

export default function LiveMatches({ profile }) {
  const supabase = createClient();
  const [opps, setOpps] = useState([]);
  const [collabs, setCollabs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState("");

  const categories = useMemo(
    () => ARCHETYPE_CATEGORY_MAP[profile.archetype] || ["local-business"],
    [profile.archetype]
  );
  const topSectors = useMemo(() => {
    const ranked = Object.entries(profile.sectorScores || {})
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([k]) => SECTOR_TO_CATEGORY[k])
      .filter(Boolean);
    return [...new Set(ranked)];
  }, [profile.sectorScores]);

  useEffect(() => {
    (async () => {
      try {
        const { data: { user: u } } = await supabase.auth.getUser();
        setUser(u || null);

        // Recommended opportunities: archetype categories, district first.
        let district = [];
        if (profile.district && profile.district !== "Unknown") {
          const { data } = await supabase
            .from("opportunities")
            .select("*, owner:profiles!opportunities_owner_id_fkey(id,name,picture)")
            .eq("status", "open")
            .eq("district", profile.district)
            .in("category", [...new Set([...categories, ...topSectors])])
            .limit(6);
          district = data || [];
        }
        if (district.length < 6) {
          const { data } = await supabase
            .from("opportunities")
            .select("*, owner:profiles!opportunities_owner_id_fkey(id,name,picture)")
            .eq("status", "open")
            .in("category", categories)
            .order("created_at", { ascending: false })
            .limit(6 - district.length);
          const seen = new Set(district.map((o) => o.id));
          district = [...district, ...(data || []).filter((o) => !seen.has(o.id))];
        }
        setOpps(district);

        // Recommended collaborators: complementary archetypes, same state preferred.
        const complementary = COMPLEMENTARY_ARCHETYPES[profile.archetype] || [];
        let cq = supabase
          .from("collaborator_profiles")
          .select("*")
          .eq("open_to_collaborate", true)
          .in("archetype", complementary.length ? complementary : ["Builder"])
          .limit(6);
        if (profile.state && profile.state !== "Unknown") cq = cq.eq("state", profile.state);
        let { data: cdata } = await cq;
        if (!cdata?.length) {
          const { data: any } = await supabase
            .from("collaborator_profiles")
            .select("*")
            .eq("open_to_collaborate", true)
            .limit(6);
          cdata = any || [];
        }
        if (u) cdata = (cdata || []).filter((c) => c.user_id !== u.id);
        setCollabs(cdata || []);

        if (u) {
          const { data: mine } = await supabase
            .from("collaborator_profiles")
            .select("user_id")
            .eq("user_id", u.id)
            .maybeSingle();
          if (mine) setSaved(true);
        }
      } catch {
        // fail soft — sections render empty states
      }
      setLoading(false);
    })();
  }, [supabase, profile, categories, topSectors]);

  async function saveProfile() {
    setSaving(true);
    setErr("");
    const { error } = await supabase.from("collaborator_profiles").upsert({
      user_id: user.id,
      archetype: profile.archetype,
      secondary_archetype: profile.secondaryArchetype || null,
      founder_role: ARCHETYPE_FOUNDER_ROLE[profile.archetype] || null,
      district: profile.district !== "Unknown" ? profile.district : null,
      state: profile.state !== "Unknown" ? profile.state : null,
      top_sectors: topSectors,
      top_idea: profile.ideas?.[0]?.name || null,
      budget: profile.budgetLabel !== "—" ? profile.budgetLabel : null,
      ep_score: profile.epScore ?? null,
      open_to_collaborate: true,
    });
    if (error) setErr(`Could not save profile: ${error.message}`);
    else setSaved(true);
    setSaving(false);
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Publish profile */}
      <div className="rounded-2xl border border-teal-200 bg-teal-50 p-5">
        <h3 className="font-display font-bold text-base text-ink mb-1">
          {saved ? "✅ You're on the collaborator marketplace" : "Join the collaborator marketplace"}
        </h3>
        <p className="text-sm text-muted mb-4">
          {saved
            ? "Founders and co-builders can now discover your profile. Update it anytime by retaking the assessment."
            : `Publish your ${profile.archetype} profile — founder role, district, sectors, and budget — so opportunities and co-founders can find you.`}
        </p>
        {err && <p className="text-sm text-rose-700 mb-3">{err}</p>}
        {!saved && (
          user ? (
            <button data-testid="save-collab-profile" onClick={saveProfile} disabled={saving} className="btn-teal !py-2.5 text-sm disabled:opacity-50">
              {saving ? "Publishing…" : "Publish my collaborator profile"}
            </button>
          ) : (
            <Link href="/get-started" className="btn-teal !py-2.5 text-sm">Sign in to publish your profile</Link>
          )
        )}
        {saved && (
          <Link href="/collaborators" className="btn-secondary !py-2.5 text-sm">View the marketplace →</Link>
        )}
      </div>

      {/* Recommended opportunities */}
      <div>
        <h3 className="font-display font-extrabold text-lg text-ink mb-1">Live opportunities for you</h3>
        <p className="text-muted text-sm mb-4">
          Matched to your <span className="font-semibold">{profile.archetype}</span> archetype
          {profile.district && profile.district !== "Unknown" ? <> and <span className="font-semibold">{profile.district}</span></> : null}.
        </p>
        {loading ? (
          <div className="grid sm:grid-cols-2 gap-4">{[1, 2].map((i) => <div key={i} className="skeleton h-48" />)}</div>
        ) : opps.length === 0 ? (
          <div className="card-base !border-dashed !border-2 p-8 text-center">
            <p className="text-muted text-sm mb-3">No live matches yet — browse the full marketplace.</p>
            <Link href="/explore" className="btn-secondary !py-2.5 text-sm">Explore opportunities</Link>
          </div>
        ) : (
          <>
            <div className="grid sm:grid-cols-2 gap-4">
              {opps.map((opp) => <OpportunityCard key={opp.id} opp={opp} />)}
            </div>
            <div className="mt-4 text-center">
              <Link href="/explore" className="text-sm font-display font-bold text-amber-700 hover:text-amber-800">
                Browse all opportunities →
              </Link>
            </div>
          </>
        )}
      </div>

      {/* Recommended collaborators */}
      <div>
        <h3 className="font-display font-extrabold text-lg text-ink mb-1">Collaborators who complement you</h3>
        <p className="text-muted text-sm mb-4">
          A {profile.archetype} pairs best with {(COMPLEMENTARY_ARCHETYPES[profile.archetype] || []).join(", ")} archetypes.
        </p>
        {loading ? (
          <div className="grid sm:grid-cols-2 gap-4">{[1, 2].map((i) => <div key={i} className="skeleton h-40" />)}</div>
        ) : collabs.length === 0 ? (
          <div className="card-base !border-dashed !border-2 p-8 text-center">
            <p className="text-muted text-sm mb-3">No collaborator profiles yet — invite co-builders to take the assessment.</p>
            <Link href="/collaborators" className="btn-secondary !py-2.5 text-sm">View marketplace</Link>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 gap-4">
            {collabs.map((c) => <CollaboratorCard key={c.user_id} collaborator={c} />)}
          </div>
        )}
      </div>
    </div>
  );
}
