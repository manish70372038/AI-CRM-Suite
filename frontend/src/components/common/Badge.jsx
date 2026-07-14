/**
 * Reusable Badge primitive.
 *
 * Renders a small colored label. `tone` maps to a semantic color set
 * so callers describe intent ("success", "warning", "neutral"...)
 * rather than picking colors directly — keeps sentiment/status
 * indicators consistent across the Dashboard, Chat, and Form views.
 */

import React from "react";

const TONE_STYLES = {
  neutral: { bg: "var(--color-bg)", color: "var(--color-text-secondary)" },
  primary: { bg: "var(--color-primary-light)", color: "var(--color-primary)" },
  success: { bg: "var(--color-success-light)", color: "var(--color-success)" },
  warning: { bg: "var(--color-warning-light)", color: "var(--color-warning)" },
  danger: { bg: "var(--color-danger-light)", color: "var(--color-danger)" },
};

function Badge({ children, tone = "neutral" }) {
  const style = TONE_STYLES[tone] || TONE_STYLES.neutral;

  return (
    <span
      className="badge"
      style={{ backgroundColor: style.bg, color: style.color }}
    >
      {children}

      <style>{`
        .badge {
          display: inline-flex;
          align-items: center;
          padding: 3px 10px;
          border-radius: 999px;
          font-size: 11px;
          font-weight: 600;
          text-transform: capitalize;
          line-height: 1.6;
        }
      `}</style>
    </span>
  );
}

export default Badge;