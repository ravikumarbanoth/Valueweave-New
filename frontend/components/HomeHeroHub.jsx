"use client";
// The hero's hub: ValueWeave in the middle, eight things it connects around
// it, every one a link to the existing page for that thing.
//
// Positions are percentages of the diagram box, and the SVG lines are drawn in
// the same 0–100 box (preserveAspectRatio="none"), so a line always ends on
// its node at any width. Two layouts: a tall ellipse with icon-and-label nodes
// below lg, a wide one with a one-line description from lg up.
//
// Client only because the labels follow the language switcher; there is no
// state or effect, and the diagram itself is static markup.
import Link from "next/link";
import {
  BookOpen, Landmark, GraduationCap, Lightbulb, MapPin, Factory, Users, Network,
} from "lucide-react";
import { useLanguage } from "@/lib/language";

// Every href is an existing route. Order is clockwise from the top.
const NODES = [
  { key: "research",     href: "/research",                 icon: BookOpen,      label: "Research Articles",      desc: "Practical studies and guides" },
  { key: "schemes",      href: "/schemes",                  icon: Landmark,      label: "Government Schemes",     desc: "Support, subsidies and loans" },
  { key: "skills",       href: "/skills",                   icon: GraduationCap, label: "Skills & Training",      desc: "What to learn, and where" },
  { key: "ideas",        href: "/ideas",                    icon: Lightbulb,     label: "Business Ideas",         desc: "Ideas people actually start" },
  { key: "districts",    href: "/districts",                icon: MapPin,        label: "Districts",              desc: "What is around you" },
  { key: "industries",   href: "/knowledge?type=industry",  icon: Factory,       label: "Industries",             desc: "Sectors and who they employ" },
  { key: "collaborate",  href: "/collaborators",            icon: Users,         label: "Collaboration",          desc: "Like-minded people to build with" },
  { key: "networks",     href: "/network",                  icon: Network,       label: "Networks & Institutions", desc: "Colleges, lenders, providers" },
];

// Eight points on an ellipse, starting at the top, 45° apart. Used from lg up,
// where there is room on every side.
function ring(rx, ry) {
  return NODES.map((_, i) => {
    const a = (-90 + i * 45) * (Math.PI / 180);
    return { x: +(50 + rx * Math.cos(a)).toFixed(2), y: +(50 + ry * Math.sin(a)).toFixed(2) };
  });
}
const WIDE = ring(39, 38);

// Below lg: one node above the hub, one below, three down each side. An even
// ring put neighbouring nodes only ~45px apart vertically at 360px, which was
// fine for English and collided as soon as a Telugu label wrapped to a third
// line. In this shape the side nodes are a third of the width away from the
// top and bottom ones, so no label length can make two nodes touch.
// Same clockwise order as NODES.
const NARROW = [
  { x: 50, y: 8 }, { x: 83, y: 26 }, { x: 83, y: 50 }, { x: 83, y: 74 },
  { x: 50, y: 92 }, { x: 17, y: 74 }, { x: 17, y: 50 }, { x: 17, y: 26 },
];

// A gentle curve from the hub to a node: the control point is pulled a little
// off the straight line so the spokes read as connections, not a clock face.
function spoke({ x, y }) {
  const mx = (50 + x) / 2, my = (50 + y) / 2;
  const cx = mx + (y - 50) * 0.12, cy = my - (x - 50) * 0.12;
  return `M50,50 Q${cx.toFixed(2)},${cy.toFixed(2)} ${x},${y}`;
}
// The outer ring joining each node to the next: everything is connected to
// everything, not only to the centre.
function outline(points) {
  return points.map((p, i) => `${i ? "L" : "M"}${p.x},${p.y}`).join(" ") + " Z";
}

function Lines({ points, className }) {
  return (
    <svg aria-hidden="true" className={`absolute inset-0 w-full h-full ${className}`} viewBox="0 0 100 100" preserveAspectRatio="none">
      <path d={outline(points)} className="vw-rail" />
      {points.map((p, i) => <path key={i} d={spoke(p)} className="vw-hub-spoke" />)}
    </svg>
  );
}

