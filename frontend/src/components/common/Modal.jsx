/**
 * Reusable Modal primitive.
 *
 * Used for the interaction detail/edit dialog opened from the
 * Dashboard's InteractionTable. Closes on overlay click or Escape key.
 */

import React, { useEffect } from "react";

function Modal({ isOpen, onClose, title, children, footer }) {
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal__header">
          <h2 className="modal__title">{title}</h2>
          <button className="modal__close" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>

        <div className="modal__body">{children}</div>

        {footer && <div className="modal__footer">{footer}</div>}
      </div>

      <style>{`
        .modal-overlay {
          position: fixed;
          inset: 0;
          background: rgba(15, 23, 42, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 100;
          padding: var(--space-lg);
        }

        .modal {
          background: var(--color-surface);
          border-radius: var(--radius-lg);
          box-shadow: var(--shadow-lg);
          width: 100%;
          max-width: 560px;
          max-height: 85vh;
          display: flex;
          flex-direction: column;
        }

        .modal__header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: var(--space-lg);
          border-bottom: 1px solid var(--color-border);
        }

        .modal__title {
          font-size: 17px;
          font-weight: 700;
          color: var(--color-text-primary);
        }

        .modal__close {
          background: transparent;
          border: none;
          font-size: 16px;
          color: var(--color-text-secondary);
          width: 28px;
          height: 28px;
          border-radius: var(--radius-sm);
        }

        .modal__close:hover {
          background: var(--color-bg);
        }

        .modal__body {
          padding: var(--space-lg);
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: var(--space-md);
        }

        .modal__footer {
          padding: var(--space-md) var(--space-lg);
          border-top: 1px solid var(--color-border);
          display: flex;
          justify-content: flex-end;
          gap: var(--space-sm);
        }
      `}</style>
    </div>
  );
}

export default Modal;