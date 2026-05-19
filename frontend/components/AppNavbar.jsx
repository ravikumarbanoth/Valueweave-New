"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { createClient } from "@/lib/supabase-browser";
import { LogOut, User as UserIcon, Inbox, Plus, Home } from "lucide-react";

export default function AppNavbar({ initialProfile = null }) {
  const supabase = createClient();
  const router = useRouter();
  const pathname = usePathname();
  const [profile, setProfile] = useState(initialProfile);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    if (initialProfile) return;
    (async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;
      const { data } = await supabase.from("profiles").select("*").eq("id", user.id).single();
      if (data) setProfile(data);
    })();
  }, [supabase, initialProfile]);

  const logout = async () => {
    await supabase.auth.signOut();
    router.push("/");
    router.refresh();
  };

  const isActive = (p) => pathname === p || (p !== "/dashboard" && pathname.startsWith(p));

  const NavItem = ({ href, label, icon: Icon, testid }) => (
    <Link
      href={href}
      data-testid={testid}
      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-semibold transition-colors ${
        isActive(href) ? "bg-amber-100 text-amber-700" : "text-muted hover:text-ink hover:bg-stone-100"
      }`}
    >
      <Icon size={15} /> {label}
    </Link>
  );

  return (
    <nav className="sticky top-0 z-40 bg-cream/90 backdrop-blur-md border-b border-stone-200">
      <div className="max-w-6xl mx-auto h-16 px-6 flex items-center justify-between">
        <Link href="/dashboard" data-testid="navbar-logo" className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500 to-yellow-400 flex items-center justify-center shadow-md shadow-amber-500/30">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 3L4 7.5V16.5L12 21L20 16.5V7.5L12 3Z" stroke="#fff" strokeWidth="2" strokeLinejoin="round"/><path d="M4 7.5L12 12M12 12L20 7.5M12 12V21" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>
          </div>
          <span className="font-display font-extrabold text-lg tracking-tight">Value<span className="text-amber-500">Weave</span></span>
        </Link>

        <div className="hidden md:flex items-center gap-1">
          <NavItem href="/dashboard" label="Feed" icon={Home} testid="nav-feed" />
          <NavItem href="/opportunities/new" label="Post" icon={Plus} testid="nav-post" />
          <NavItem href="/connections" label="Connections" icon={Inbox} testid="nav-connections" />
          <NavItem href="/profile" label="Profile" icon={UserIcon} testid="nav-profile" />
        </div>

        <div className="relative">
          <button
            data-testid="user-menu-trigger"
            onClick={() => setMenuOpen((o) => !o)}
            className="flex items-center gap-2 bg-white border border-stone-200 rounded-full pl-1 pr-3 py-1 hover:bg-stone-50"
          >
            {profile?.picture ? (
              <img src={profile.picture} alt="" className="w-7 h-7 rounded-full" />
            ) : (
              <div className="w-7 h-7 rounded-full bg-amber-200 text-amber-700 flex items-center justify-center font-bold text-xs">
                {(profile?.name || "?")[0]?.toUpperCase()}
              </div>
            )}
            <span className="hidden md:block text-xs font-semibold">{profile?.name?.split(" ")[0]}</span>
          </button>
          {menuOpen && (
            <div className="absolute right-0 top-12 bg-white border border-stone-200 rounded-xl shadow-xl py-1.5 w-48 z-50">
              <Link href="/profile" data-testid="menu-profile" className="block px-4 py-2 text-sm hover:bg-stone-50">My Profile</Link>
              <Link href="/connections" data-testid="menu-connections" className="block px-4 py-2 text-sm hover:bg-stone-50">Connections</Link>
              <div className="border-t border-stone-100 my-1" />
              <button data-testid="menu-logout" onClick={logout} className="w-full text-left px-4 py-2 text-sm text-amber-700 hover:bg-amber-50 flex items-center gap-2">
                <LogOut size={14} /> Sign out
              </button>
            </div>
          )}
        </div>
      </div>

      {/* mobile bottom nav */}
      <div className="md:hidden fixed bottom-0 inset-x-0 z-40 bg-white border-t border-stone-200 flex justify-around py-1.5">
        {[
          { href: "/dashboard", label: "Feed", icon: Home, testid: "mnav-feed" },
          { href: "/opportunities/new", label: "Post", icon: Plus, testid: "mnav-post" },
          { href: "/connections", label: "Inbox", icon: Inbox, testid: "mnav-inbox" },
          { href: "/profile", label: "Me", icon: UserIcon, testid: "mnav-profile" },
        ].map(({ href, label, icon: Icon, testid }) => (
          <Link key={href} href={href} data-testid={testid} className={`flex flex-col items-center gap-0.5 px-3 py-1 rounded-lg ${isActive(href) ? "text-amber-600" : "text-muted"}`}>
            <Icon size={20} />
            <span className="text-[10px] font-semibold">{label}</span>
          </Link>
        ))}
      </div>
    </nav>
  );
}
