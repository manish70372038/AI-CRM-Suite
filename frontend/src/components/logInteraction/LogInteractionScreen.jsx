/**
 * LogInteractionScreen — the core screen required by the assignment.
 *
 * Displays Form Mode and Chat Mode side-by-side in a two-column split
 * layout (rather than a tab toggle), so the rep can see and use both
 * input methods at once. Both panels write into the same underlying
 * `draft` state in interactionSlice, so entities extracted via chat
 * appear live in the form on the left.
 */

import React from "react";

import FormMode from "./FormMode";
import ChatMode from "./ChatMode";

function LogInteractionScreen() {
  return (
    <div className="log-screen">
      <div className="log-screen__panel log-screen__panel--form card">
        <div className="log-screen__panel-header">
          <span className="log-screen__panel-icon">📋</span>
          <h2 className="log-screen__panel-title">Form Mode</h2>
        </div>
        <div className="log-screen__panel-body">
          <FormMode />
        </div>
      </div>

      <div className="log-screen__panel log-screen__panel--chat card">
        <div className="log-screen__panel-header">
          <span className="log-screen__panel-icon">💬</span>
          <h2 className="log-screen__panel-title">Chat Mode</h2>
        </div>
        <div className="log-screen__panel-body log-screen__panel-body--chat">
          <ChatMode />
        </div>
      </div>

      <style>{`
        .log-screen {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: var(--space-lg);
          align-items: start;
        }

        .log-screen__panel {
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        .log-screen__panel-header {
          display: flex;
          align-items: center;
          gap: var(--space-sm);
          padding: var(--space-md) var(--space-lg);
          border-bottom: 1px solid var(--color-border);
          background: var(--color-bg);
        }

        .log-screen__panel-icon {
          font-size: 16px;
        }

        .log-screen__panel-title {
          font-size: 14px;
          font-weight: 700;
          color: var(--color-text-primary);
        }

        .log-screen__panel-body {
          padding: var(--space-lg);
        }

        .log-screen__panel-body--chat {
          padding: 0;
        }

        .log-screen__panel--chat .chat-mode {
          border: none;
          border-radius: 0;
          height: 640px;
        }

        @media (max-width: 960px) {
          .log-screen {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
}

export default LogInteractionScreen;