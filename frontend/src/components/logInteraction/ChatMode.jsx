/**
 * ChatMode — conversational interaction logging, ChatGPT-style.
 *
 * Sends free-text messages to POST /chat, which the backend routes
 * through the LangGraph agent's intent router to one of the 5 tools.
 * Tool invocations are rendered as small indicator chips inline in
 * the conversation so the rep can see what the AI actually did
 * (e.g. "🔧 Logged Interaction #14").
 *
 * When the Log Interaction tool returns extracted entities, they are
 * merged into the shared interaction draft via
 * `setDraftFromExtraction` — INCLUDING the saved record's `id`. This
 * is what lets Form Mode know the record already exists in the DB,
 * so submitting the form later UPDATES it instead of creating a
 * duplicate interaction.
 */

import React, { useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import Button from "../common/Button";
import { sendChatMessage, appendUserMessage } from "../../store/chatSlice";
import { setDraftFromExtraction } from "../../store/interactionSlice";

const TOOL_LABELS = {
  log_interaction: "📝 Logged Interaction",
  edit_interaction: "✏️ Edited Interaction",
  search_interaction: "🔍 Searched Interactions",
  summarize_previous: "📋 Summarized Previous Visits",
  recommend_followup: "💡 Recommended Follow-up",
};

function ChatBubble({ message }) {
  if (message.role === "tool") {
    return (
      <div className="chat-tool-chip">
        {TOOL_LABELS[message.toolName] || `🔧 ${message.toolName}`}
        {message.content && <span className="chat-tool-chip__detail"> — {message.content}</span>}
      </div>
    );
  }

  return (
    <div className={`chat-bubble chat-bubble--${message.role}`}>
      <div className="chat-bubble__content">{message.content}</div>
    </div>
  );
}

function ChatMode() {
  const dispatch = useDispatch();
  const { messages, sessionId, status, lastToolResult } = useSelector((state) => state.chat);
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    // Log Interaction tool ALREADY saved this to the DB — pass its id
    // along so Form Mode updates the same record instead of creating
    // a second, duplicate interaction when the rep hits Save there.
    if (lastToolResult?.toolName === "log_interaction" && lastToolResult.data) {
      const { id, doctor_name, hospital, products_discussed, follow_up_date, summary, sentiment } =
        lastToolResult.data;
      dispatch(
        setDraftFromExtraction({
          id,
          doctor_name: doctor_name || "",
          hospital: hospital || "",
          products_discussed: products_discussed || [],
          follow_up_date: follow_up_date || "",
          raw_notes: summary || "",
          sentiment: sentiment || "",
        })
      );
    }

    // Edit Interaction tool also returns the (same) record's id —
    // keep the draft's activeInteractionId pointed at it too, so any
    // further form edits also update rather than duplicate.
    if (lastToolResult?.toolName === "edit_interaction" && lastToolResult.data?.id) {
      const { id, doctor_name, hospital, products_discussed, follow_up_date, summary, sentiment } =
        lastToolResult.data;
      dispatch(
        setDraftFromExtraction({
          id,
          doctor_name: doctor_name || "",
          hospital: hospital || "",
          products_discussed: products_discussed || [],
          follow_up_date: follow_up_date || "",
          raw_notes: summary || "",
          sentiment: sentiment || "",
        })
      );
    }
  }, [lastToolResult, dispatch]);

  const handleSend = async (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || status === "sending") return;

    dispatch(appendUserMessage(trimmed));
    setInput("");
    dispatch(sendChatMessage({ message: trimmed, repId: 1, sessionId }));
  };

  return (
    <div className="chat-mode">
      <div className="chat-mode__messages">
        {messages.length === 0 && (
          <div className="chat-mode__placeholder">
            Try: <em>"Met Dr. Sharma at Apollo Hospital, discussed Cardivex and Neurotol,
            follow up in 2 weeks"</em>
          </div>
        )}

        {messages.map((msg) => (
          <ChatBubble key={msg.id} message={msg} />
        ))}

        {status === "sending" && (
          <div className="chat-bubble chat-bubble--assistant">
            <div className="chat-bubble__content chat-bubble__typing">Thinking...</div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <form className="chat-mode__input-row" onSubmit={handleSend}>
        <input
          className="chat-mode__input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Describe the interaction, or ask to search, summarize, or recommend..."
        />
        <Button type="submit" variant="primary" disabled={status === "sending" || !input.trim()}>
          Send
        </Button>
      </form>

      <style>{`
        .chat-mode {
          display: flex;
          flex-direction: column;
          height: 560px;
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          background: var(--color-surface);
          overflow: hidden;
        }

        .chat-mode__messages {
          flex: 1;
          overflow-y: auto;
          padding: var(--space-lg);
          display: flex;
          flex-direction: column;
          gap: var(--space-sm);
        }

        .chat-mode__placeholder {
          margin: auto;
          text-align: center;
          color: var(--color-text-secondary);
          font-size: 13px;
          max-width: 360px;
          line-height: 1.6;
        }

        .chat-bubble {
          display: flex;
          max-width: 75%;
        }

        .chat-bubble--user {
          align-self: flex-end;
        }

        .chat-bubble--assistant {
          align-self: flex-start;
        }

        .chat-bubble__content {
          padding: 10px 14px;
          border-radius: var(--radius-md);
          font-size: 14px;
          line-height: 1.5;
          white-space: pre-wrap;
        }

        .chat-bubble--user .chat-bubble__content {
          background: var(--color-primary);
          color: #fff;
          border-bottom-right-radius: 4px;
        }

        .chat-bubble--assistant .chat-bubble__content {
          background: var(--color-bg);
          color: var(--color-text-primary);
          border-bottom-left-radius: 4px;
        }

        .chat-bubble__typing {
          color: var(--color-text-secondary);
          font-style: italic;
        }

        .chat-tool-chip {
          align-self: flex-start;
          background: var(--color-primary-light);
          color: var(--color-primary);
          font-size: 12px;
          font-weight: 600;
          padding: 6px 12px;
          border-radius: 999px;
        }

        .chat-tool-chip__detail {
          font-weight: 400;
          opacity: 0.85;
        }

        .chat-mode__input-row {
          display: flex;
          gap: var(--space-sm);
          padding: var(--space-md);
          border-top: 1px solid var(--color-border);
        }

        .chat-mode__input {
          flex: 1;
          border: 1px solid var(--color-border);
          border-radius: var(--radius-sm);
          padding: 10px 14px;
          font-size: 14px;
          font-family: var(--font-family);
        }

        .chat-mode__input:focus {
          outline: none;
          border-color: var(--color-primary);
          box-shadow: 0 0 0 3px var(--color-primary-light);
        }
      `}</style>
    </div>
  );
}

export default ChatMode;