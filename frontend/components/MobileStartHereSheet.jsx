"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { X } from "lucide-react";

const ACTIONS = [
  { emoji: "🧠", label: "Discover Yourself", href: "/discover", bg: "bg-violet-50" },
  { emoji: "💡", label: "Business Ideas", href: "/ideas", bg: "bg-amber-50" },
  { emoji: "🤝", label: "Collaborators", href: "/collaborators", bg: "bg-teal-50" },
  { emoji: "📍", label: "District Opportunities", href: "/district", bg: "bg-emerald-50" },
];

export default function MobileStartHereSheet() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  return (
    <>
      {/* Floating button — mobile only */}
      <button
        onClick={() => setOpen(true)}
        aria-label="Start here"
        className="md:hidden fixed bottom-6 right-4 z-50 btn-primary shadow-xl shadow-amber-500/30 !py-3 !px-5 text-sm flex items-center gap-2"
      >
        <span className="text-base">✨</span>
        Start Here
      </button>

      {/* Backdrop */}
      {open && (
        <div
          className="md:hidden fixed inset-0 z-50 bg-ink/50 backdrop-blur-sm"
          onClick={() => setOpen(false)}
        />
      )}

      {/* Bottom sheet */}
      <div
        className={`md:hidden fixed inset-x-0 bottom-0 z-[60] bg-white rounded-t-3xl shadow-2xl transition-transform duration-300 ${
          open ? "translate-y-0" : "translate-y-full"
        }`}
      >
        <div className="flex items-center justify-between px-5 pt-5 pb-3">
          <div>
            <h3 className="font-display font-extrabold text-lg text-ink">Where do you want to go?</h3>
            <p className="text-xs text-muted mt-0.5">Choose your starting point</p>
          </div>
          <button
            onClick={() => setOpen(false)}
            aria-label="Close"
            className="w-9 h-9 rounded-full bg-stone-100 flex items-center justify-center hover:bg-stone-200 transition-colors"
          >
            <X size={18} className="text-ink" />
          </button>
        </div>

        <div className="px-4 pb-8 pt-2 grid grid-cols-2 gap-3">
          {ACTIONS.map((action) => (
            <Link
              key={action.href}
              href={action.href}
              onClick={() => setOpen(false)}
              className={`${action.bg} rounded-2xl p-4 flex flex-col items-center gap-2 text-center min-h-[44px] active:opacity-70 transition-opacity`}
            >
              <span className="text-3xl">{action.emoji}</span>
              <span className="font-display font-bold text-sm text-ink">{action.label}</span>
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}
