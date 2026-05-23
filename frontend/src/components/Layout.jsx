import React from "react";
import Navbar, { MobileBottomNav } from "@/components/Navbar";

export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Navbar />
      <main className="flex-1 pb-20 md:pb-0">{children}</main>
      <Footer />
      <MobileBottomNav />
    </div>
  );
}

function Footer() {
  return (
    <footer className="border-t border-border bg-card/40 mt-16">
      <div className="vw-container py-10 grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="h-7 w-7 rounded-lg bg-primary text-white inline-flex items-center justify-center font-extrabold">V</span>
            <span className="font-extrabold tracking-tight" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>ValueWeave</span>
          </div>
          <p className="text-muted-foreground max-w-sm">
            A Bharat-first ecosystem to discover, team up on, and build meaningful businesses — together.
          </p>
        </div>
        <div>
          <div className="vw-section-label mb-2">Explore</div>
          <ul className="space-y-1 text-foreground/80">
            <li><a href="/ideas" className="hover:text-primary">Idea Library</a></li>
            <li><a href="/opportunities" className="hover:text-primary">Opportunities</a></li>
            <li><a href="/dashboard" className="hover:text-primary">Dashboard</a></li>
          </ul>
        </div>
        <div>
          <div className="vw-section-label mb-2">Community</div>
          <p className="text-muted-foreground">Built across Telangana &amp; Andhra Pradesh, scaling to all of Bharat.</p>
        </div>
      </div>
      <div className="border-t border-border py-4 text-center text-xs text-muted-foreground">
        © {new Date().getFullYear()} ValueWeave · Made for builders of Bharat
      </div>
    </footer>
  );
}
