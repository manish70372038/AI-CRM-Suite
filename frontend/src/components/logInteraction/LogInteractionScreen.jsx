/**
 * LogInteractionScreen — the core screen required by the assignment.
 *
 * Offers a tab toggle between Form Mode and Chat Mode. Both write
 * into the same underlying `draft` state in interactionSlice, so
 * switching tabs never loses in-progress data — the whole point of
 * offering "flexibility" between structured and conversational input.
 */

import React, { useState } from "react";

import FormMode from "./FormMode";
import ChatMode from "./ChatMode";

const TABS = [
  { id: "form", label: "📋 Form" },
  { id: "chat", label: "💬 Chat" },
];

function LogInteractionScreen() {
  const [activeTab, setActiveTab] = useState("form");

  return (
    <div className="log-screen card">
      <div className="log-screen__tabs">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={`log-screen__tab${activeTab === tab.id ? " log-screen__tab--active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
            type="button"
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="log-screen__body">
        {activeTab === "form" ? <FormMode /> : <ChatMode />}
      </div>

      <style>{`
        .log-screen {
          padding: var(--space-lg);
        }

        .log-screen__tabs {
          display: flex;
          gap: 4px;
          background: var(--color-bg);
          padding: 4px;
          border-radius: var(--radius-sm);
          width: fit-content;
          margin-bottom: var(--space-lg);
        }

        .log-screen__tab {
          background: transparent;
          border: none;
          padding: 8px 20px;
          border-radius: 6px;
          font-weight: 600;
          font-size: 13px;
          color: var(--color-text-secondary);
          transition: background-color 0.15s ease, color 0.15s ease;
        }

        .log-screen__tab--active {
          background: var(--color-surface);
          color: var(--color-primary);
          box-shadow: var(--shadow-sm);
        }
      `}</style>
    </div>
  );
}

export default LogInteractionScreen;