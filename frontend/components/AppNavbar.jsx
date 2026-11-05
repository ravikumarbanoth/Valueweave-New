"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { createClient } from "@/lib/supabase-browser";
import { LogOut, User as UserIcon, Inbox, Plus, Home } from "lucide-react";
import SocialLinks from "@/components/SocialLinks";
import NotificationBell from "@/components/NotificationBell";
import MobileNavMenu from "@/components/MobileNavMenu";
import HeaderActions from "@/components/HeaderActions";
import { useLanguage } from "@/lib/language";

const PUBLIC_LINKS = [
  { href: "/discover", label: "Discover" },
  { href: "/ideas", label: "Idea Library" },
  { href: "/research", label: "Research" },
  { href: "/districts", label: "Districts" },
  { href: "/opportunity-radar", label: "Opportunity Radar" },
  { href: "/collaborators", label: "Collaborators" },
];

export default function AppNavbar({ initialProfile = null }) {
  const supabase = createClient();
  const router = useRouter();
  const pathname = usePathname();
  const [profile, setProfile] = useState(initialProfile);
  const [authed, setAuthed] = useState(initialProfile ? true : null);
  const [menuOpen, setMenuOpen] = useState(false);
  const { t } = useLanguage();

  useEffect(() => {
    if (initialProfile) { setAuthed(true); return; }
    (async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) { setAuthed(false); return; }
      setAuthed(true);
      const { data } = await supabase.from("profiles").select("*").eq("id", user.id).single();
      if (data) setProfile(data);
    })();
  }, [supabase, initialProfile]);

  const logout = async () => {
    await supabase.auth.signOut();
    router.push("/");
    router.refresh();
  };

  const isActive = (p) => pathname === p || pathname.startsWith(`${p}/`);
  const logoHref = authed ? "/dashboard" : "/";

  const NavItem = ({ href, label, icon: Icon, testid }) => (
    <Link
      href={href}
      data-testid={testid}
      //: px-2 below lg, px-3 from lg. 768px is the tightest band in the whole
      //: header: it is the first width where these four links appear AND the
      //: last where the row still has to hold the brand plus four action
      //: tiles. Measured there the row wanted 786px of a 768px viewport. Four
      //: links at 8px less horizontal padding give 32px back; from lg the
      //: padding is the original px-3, so the desktop row is unchanged.
      className={`flex items-center gap-1.5 px-2 lg:px-3 py-1.5 rounded-lg text-sm font-display font-semibold transition-colors ${
        isActive(href) ? "bg-amber-100 text-amber-700" : "text-muted hover:text-ink hover:bg-stone-100"
      }`}
    >
      <Icon size={15} /> {t(`nav.${label.toLowerCase()}`, label)}
    </Link>
  );

  return (
    <>
      <nav className="sticky top-0 z-40 bg-cream/90 backdrop-blur-md border-b border-stone-200">
        {/*
          THREE COLUMNS BELOW md, ONE FLEX ROW FROM md — the same arrangement
          HomeNavClient uses, so the header does not change shape as a reader
          moves between the landing page and everything else.

          Below md: hamburger (signed out) in the first track, brand centred in
          its own track, icon tiles in the third.
          From md:   brand left, navigation beside it, cluster pushed right.
          From 1152: the signed-out inline links and sign-in/join join the row.

          THE BUG THIS REPLACES: the logo was `absolute left-1/2
          -translate-x-1/2` below lg. Absolute positioning takes it OUT OF
          FLOW, so the right-hand cluster was laid out as though the brand did
          not exist. Signed out that cluster is two tiles and nothing touched;
          signed in it is four — search, YouTube, notifications, avatar — and
          its left edge crossed the centre line and sat on top of the
          wordmark. Desktop was unaffected because the logo was `lg:static`
          there, and the landing page was unaffected because HomeNavClient
          never shows the bell or the avatar.

          So the fix is not more margin, it is putting the brand back in flow.
          A three-column grid gives each part its own track: the centre track
          is `minmax(0, 1fr)`, which is the grid spelling of `min-width: 0` —
          without it a long brand would refuse to shrink and push the icons
          off-screen again, which is the same bug wearing a different hat.

          The grid-to-flex boundary is md, not lg, and that was the second bug.
          The signed-in navigation items are `hidden md:flex`, so between 768
          and 1023 the row had FOUR children in THREE tracks: the fourth wrapped
          onto a second line, 244px below the brand. Overlap checks cannot see
          that — things on different rows do not overlap — so the measurement
          now also asserts every header element shares one row top.

          The hamburger renders for signed-out readers only, which is existing
          behaviour: a signed-in reader gets the bottom tab bar at the end of
          this component instead.
        */}
        <div className="max-w-6xl mx-auto h-16 px-3 sm:px-4 lg:px-6
                        grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-2
                        md:flex md:gap-3">
          {/*
            `authed !== true` rather than `authed === false`, so the hamburger
            is in the server-rendered HTML too. A signed-in reader loses it on
            hydration and gets the bottom tab bar instead, which is the
            existing behaviour; a signed-out one — and a crawler, and anyone
            whose JavaScript has not arrived yet — sees it immediately rather
            than watching the left of the header fill in.

            The wrapper stays even when the button inside it does not, so the
            grid keeps three tracks and the brand does not jump sideways
            between the signed-out and signed-in renders of the same page.

            `md:empty:hidden` is why it does not stay in the FLEX layout. An
            empty flex child is still a flex child: it was contributing a 12px
            gap at 768px for a button that is not there. Below md it must keep
            occupying its grid track (that is what centres the brand), so the
            hiding is gated on md, and `empty:` means it only applies on the
            signed-in render where the button is genuinely absent.

            It now hides at 1152 rather than lg, in step with the inline links
            it hands over to — see the note on those below.
          */}
          <div className="flex items-center shrink-0 min-[1152px]:hidden md:empty:hidden">
            {authed !== true && <MobileNavMenu />}
          </div>

          <Link
            href={logoHref}
            data-testid="navbar-logo"
            className="flex items-center gap-2.5 min-w-0 min-h-[44px]
                       justify-self-center md:justify-self-start md:shrink-0"
          >
            <div className="w-9 h-9 shrink-0 rounded-xl bg-gradient-to-br from-amber-500 to-yellow-400 flex items-center justify-center shadow-md shadow-amber-500/30">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 3L4 7.5V16.5L12 21L20 16.5V7.5L12 3Z" stroke="#fff" strokeWidth="2" strokeLinejoin="round"/><path d="M4 7.5L12 12M12 12L20 7.5M12 12V21" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>
            </div>
            {/*
              COMPACT BRAND ON THE NARROWEST PHONES. At 320–360px the signed-in
              row cannot hold a 44px hamburger, the mark, a 95px wordmark and
              four action tiles — the arithmetic does not work at any spacing,
              so something has to give and it should be the least informative
              thing. The mark stays, the word goes, and it returns at 400px
              where it measurably fits. `truncate` is the belt to that braces:
              if a future brand string grows, it ellipses inside its own track
              instead of shoving the icons.
            */}
            <span className="hidden min-[400px]:inline truncate font-display font-extrabold text-lg tracking-tight">
              Value<span className="text-amber-500">Weave</span>
            </span>
          </Link>

          {authed && (
            <div className="hidden md:flex items-center gap-1">
              <NavItem href="/dashboard" label="Feed" icon={Home} testid="nav-feed" />
              <NavItem href="/opportunities/new" label="Post" icon={Plus} testid="nav-post" />
              <NavItem href="/connections" label="Inbox" icon={Inbox} testid="nav-connections" />
              <NavItem href="/profile" label="Profile" icon={UserIcon} testid="nav-profile" />
            </div>
          )}

          {/*
            ONE RIGHT-HAND CLUSTER, AND HeaderActions SITS OUTSIDE THE AUTH GATE.

            This was a real bug, and a browser test could not see it. `authed`
            starts as null and is resolved in an effect, so on the SERVER
            neither the `authed === false` nor the `authed` branch renders.
            With the icons inside those branches the server-rendered HTML of
            all 36 AppNavbar routes had no search button, no YouTube link and
            no hamburger — they appeared only once JavaScript had run. The
            Playwright pass went green because by then it had.

            Search and the YouTube channel do not depend on who is reading, so
            they render unconditionally and are in the first HTML byte. Only
            the things that genuinely differ by auth state stay gated.
          */}
          <div className="flex items-center gap-1.5 sm:gap-2 justify-self-end md:ml-auto">
            {/*
              THE SIX PUBLIC LINKS APPEAR AT 1152px, NOT AT lg (1024).

              This is a PRE-EXISTING overflow this patch inherits rather than
              causes, but it is the same defect and the same six lines of
              layout, so it is fixed here. Measured on committed HEAD the
              signed-out row wanted 1036px inside a 1024px viewport, so
              /research, /knowledge, /schemes and /districts each carried a
              horizontal scrollbar on a 1024px laptop. It arrived with the
              header search and YouTube tiles (96px plus a gap) earlier in this
              milestone and went unnoticed because 1024 was not in the viewport
              matrix. It is now.

              Trimming the links' padding was tried first and is not enough.
              At px-3 the English row fit 1024 with ONE pixel to spare, and in
              Telugu — which this site ships — "కనుగొనండి" and friends needed
              976px of a 976px content box, so a label wrapped and its link
              grew from 40px to 52px tall. Padding cannot buy 100px.

              1152px is max-w-6xl itself: the width at which the container
              stops growing, so the content box is 1104px at that viewport and
              every wider one. The links keep their original px-5 and the
              desktop row is unchanged. Between 1024 and 1151 the hamburger
              covers instead — and it already lists all six of these links
              plus sign-in and join, so not one route in is lost.
            */}
            {authed === false && (
              <div className="hidden min-[1152px]:flex items-center gap-1">
                {PUBLIC_LINKS.map((link) => (
                  //: `!px-3 min-[1100px]:!px-5` — a PRE-EXISTING overflow, not one this
                  //: patch introduced, but it is the same defect class and the
                  //: same six lines of layout, so it is fixed here rather than
                  //: left behind. Measured on committed HEAD the signed-out
                  //: row needed 1036px at a 1024px viewport, so /research,
                  //: /knowledge, /schemes and /districts all carried a
                  //: horizontal scrollbar on a 1024px laptop. It arrived with
                  //: the header search and YouTube tiles (96px + gap) earlier
                  //: in this milestone and was missed because 1024 was not in
                  //: the viewport matrix — 1024 is now in it. btn-ghost is
                  <Link key={link.href} href={link.href} className={`btn-ghost text-xs ${isActive(link.href) ? "!bg-amber-100 !text-amber-700" : ""}`}>
                    {t(`nav.${link.label.toLowerCase().replaceAll(" ", "-")}`, link.label)}
                  </Link>
                ))}
              </div>
            )}

            {/*
              HeaderActions replaces the SocialLinks row that used to sit here.
              It carries the same YouTube channel — both read useSocialUrls() —
              so this is not a second copy of the URL, and showing SocialLinks
              as well would put YouTube in the header twice. X and Instagram
              remain in the footer and in the signed-in user menu, which is
              where they were reachable from on a phone anyway: that row was
              `hidden sm:flex`.
            */}
            <HeaderActions />

            {authed === false && (
              <>
                {/* PX Phase 10: at 390px this wrapped to two lines — a pill
                    reading "Sign / in". Found in a screenshot, not by the
                    crawl: a wrapped button gets TALLER, so no height check
                    catches it. Nothing else changes; the words simply stay on
                    one line. Both are hidden below 1152px now — the same
                    breakpoint as the six links above, because they are part of
                    the same row that did not fit; the hamburger drawer ends
                    with these two links, so no route in is lost. */}
                <Link href="/signin" data-testid="nav-public-signin" className="btn-secondary !py-2 !px-4 text-sm whitespace-nowrap hidden min-[1152px]:inline-flex">{t("nav.signin", "Sign in")}</Link>
                <Link href="/get-started" data-testid="nav-public-join" className="btn-primary !py-2 !px-4 text-sm whitespace-nowrap hidden min-[1152px]:inline-flex">{t("nav.join_short", "Join")}</Link>
              </>
            )}

            {authed && <NotificationBell />}

            {/*
              The avatar used to be a FOURTH sibling of the row. Under the grid
              that would have opened a fourth track and shoved the brand
              further left on exactly the signed-in pages this is fixing, so it
              now lives inside the one right-hand cluster with everything else.
              Its dropdown is still positioned against this wrapper, so the
              menu itself is unchanged.
            */}
            {authed && (
            <div className="relative shrink-0">
              <button
                data-testid="user-menu-trigger"
                onClick={() => setMenuOpen((o) => !o)}
                //: pr-2 below sm — with no name beside it the old pr-3 was
                //: padding against nothing. pl-1.5 rather than pl-1 because
                //: measuring the tap target showed 1px border + 4 + 28 + 8 +
                //: 1px = 42px wide: the trim had taken the avatar UNDER the
                //: 44px minimum every other control in this row meets. 6 + 28
                //: + 8 + 2 = 44 exactly, so the avatar no longer passes on its
                //: height alone.
                className="flex items-center gap-2 bg-white border border-stone-200 rounded-full pl-1.5 pr-2 sm:pr-3 py-1 hover:bg-stone-50 min-h-[44px]"
              >
                {profile?.picture ? (
                  <img src={profile.picture} alt="" className="w-7 h-7 rounded-full" />
                ) : (
                  <div className="w-7 h-7 rounded-full bg-amber-200 text-amber-700 flex items-center justify-center font-bold text-xs">
                    {(profile?.name || "?")[0]?.toUpperCase()}
                  </div>
                )}
                {/*
                  The first name appears from lg, not md. It is the one
                  unbounded-width element in the row: "Ravi" costs 24px and
                  "Venkateswarlu" costs about 80, so at 768px — where the four
                  nav links are also present — whether the header overflows
                  depended on who was signed in. Capping it with truncate would
                  have meant an ellipsed name; deferring it to lg means the
                  tablet row shows the avatar alone, exactly as the phone row
                  does, and the name is still in the menu it opens.
                */}
                <span className="hidden lg:block text-xs font-semibold">{profile?.name?.split(" ")[0]}</span>
              </button>
              {menuOpen && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setMenuOpen(false)} />
                  <div className="absolute right-0 top-12 bg-white border border-stone-200 rounded-xl shadow-xl py-1.5 w-52 z-50">
                    <Link href="/" data-testid="menu-home" className="block px-4 py-2.5 text-sm hover:bg-stone-50">{t("nav.home", "Home")}</Link>
                    <Link href="/profile" data-testid="menu-profile" className="block px-4 py-2.5 text-sm hover:bg-stone-50">{t("nav.my_profile", "My Profile")}</Link>
                    <Link href="/connections" data-testid="menu-connections" className="block px-4 py-2.5 text-sm hover:bg-stone-50">{t("nav.connections", "Connections")}</Link>
                    <div className="border-t border-stone-100 my-1" />
                    <button data-testid="menu-logout" onClick={logout} className="w-full text-left px-4 py-2.5 text-sm text-amber-700 hover:bg-amber-50 flex items-center gap-2">
                      <LogOut size={14} /> {t("nav.signout", "Sign out")}
                    </button>
                    <div className="border-t border-stone-100 my-1" />
                    <div className="px-2 py-1.5">
                      <p className="px-2 text-[10px] uppercase tracking-wider text-stone-400 font-display font-bold mb-1">{t("footer.follow_title", "Follow ValueWeave")}</p>
                      <SocialLinks variant="inline" size={16} />
                    </div>
                  </div>
                </>
              )}
            </div>
            )}
          </div>
        </div>
      </nav>

      {authed && (
        <div className="md:hidden fixed bottom-0 inset-x-0 z-40 bg-white border-t border-stone-200 flex justify-around py-1.5 pb-[max(0.375rem,env(safe-area-inset-bottom))]">
          {[
            { href: "/dashboard", label: "Feed", icon: Home, testid: "mnav-feed" },
            { href: "/opportunities/new", label: "Post", icon: Plus, testid: "mnav-post" },
            { href: "/connections", label: "Inbox", icon: Inbox, testid: "mnav-inbox" },
            { href: "/profile", label: "Me", icon: UserIcon, testid: "mnav-profile" },
          ].map(({ href, label, icon: Icon, testid }) => (
            <Link key={href} href={href} data-testid={testid} className={`flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-lg ${isActive(href) ? "text-amber-600" : "text-muted"}`}>
              <Icon size={20} />
              <span className="text-[10px] font-semibold font-display">{label === "Me" ? t("nav.me", "Me") : t(`nav.${label.toLowerCase()}`, label)}</span>
            </Link>
          ))}
        </div>
      )}
    </>
  );
}
