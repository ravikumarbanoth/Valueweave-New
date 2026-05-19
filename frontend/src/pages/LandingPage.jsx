import { useEffect } from "react";
import { Link } from "react-router-dom";

// Adapted from user's existing landing page code. CTAs now route to /get-started.

const GlobalStyles = () => (
  <style>{`
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');
    .vw-landing *, .vw-landing *::before, .vw-landing *::after { box-sizing: border-box; }
    .vw-landing { --amber:#F97316;--amber-lt:#FED7AA;--amber-dk:#C2410C;--teal:#0D9488;--teal-lt:#CCFBF1;--teal-dk:#0F766E;--cream:#FFFBF5;--ink:#1C1917;--muted:#78716C;--border:#E7E5E4; font-family:'DM Sans',sans-serif; background:var(--cream); color:var(--ink); overflow-x:hidden; }
    .vw-landing h1,.vw-landing h2,.vw-landing h3,.vw-landing h4 { font-family:'Syne',sans-serif; }
    @keyframes fadeUp { from{opacity:0;transform:translateY(28px);} to{opacity:1;transform:translateY(0);} }
    @keyframes floatA { 0%,100%{transform:translateY(0) rotate(0);} 50%{transform:translateY(-14px) rotate(3deg);} }
    @keyframes floatB { 0%,100%{transform:translateY(0) rotate(0);} 50%{transform:translateY(-20px) rotate(-4deg);} }
    @keyframes floatC { 0%,100%{transform:translateY(0);} 50%{transform:translateY(-10px);} }
    @keyframes pulseRing { 0%{transform:scale(0.9);opacity:0.6;} 70%{transform:scale(1.3);opacity:0;} 100%{transform:scale(0.9);opacity:0;} }
    @keyframes spinSlow { from{transform:rotate(0);} to{transform:rotate(360deg);} }
    @keyframes marquee { from{transform:translateX(0);} to{transform:translateX(-50%);} }
    @keyframes blobMorph { 0%,100%{border-radius:60% 40% 30% 70%/60% 30% 70% 40%;} 50%{border-radius:30% 60% 70% 40%/50% 60% 30% 60%;} }
    .vw-landing .animate-fadeUp { animation: fadeUp 0.7s ease both; }
    .vw-landing .animate-floatA { animation: floatA 5s ease-in-out infinite; }
    .vw-landing .animate-floatB { animation: floatB 6.5s ease-in-out infinite; }
    .vw-landing .animate-floatC { animation: floatC 4s ease-in-out infinite; }
    .vw-landing .animate-spinSlow { animation: spinSlow 18s linear infinite; }
    .vw-landing .animate-blob { animation: blobMorph 8s ease-in-out infinite; }
    .vw-landing .animate-marquee { animation: marquee 28s linear infinite; }
    .vw-landing .delay-100{animation-delay:.1s} .vw-landing .delay-200{animation-delay:.2s} .vw-landing .delay-300{animation-delay:.3s} .vw-landing .delay-400{animation-delay:.4s}
    .vw-landing .reveal { opacity:0; transform:translateY(24px); transition: opacity .65s ease, transform .65s ease; }
    .vw-landing .reveal.visible { opacity:1; transform:translateY(0); }
    .vw-landing .btn-primary { display:inline-flex;align-items:center;gap:8px;background:var(--amber);color:#fff;padding:14px 28px;border-radius:50px;font-family:'Syne',sans-serif;font-weight:700;font-size:15px;border:none;cursor:pointer;box-shadow:0 4px 20px rgba(249,115,22,.35);transition:all .2s;text-decoration:none; }
    .vw-landing .btn-primary:hover { background:var(--amber-dk);transform:translateY(-2px);box-shadow:0 8px 28px rgba(249,115,22,.45); }
    .vw-landing .btn-secondary { display:inline-flex;align-items:center;gap:8px;background:transparent;color:var(--ink);padding:13px 28px;border-radius:50px;font-family:'Syne',sans-serif;font-weight:600;font-size:15px;border:2px solid var(--border);cursor:pointer;transition:all .2s;text-decoration:none; }
    .vw-landing .btn-secondary:hover { border-color:var(--amber);background:var(--amber-lt);transform:translateY(-2px); }
    .vw-landing .hero-mesh { background: radial-gradient(ellipse 60% 60% at 80% 20%, rgba(249,115,22,.13) 0%, transparent 60%), radial-gradient(ellipse 50% 50% at 10% 80%, rgba(13,148,136,.12) 0%, transparent 55%), var(--cream); }
    .vw-landing .bg-warm { background:#FFF8F0; }
    .vw-landing .card { background:#fff;border:1px solid var(--border);border-radius:20px;padding:28px;transition:all .25s; }
    .vw-landing .card:hover { transform:translateY(-5px);box-shadow:0 16px 48px rgba(0,0,0,.08); }
    .vw-landing .navbar { position:fixed;top:0;left:0;right:0;z-index:100;transition:all .3s; padding:0 24px; }
    .vw-landing .navbar.scrolled { background:rgba(255,251,245,.92);backdrop-filter:blur(16px);box-shadow:0 1px 24px rgba(0,0,0,.07); }
    @media (max-width:768px) { .vw-landing .hide-mobile { display:none !important; } }
  `}</style>
);

