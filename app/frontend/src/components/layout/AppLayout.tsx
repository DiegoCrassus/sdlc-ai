import { NavLink, Outlet } from "react-router-dom";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  [
    "rounded-lg px-4 py-2 text-sm font-medium transition-colors",
    isActive
      ? "bg-emerald-500/20 text-emerald-400 ring-1 ring-emerald-500/40"
      : "text-slate-400 hover:bg-slate-800 hover:text-white",
  ].join(" ");

export function AppLayout() {
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
          <nav className="flex gap-2" aria-label="Main navigation">
            <NavLink to="/" end className={navLinkClass}>
              Dashboard
            </NavLink>
            <NavLink to="/forecast" className={navLinkClass}>
              Forecast
            </NavLink>
          </nav>
        </div>
      </header>
      <Outlet />
    </div>
  );
}