export default function HomeHeroHub() {
  const { t } = useLanguage();

  return (
    <div data-testid="home-hub" className="relative mt-14 sm:mt-16">
      <div className="text-center max-w-2xl mx-auto px-2">
        <p className="font-display font-bold text-xs sm:text-sm tracking-[0.18em] uppercase text-amber-600">
          {t("hub.tagline", "Discover the connections. Unlock the opportunities.")}
        </p>
        <h2 className="mt-3 font-display font-extrabold text-2xl sm:text-3xl md:text-4xl tracking-tight leading-tight text-ink">
          {t("hub.title", "Discover connections for your next opportunity")}
        </h2>
        <p className="mt-3 text-muted text-sm sm:text-base leading-relaxed">
          {t("hub.subtitle", "Explore business ideas, government support, skills, research, districts and people that can help turn information into action.")}
        </p>
      </div>

      <nav
        aria-label={t("hub.nav_label", "What ValueWeave connects")}
        className="relative mx-auto mt-6 max-w-5xl aspect-[3/4] sm:aspect-[5/4] lg:aspect-[16/9]"
      >
        <Lines points={NARROW} className="lg:hidden" />
        <Lines points={WIDE} className="hidden lg:block" />

        {/* The hub. */}
        <Link
          href="/knowledge"
          data-testid="home-hub-centre"
          className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-10 flex flex-col items-center justify-center
                     w-24 h-24 sm:w-32 sm:h-32 lg:w-36 lg:h-36 rounded-full bg-white border-2 border-amber-300
                     shadow-[0_0_0_10px_rgba(251,191,36,0.12),0_10px_40px_-8px_rgba(245,158,11,0.45)] vw-hub-pulse
                     hover:border-amber-500 transition-colors"
        >
          <span className="w-9 h-9 sm:w-11 sm:h-11 rounded-xl bg-gradient-to-br from-amber-500 to-yellow-400 flex items-center justify-center shadow-md shadow-amber-500/30">
            <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 3L4 7.5V16.5L12 21L20 16.5V7.5L12 3Z" stroke="#fff" strokeWidth="2" strokeLinejoin="round"/><path d="M4 7.5L12 12M12 12L20 7.5M12 12V21" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>
          </span>
          <span className="mt-1.5 font-display font-extrabold text-[13px] sm:text-base tracking-tight text-ink">
            Value<span className="text-amber-500">Weave</span>
          </span>
        </Link>

        {NODES.map((n, i) => {
          const Icon = n.icon;
          const label = t(`hub.${n.key}`, n.label);
          return (
            <Link
              key={n.key}
              href={n.href}
              data-testid={`home-hub-${n.key}`}
              style={{ "--nx": `${NARROW[i].x}%`, "--ny": `${NARROW[i].y}%`, "--wx": `${WIDE[i].x}%`, "--wy": `${WIDE[i].y}%` }}
              className="group absolute z-10 -translate-x-1/2 -translate-y-1/2
                         left-[var(--nx)] top-[var(--ny)] lg:left-[var(--wx)] lg:top-[var(--wy)]
                         flex flex-col items-center text-center w-[5.5rem] sm:w-28 lg:w-44 min-h-[44px]
                         rounded-2xl px-1.5 py-2 lg:px-3 lg:py-2.5 bg-white/90 backdrop-blur-sm border border-amber-100
                         shadow-sm hover:border-amber-400 hover:shadow-md hover:-translate-y-[calc(50%+2px)] transition-all
                         focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-500"
            >
              <span className="w-8 h-8 lg:w-9 lg:h-9 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center group-hover:bg-amber-100 transition-colors">
                <Icon size={17} aria-hidden="true" />
              </span>
              <span className="mt-1 font-display font-bold text-[11px] sm:text-xs lg:text-sm leading-tight text-ink">{label}</span>
              <span className="hidden lg:block mt-0.5 text-[11px] leading-snug text-muted">{t(`hub.${n.key}_desc`, n.desc)}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
