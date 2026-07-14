/**
 * Reusable Button primitive.
 *
 * Supports `variant` (primary | secondary | ghost | danger) and
 * `size` (sm | md) so every button in the app shares one consistent
 * implementation instead of ad-hoc styled buttons per component.
 */

import React from "react";

function Button({
  children,
  variant = "primary",
  size = "md",
  onClick,
  type = "button",
  disabled = false,
  fullWidth = false,
  ...rest
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`btn btn--${variant} btn--${size}${fullWidth ? " btn--full" : ""}`}
      {...rest}
    >
      {children}

      <style>{`
        .btn {
          border: none;
          border-radius: var(--radius-sm);
          font-weight: 600;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          transition: background-color 0.15s ease, opacity 0.15s ease, border-color 0.15s ease;
          white-space: nowrap;
        }

        .btn:disabled {
          opacity: 0.55;
          cursor: not-allowed;
        }

        .btn--full {
          width: 100%;
        }

        /* Sizes */
        .btn--sm {
          padding: 6px 12px;
          font-size: 12px;
        }

        .btn--md {
          padding: 10px 18px;
          font-size: 14px;
        }

        /* Variants */
        .btn--primary {
          background: var(--color-primary);
          color: #fff;
        }
        .btn--primary:hover:not(:disabled) {
          background: var(--color-primary-hover);
        }

        .btn--secondary {
          background: var(--color-surface);
          color: var(--color-text-primary);
          border: 1px solid var(--color-border);
        }
        .btn--secondary:hover:not(:disabled) {
          background: var(--color-bg);
        }

        .btn--ghost {
          background: transparent;
          color: var(--color-text-secondary);
        }
        .btn--ghost:hover:not(:disabled) {
          background: var(--color-bg);
          color: var(--color-text-primary);
        }

        .btn--danger {
          background: var(--color-danger);
          color: #fff;
        }
        .btn--danger:hover:not(:disabled) {
          opacity: 0.9;
        }
      `}</style>
    </button>
  );
}

export default Button;