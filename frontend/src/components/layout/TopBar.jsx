/**
 * TopBar — persistent header above the routed page content.
 *
 * Derives a page title from the current route so it doesn't need to
 * be passed down manually from every page, and offers a quick-action
 * button to jump straight into logging an interaction.
 */

import React from "react";
import { useLocation, useNavigate } from "react-router-dom";

const TITLES = {
  "/dashboard": "Dashboard",
  "/log-interaction": "Log Interaction",
};

function TopBar() {
  const location = useLocation();
  const navigate = useNavigate();

  const title = TITLES[location.pathname] || "AI-First CRM";

  return (
    <header className="topbar">
      <h1 className="topbar__title">{title}</h1>

      <div className="topbar__actions">
        {location.pathname !== "/log-interaction" && (
          <button
            className="topbar__cta"
            onClick={() => navigate("/log-interaction")}
          >
            + Log Interaction
          </button>
        )}
      </div>

      <style>{`
        .topbar {
          height: var(--topbar-height);
          background: var(--color-surface);
          border-bottom: 1px solid var(--color-border);
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 var(--space-xl);
          position: sticky;
          top: 0;
          z-index: 10;
        }

        .topbar__title {
          font-size: 18px;
          font-weight: 700;
          color: var(--color-text-primary);
        }

        .topbar__actions {
          display: flex;
          align-items: center;
          gap: var(--space-sm);
        }

        .topbar__cta {
          background: var(--color-primary);
          color: #fff;
          border: none;
          padding: 8px 16px;
          border-radius: var(--radius-sm);
          font-weight: 600;
          font-size: 13px;
          transition: background-color 0.15s ease;
        }

        .topbar__cta:hover {
          background: var(--color-primary-hover);
        }
      `}</style>
    </header>
  );
}

export default TopBar;