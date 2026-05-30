import Link from "next/link";

export default function ProfileView({ profile, opps, isMe = false }) {
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
              {profile.skills.map((skill) => <span key={skill} className="chip bg-stone-100 text-stone-700">{skill}</span>)}
            </div>
          </div>
        )}
        {profile.interests?.length > 0 && (
          <div className="mt-4">
            <h3 className="label-display">Interests</h3>
            <div className="flex flex-wrap gap-1.5">
              {profile.interests.map((interest) => <span key={interest} className="chip bg-teal-50 text-teal-600">{interest}</span>)}
            </div>
          </div>
        )}
      </div>

      <h2 className="font-display font-extrabold text-xl mb-3">
        {isMe ? "My opportunities" : `${profile.name?.split(" ")[0] || "Builder"}'s opportunities`} ({opps.length})
      </h2>
      {opps.length === 0 ? (
        <div data-testid="profile-no-opps" className="card-base !border-dashed !border-2 p-9 text-center text-muted">No opportunities posted yet.</div>
      ) : (
        <div className="grid gap-3">
          {opps.map((opp) => (
            <Link key={opp.id} href={`/opportunities/${opp.id}`} className="card-base p-4 hover:border-amber-300 transition-colors">
              <h3 className="font-display font-bold">{opp.title}</h3>
              <p className="text-sm text-muted">{opp.category} · {opp.location}</p>
            </Link>
          ))}
        </div>
      )}
    </>
  );
}
