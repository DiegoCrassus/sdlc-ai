import { NavLink, Outlet } from "react-router-dom";
import styles from "./Layout.module.css";

const navItems = [
  { to: "/", label: "Discover", end: true },
  { to: "/watchlist", label: "Watchlist" },
  { to: "/portfolio", label: "Portfolio" },
];

export function Layout() {
  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <div className={styles.brand}>
          <span className={styles.logo}>◈</span>
          <div>
            <h1 className={styles.title}>Investment Radar</h1>
            <p className={styles.subtitle}>Local demo · no auth</p>
          </div>
        </div>
        <nav className={styles.nav} aria-label="Main">
          {navItems.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                isActive ? `${styles.link} ${styles.active}` : styles.link
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  );
}
