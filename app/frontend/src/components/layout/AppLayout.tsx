import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

import { IdentifyModal } from "../auth/IdentifyModal";
import { useAuth } from "../../context/AuthContext";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  [
    "rounded-lg px-4 py-2 text-sm font-medium transition-colors",
    isActive
      ? "bg-emerald-500/20 text-emerald-400 ring-1 ring-emerald-500/40"
      : "text-slate-400 hover:bg-slate-800 hover:text-white",
  ].join(" ");

export function AppLayout() {
  const { user, isLoading, isAuthenticated, identify, logout } = useAuth();
  const [identifyOpen, setIdentifyOpen] = useState(false);

  return (
    <div className="min-h-screen bg-surface">
      <header className="border-b border-slate-800 bg-slate-950/80 px-6 py-5 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-emerald-400">Live mock feed</p>
            <h1 className="text-3xl font-bold text-white">MarketPulse</h1>
            <p className="mt-1 text-sm text-slate-400">
              Financial & crypto dashboard · refreshes every 30s
            </p>
          </div>
          <div className="flex flex-col items-start gap-3 sm:items-end">
            <div className="flex items-center gap-3">
              {isLoading ? (
                <span className="text-sm text-slate-500">Checking session…</span>
              ) : isAuthenticated && user ? (
                <>
                  <span className="text-sm text-slate-300" data-testid="header-user-email">
                    {user.email}
                  </span>
                  <button
                    type="button"
                    onClick={() => void logout()}
                    className="rounded-lg border border-slate-700 px-3 py-1.5 text-sm font-medium text-slate-300 hover:bg-slate-800"
                  >
                    Log out
                  </button>
                </>
              ) : (
                <button
                  type="button"
                  onClick={() => setIdentifyOpen(true)}
                  className="rounded-lg bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-500"
                >
                  Sign in
                </button>
              )}
            </div>
            <nav className="flex gap-2" aria-label="Main navigation">
              <NavLink to="/" end className={navLinkClass}>
                Dashboard
              </NavLink>
              <NavLink to="/forecast" className={navLinkClass}>
                Forecast
              </NavLink>
              <NavLink to="/compare" className={navLinkClass}>
                Compare
              </NavLink>
              <NavLink to="/portfolio" className={navLinkClass}>
                Portfólio
              </NavLink>
            </nav>
          </div>
        </div>
      </header>
      <IdentifyModal
        open={identifyOpen}
        onClose={() => setIdentifyOpen(false)}
        onSubmit={identify}
      />
      <Outlet />
    </div>
  );
}
