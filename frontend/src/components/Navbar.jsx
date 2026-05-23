import React from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { Lightbulb, Home, LayoutDashboard, User2, Menu, X, LogOut } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

const navItems = [
  { to: "/", label: "Home", testid: "navbar-home-link" },
  { to: "/ideas", label: "Ideas", testid: "navbar-ideas-link", highlight: true },
  { to: "/opportunities", label: "Opportunities", testid: "navbar-opportunities-link" },
  { to: "/dashboard", label: "Dashboard", testid: "navbar-dashboard-link" },
];

export default function Navbar() {
  const { user, signOut, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = React.useState(false);

  React.useEffect(() => { setMobileOpen(false); }, [location.pathname]);

  return (
    <header className="vw-glass-nav sticky top-0 z-50" data-testid="vw-navbar">
      <div className="vw-container flex items-center justify-between h-16">
        <button
          onClick={() => navigate("/")}
          className="flex items-center gap-2 group"
          data-testid="navbar-logo"
        >
          <span className="relative inline-flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-[0_4px_14px_rgba(232,93,4,0.4)] group-hover:scale-105 transition-transform">
            <span className="font-extrabold text-base tracking-tight">V</span>
          </span>
          <span className="font-extrabold text-lg tracking-tight" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
            ValueWeave
          </span>
        </button>

        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              data-testid={item.testid}
              className={({ isActive }) =>
                `relative px-4 py-2 rounded-full text-sm font-semibold transition-colors ${
                  isActive
                    ? "text-primary bg-secondary"
                    : "text-foreground/80 hover:text-foreground hover:bg-muted"
                } ${item.highlight && !isActive ? "ring-1 ring-primary/20" : ""}`
              }
              end={item.to === "/"}
            >
              {item.label}
              {item.highlight && (
                <span className="ml-1.5 inline-block h-1.5 w-1.5 rounded-full bg-primary align-middle" />
              )}
            </NavLink>
          ))}
        </nav>

        <div className="hidden md:flex items-center gap-2">
          {loading ? null : user ? (
            <div className="flex items-center gap-2">
              <button
                onClick={() => navigate("/dashboard")}
                className="flex items-center gap-2 rounded-full pl-2 pr-3 py-1.5 hover:bg-muted transition-colors"
                data-testid="navbar-user-chip"
              >
                {user.picture ? (
                  <img src={user.picture} alt="" className="h-7 w-7 rounded-full" />
                ) : (
                  <span className="h-7 w-7 rounded-full bg-accent text-accent-foreground inline-flex items-center justify-center text-xs font-bold">
                    {user.name?.[0] || user.email?.[0] || "U"}
                  </span>
                )}
                <span className="text-sm font-semibold max-w-[110px] truncate">{user.name?.split(" ")[0] || "Account"}</span>
              </button>
              <button
                onClick={signOut}
                className="vw-btn-ghost px-3 py-2"
                data-testid="navbar-signout"
                title="Sign out"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={() => navigate("/login")}
              className="vw-btn-primary py-2.5 px-5 text-sm"
              data-testid="navbar-signin-btn"
            >
              Sign in
            </button>
          )}
        </div>

        <button
          className="md:hidden p-2 rounded-lg hover:bg-muted"
          onClick={() => setMobileOpen((v) => !v)}
          data-testid="navbar-mobile-toggle"
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {mobileOpen && (
        <div className="md:hidden border-t border-border bg-background/95 backdrop-blur-xl">
          <div className="vw-container py-3 flex flex-col gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                data-testid={`mobile-${item.testid}`}
                className={({ isActive }) =>
                  `px-4 py-3 rounded-xl text-base font-semibold ${
                    isActive ? "text-primary bg-secondary" : "hover:bg-muted"
                  }`
                }
                end={item.to === "/"}
              >
                {item.label}
              </NavLink>
            ))}
            {!user && !loading && (
              <button
                onClick={() => navigate("/login")}
                className="vw-btn-primary mt-2"
                data-testid="mobile-navbar-signin"
              >
                Sign in
              </button>
            )}
            {user && (
              <button onClick={signOut} className="vw-btn-outline mt-2" data-testid="mobile-navbar-signout">
                <LogOut className="h-4 w-4" /> Sign out
              </button>
            )}
          </div>
        </div>
      )}
    </header>
  );
}

export function MobileBottomNav() {
  const { user } = useAuth();
  const items = [
    { to: "/", label: "Home", icon: Home, testid: "mobile-nav-home" },
    { to: "/ideas", label: "Ideas", icon: Lightbulb, testid: "mobile-nav-ideas" },
    { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard, testid: "mobile-nav-dashboard" },
    { to: user ? "/dashboard" : "/login", label: user ? "Profile" : "Sign in", icon: User2, testid: "mobile-nav-profile" },
  ];
  return (
    <nav
      className="md:hidden fixed bottom-0 inset-x-0 z-40 backdrop-blur-2xl bg-background/90 border-t border-border"
      data-testid="mobile-bottom-nav"
    >
      <div className="grid grid-cols-4 max-w-md mx-auto">
        {items.map((it) => (
          <NavLink
            key={it.to + it.label}
            to={it.to}
            end={it.to === "/"}
            data-testid={it.testid}
            className={({ isActive }) =>
              `flex flex-col items-center gap-1 py-2.5 text-[11px] font-semibold transition-colors ${
                isActive ? "text-primary" : "text-muted-foreground"
              }`
            }
          >
            <it.icon className="h-5 w-5" />
            {it.label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
