"use client";
import { useState } from "react";
import Link from "next/link";
import { Menu, X } from "lucide-react";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/discover", label: "🧠 Discover Yourself" },
  { href: "/ideas", label: "💡 Business Ideas" },
  { href: "/explore", label: "🚀 Opportunities" },
  { href: "/collaborators", label: "🤝 Collaborators" },
  { href: "/district", label: "📍 Districts" },
  { href: "/research", label: "📊 Research" },
  { href: "/questions", label: "❓ Q&A" },
];

export default function MobileNavMenu() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setOpen((o) => !o)}
        aria-label={open ? "Close menu" : "Open menu"}
        className="md:hidden w-10 h-10 flex items-center justify-center rounded-lg hover:bg-stone-100 transition-colors min-h-[44px] min-w-[44px]"
      >
        {open ? <X size={20} className="text-ink" /> : <Menu size={20} className="text-ink" />}
      </button>

      {/* Backdrop */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-ink/30 backdrop-blur-sm md:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      {/* Dropdown */}
      <div
        className={`md:hidden fixed top-16 inset-x-0 z-50 bg-white border-b border-stone-200 shadow-xl transition-all duration-200 ${
          open ? "opacity-100 pointer-events-auto translate-y-0" : "opacity-0 pointer-events-none -translate-y-2"
        }`}
      >
        <nav className="px-4 py-3 flex flex-col gap-0.5">
          {LINKS.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              onClick={() => setOpen(false)}
              className="flex items-center px-3 py-3 rounded-xl text-sm font-display font-semibold text-ink hover:bg-amber-50 hover:text-amber-700 transition-colors min-h-[44px]"
            >
              {l.label}
            </Link>
          ))}
          <div className="border-t border-stone-100 my-2" />
          <Link href="/signin" onClick={() => setOpen(false)} className="btn-secondary w-full justify-center text-sm">Sign in</Link>
          <Link href="/get-started" onClick={() => setOpen(false)} className="btn-primary w-full justify-center text-sm mt-1">Join ValueWeave →</Link>
        </nav>
      </div>
    </>
  );
}
