/**
 * Sidebar — persistent left-hand navigation.
 *
 * Uses React Router's NavLink so the active route gets automatic
 * styling via the `active` class, without manual path comparison.
 */

import React from "react";
import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: "📊" },
  { to: "/log-interaction", label: "Log Interaction", icon: "📝" },
];

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <div className="sidebar__logo">AI</div>
        <div>
          <div className="sidebar__title">CRM Suite</div>
          <div className="sidebar__subtitle">HCP Module</div>
        </div>
      </div>

      <nav className="sidebar__nav">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `sidebar__link${isActive ? " sidebar__link--active" : ""}`
            }
          >
            <span className="sidebar__icon">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar__footer">
        <div className="sidebar__rep-badge">
          <div className="sidebar__avatar">R</div>
          <div>
            <div className="sidebar__rep-name">Field Rep</div>
            <div className="sidebar__rep-region">North Region</div>
          </div>
        </div>
      </div>

      <style>{`
        .sidebar {
          position: fixed;
          top: 0;
          left: 0;
          bottom: 0;
          width: var(--sidebar-width);
          background: var(--color-surface);
          border-right: 1px solid var(--color-border);
          display: flex;
          flex-direction: column;
          padding: var(--space-lg) var(--space-md);
        }

        .sidebar__brand {
          display: flex;
          align-items: center;
          gap: var(--space-sm);
          padding: 0 var(--space-sm) var(--space-lg);
          margin-bottom: var(--space-md);
          border-bottom: 1px solid var(--color-border);
        }

        .sidebar__logo {
          width: 36px;
          height: 36px;
          border-radius: var(--radius-sm);
          background: var(--color-primary);
          color: #fff;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 14px;
        }

        .sidebar__title {
          font-weight: 700;
          font-size: 15px;
          color: var(--color-text-primary);
        }

        .sidebar__subtitle {
          font-size: 11px;
          color: var(--color-text-secondary);
        }

        .sidebar__nav {
          display: flex;
          flex-direction: column;
          gap: 4px;
          flex: 1;
        }

        .sidebar__link {
          display: flex;
          align-items: center;
          gap: var(--space-sm);
          padding: 10px 12px;
          border-radius: var(--radius-sm);
          color: var(--color-text-secondary);
          font-weight: 500;
          font-size: 14px;
          transition: background-color 0.15s ease, color 0.15s ease;
        }

        .sidebar__link:hover {
          background: var(--color-bg);
          color: var(--color-text-primary);
        }

        .sidebar__link--active {
          background: var(--color-primary-light);
          color: var(--color-primary);
        }

        .sidebar__icon {
          font-size: 16px;
        }

        .sidebar__footer {
          padding-top: var(--space-md);
          border-top: 1px solid var(--color-border);
        }

        .sidebar__rep-badge {
          display: flex;
          align-items: center;
          gap: var(--space-sm);
          padding: var(--space-sm);
          border-radius: var(--radius-sm);
        }

        .sidebar__avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: var(--color-primary-light);
          color: var(--color-primary);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 13px;
        }

        .sidebar__rep-name {
          font-size: 13px;
          font-weight: 600;
          color: var(--color-text-primary);
        }

        .sidebar__rep-region {
          font-size: 11px;
          color: var(--color-text-secondary);
        }
      `}</style>
    </aside>
  );
}

export default Sidebar;