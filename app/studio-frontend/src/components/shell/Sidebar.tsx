import { NavLink } from "react-router-dom";

export type NavItem = {
  to: string;
  label: string;
  end?: boolean;
};

export const PRIMARY_NAV: NavItem[] = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/workflows", label: "Workflows" },
  { to: "/builder", label: "Workflow Builder" },
  { to: "/agents", label: "Agents & Subagents" },
  { to: "/rules", label: "Rules & Skills" },
  { to: "/commands", label: "Commands" },
  { to: "/registry", label: "Registry" },
  { to: "/validation", label: "Validation" },
  { to: "/simulation", label: "Simulation" },
  { to: "/assistance", label: "Assistance" },
  { to: "/observability", label: "Observability" },
  { to: "/evidence", label: "Evidence & Delivery" },
  { to: "/settings", label: "Settings" },
];

const linkClass = ({ isActive }: { isActive: boolean }) =>
  [
    "block rounded-lg px-3 py-2 text-sm font-medium transition-colors",
    isActive
      ? "bg-studio-accent/15 text-studio-accent ring-1 ring-studio-accent/30"
      : "text-slate-400 hover:bg-slate-800 hover:text-white",
  ].join(" ");

type SidebarProps = {
  open: boolean;
  onClose: () => void;
};

export function Sidebar({ open, onClose }: SidebarProps) {
  return (
    <>
      {open ? (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          aria-label="Close navigation"
          onClick={onClose}
        />
      ) : null}
      <aside
        className={[
          "fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-slate-800 bg-slate-950 transition-transform lg:static lg:z-0 lg:translate-x-0",
          open ? "translate-x-0 top-14" : "-translate-x-full top-14 lg:top-0 lg:translate-x-0",
        ].join(" ")}
      >
        <nav className="flex-1 overflow-y-auto p-4" aria-label="Studio navigation">
          <ul className="space-y-1">
            {PRIMARY_NAV.map((item) => (
              <li key={item.to}>
                <NavLink to={item.to} end={item.end} className={linkClass} onClick={onClose}>
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
      </aside>
    </>
  );
}
