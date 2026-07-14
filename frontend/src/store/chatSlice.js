/**
 * Chat slice.
 *
 * Owns the conversational Log Interaction experience: message history,
 * the active session id (so the backend can maintain LangGraph agent
 * state across turns), and the sendMessage thunk.
 *
 * When the agent's response includes structured extracted data (e.g.
 * after the Log Interaction tool runs), the ChatMode component reads
 * `lastToolResult` and dispatches `setDraftFromExtraction` on the
 * interaction slice so Form Mode stays in sync — that cross-slice
 * wiring happens in the component, not here, to keep slices decoupled.
 */

import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axiosClient from "../api/axiosClient";

export const sendChatMessage = createAsyncThunk(
  "chat/sendMessage",
  async ({ message, repId, sessionId }, { rejectWithValue }) => {
    try {
      const response = await axiosClient.post("/chat", {
        message,
        rep_id: repId,
        session_id: sessionId,
      });
      return response.data;
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

const chatSlice = createSlice({
  name: "chat",
  initialState: {
    sessionId: null,
    messages: [], // { id, role: 'user' | 'assistant' | 'tool', content, toolName? }
    lastToolResult: null,
    status: "idle", // idle | sending | succeeded | failed
    error: null,
  },
  reducers: {
    appendUserMessage: (state, action) => {
      state.messages.push({
        id: `local-${Date.now()}`,
        role: "user",
        content: action.payload,
      });
    },
    clearChat: (state) => {
      state.sessionId = null;
      state.messages = [];
      state.lastToolResult = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => {
        state.status = "sending";
        state.error = null;
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.sessionId = action.payload.session_id;

        if (action.payload.tool_name) {
          state.messages.push({
            id: `tool-${Date.now()}`,
            role: "tool",
            toolName: action.payload.tool_name,
            content: action.payload.tool_summary || `Ran ${action.payload.tool_name}`,
          });
          state.lastToolResult = {
            toolName: action.payload.tool_name,
            data: action.payload.tool_result,
          };
        }

        state.messages.push({
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: action.payload.reply,
        });
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
        state.messages.push({
          id: `error-${Date.now()}`,
          role: "assistant",
          content: "Sorry, something went wrong processing that. Please try again.",
        });
      });
  },
});

export const { appendUserMessage, clearChat } = chatSlice.actions;

export default chatSlice.reducer;