function useReveal() {
  useEffect(() => {
    const els = document.querySelectorAll(".vw-landing .reveal");
    const obs = new IntersectionObserver(
      (entries) => entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add("visible"); }),
      { threshold: 0.12 }
    );
    els.forEach((el) => obs.observe(el));
    return () => obs.disconnect();
  }, []);
}

function Navbar() {
  const [scrolled, setScrolled] = useStateScroll();
  return (
    <nav className={`navbar ${scrolled ? "scrolled" : ""}`}>
      <div style={{ maxWidth: 1180, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between", height: 68 }}>
        <Link to="/" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
          <div style={{ width: 38, height: 38, borderRadius: 12, background: "linear-gradient(135deg,#F97316,#FBBF24)", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 4px 12px rgba(249,115,22,0.35)" }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M12 3L4 7.5V16.5L12 21L20 16.5V7.5L12 3Z" stroke="#fff" strokeWidth="2" strokeLinejoin="round"/><path d="M4 7.5L12 12M12 12L20 7.5M12 12V21" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>
          </div>
          <span style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: 20, color: "#1C1917", letterSpacing: "-0.5px" }}>
            Value<span style={{ color: "#F97316" }}>Weave</span>
          </span>
        </Link>
        <Link to="/get-started" data-testid="nav-get-started" className="btn-primary" style={{ padding: "10px 22px", fontSize: 14 }}>
          Join Early Access →
        </Link>
      </div>
    </nav>
  );
}

function useStateScroll() {
  const [s, setS] = useState(false);
  useEffect(() => {
    const h = () => setS(window.scrollY > 30);
    window.addEventListener("scroll", h);
    return () => window.removeEventListener("scroll", h);
  }, []);
  return [s, setS];
}
import { useState } from "react";

function Hero() {
  return (
    <section className="hero-mesh" style={{ paddingTop: 120, paddingBottom: 80, overflow: "hidden", padding: "120px 24px 80px" }}>
      <div style={{ maxWidth: 1180, margin: "0 auto", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 60, alignItems: "center" }} className="hero-grid">
        <style>{`@media(max-width:768px){.hero-grid{grid-template-columns:1fr !important;}}`}</style>
        <div>
          <div className="animate-fadeUp" style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "#FED7AA", borderRadius: 50, padding: "7px 16px", marginBottom: 24 }}>
            <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#F97316", boxShadow: "0 0 0 3px rgba(249,115,22,0.3)" }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#C2410C" }}>Now Open for Early Access · Bharat Edition</span>
          </div>
          <h1 className="animate-fadeUp delay-100" style={{ fontSize: "clamp(36px,5.5vw,62px)", fontWeight: 800, lineHeight: 1.08, letterSpacing: "-1.5px", color: "#1C1917", marginBottom: 24 }}>
            Where Ambition<br />
            <span style={{ background: "linear-gradient(135deg,#F97316 0%,#FBBF24 50%,#0D9488 100%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>
              Finds Its Team.
            </span>
          </h1>
          <p className="animate-fadeUp delay-200" style={{ fontSize: "clamp(16px,1.8vw,19px)", color: "#78716C", lineHeight: 1.75, maxWidth: 480, marginBottom: 36 }}>
            ValueWeave connects India's youth, students, and skilled builders to discover collaborators, form startup teams, and create real economic opportunities — from tier-2 towns to global ambitions.
          </p>
          <div className="animate-fadeUp delay-300" style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <Link to="/get-started" data-testid="hero-cta-primary" className="btn-primary">Start Building ⚡</Link>
            <a href="#how-it-works" className="btn-secondary">How It Works →</a>
          </div>
          <div className="animate-fadeUp delay-400" style={{ display: "flex", alignItems: "center", gap: 16, marginTop: 40 }}>
            <div style={{ display: "flex" }}>
              {["🧑‍💻","👩‍🔬","🧑‍🌾","👩‍🔧","🧑‍🎨"].map((e, i) => (
                <div key={i} style={{ width: 36, height: 36, borderRadius: "50%", background: `hsl(${i * 35 + 20},80%,88%)`, border: "2px solid #fff", marginLeft: i === 0 ? 0 : -10, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16 }}>{e}</div>
              ))}
            </div>
            <div>
              <div style={{ fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 14, color: "#1C1917" }}>2,400+ builders joined</div>
              <div style={{ fontSize: 12, color: "#78716C" }}>across 28 states · growing daily</div>
            </div>
          </div>
        </div>
        <div style={{ position: "relative", display: "flex", justifyContent: "center", alignItems: "center", minHeight: 440 }}>
          <div className="animate-blob" style={{ position: "absolute", width: 380, height: 380, background: "linear-gradient(135deg,rgba(249,115,22,0.12),rgba(13,148,136,0.12))", borderRadius: "60% 40% 30% 70%/60% 30% 70% 40%", zIndex: 0 }} />
          <div style={{ position: "relative", zIndex: 1 }}>
            <div style={{ width: 100, height: 100, borderRadius: "50%", background: "linear-gradient(135deg,#F97316,#FBBF24)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto", boxShadow: "0 8px 32px rgba(249,115,22,0.4)", position: "relative", zIndex: 2 }}>
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none"><path d="M12 3L4 7.5V16.5L12 21L20 16.5V7.5L12 3Z" stroke="#fff" strokeWidth="1.8" strokeLinejoin="round"/><path d="M4 7.5L12 12M12 12L20 7.5M12 12V21" stroke="#fff" strokeWidth="1.8" strokeLinecap="round"/></svg>
              {[1,2].map(i => (
                <div key={i} style={{ position: "absolute", inset: -8 * i, borderRadius: "50%", border: `2px solid rgba(249,115,22,${0.25 - i * 0.08})`, animation: `pulseRing ${1.4 + i * 0.5}s ease-out infinite`, animationDelay: `${i * 0.4}s` }} />
              ))}
            </div>
            {[
              { top: -110, left: -20, emoji: "🧑‍💻", label: "Dev · Pune", color: "#EFF6FF", border: "#BFDBFE" },
              { top: -80, right: -140, emoji: "👩‍🔬", label: "AI Builder · Bhopal", color: "#F0FDF4", border: "#BBF7D0" },
              { bottom: -90, left: -140, emoji: "🧑‍🌾", label: "Agri-tech · Nagpur", color: "#FFF7ED", border: "#FED7AA" },
              { bottom: -60, right: -30, emoji: "🔧", label: "EV Tech · Nashik", color: "#F5F3FF", border: "#DDD6FE" },
            ].map((c, i) => (
              <div key={i} className={`animate-float${["A","B","C","A"][i]}`} style={{ position: "absolute", ...c, background: c.color, border: `1.5px solid ${c.border}`, borderRadius: 14, padding: "10px 14px", display: "flex", alignItems: "center", gap: 8, boxShadow: "0 4px 16px rgba(0,0,0,0.08)", whiteSpace: "nowrap" }}>
                <span style={{ fontSize: 22 }}>{c.emoji}</span>
                <span style={{ fontSize: 12, fontWeight: 600, color: "#1C1917" }}>{c.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function HowItWorks() {
  const steps = [
    { num: "01", icon: "👤", title: "Create Your Profile", desc: "Tell us your skills, interests, and what you want to build. Everyone has a place here." },
    { num: "02", icon: "🔍", title: "Discover Opportunities", desc: "Browse local businesses, startup ideas, tech projects, and community initiatives." },
    { num: "03", icon: "🤝", title: "Connect with Collaborators", desc: "Send collaboration requests, chat directly, and explore what you can build together." },
    { num: "04", icon: "🚀", title: "Build Together", desc: "Form your team, define your project, and launch — right from your hometown." },
  ];
  return (
    <section id="how-it-works" className="bg-warm" style={{ padding: "96px 24px" }}>
      <div style={{ maxWidth: 1180, margin: "0 auto" }}>
        <div className="reveal" style={{ textAlign: "center", marginBottom: 64 }}>
          <span style={{ display: "inline-block", background: "#CCFBF1", color: "#0F766E", borderRadius: 50, padding: "6px 18px", fontSize: 13, fontWeight: 700, marginBottom: 16, letterSpacing: "0.5px" }}>HOW IT WORKS</span>
          <h2 style={{ fontSize: "clamp(28px,4vw,46px)", fontWeight: 800, letterSpacing: "-1px", lineHeight: 1.1, color: "#1C1917" }}>
            From "I have an idea" to<br /><span style={{ color: "#0D9488" }}>"We built it."</span>
          </h2>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(240px,1fr))", gap: 24 }}>
          {steps.map((s, i) => (
            <div key={i} className="card reveal">
              <div style={{ fontSize: 40, marginBottom: 16 }}>{s.icon}</div>
              <div style={{ width: 40, height: 40, background: "linear-gradient(135deg,#F97316,#FBBF24)", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'Syne',sans-serif", fontWeight: 800, color: "#fff", marginBottom: 16, fontSize: 14 }}>{s.num}</div>
              <h3 style={{ fontWeight: 700, fontSize: 18, marginBottom: 10, color: "#1C1917" }}>{s.title}</h3>
              <p style={{ fontSize: 14, color: "#78716C", lineHeight: 1.7 }}>{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function FinalCTA() {
  return (
    <section style={{ padding: "96px 24px", background: "#1C1917", color: "#fff", textAlign: "center" }}>
      <div style={{ maxWidth: 720, margin: "0 auto" }}>
        <h2 style={{ fontSize: "clamp(28px,4vw,48px)", fontWeight: 800, letterSpacing: "-1px", lineHeight: 1.1, marginBottom: 18 }}>
          Be part of the&nbsp;
          <span style={{ background: "linear-gradient(135deg,#F97316,#FBBF24,#0D9488)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>first wave</span>.
        </h2>
        <p style={{ fontSize: 16, color: "rgba(255,255,255,0.6)", marginBottom: 32, lineHeight: 1.7 }}>
          Join 2,400+ early builders shaping India's next collaboration platform.
        </p>
        <Link to="/get-started" data-testid="footer-cta" className="btn-primary" style={{ fontSize: 15 }}>Get Early Access ✨</Link>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer style={{ background: "#141210", color: "rgba(255,255,255,0.5)", padding: "32px 24px", textAlign: "center", fontSize: 13 }}>
      © 2025 ValueWeave Technologies · Made with ❤️ for Bharat
    </footer>
  );
}

export default function LandingPage() {
  useReveal();
  return (
    <div className="vw-landing">
      <GlobalStyles />
      <Navbar />
      <main>
        <Hero />
        <HowItWorks />
        <FinalCTA />
      </main>
      <Footer />
    </div>
  );
}
