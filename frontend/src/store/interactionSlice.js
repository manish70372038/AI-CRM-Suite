/**
 * Interaction slice.
 *
 * Owns:
 * - `list`: interactions fetched for the Dashboard / search results
 * - `selected`: the currently open interaction (for view/edit)
 * - `draft`: the in-progress form data. Shared between Form Mode and
 *   Chat Mode so that when the AI extracts entities from a chat
 *   message, switching to the Form tab shows those values pre-filled
 *   and editable.
 *
 * Async thunks call the backend via axiosClient and are the only
 * place API calls for interactions happen — components never call
 * axios directly.
 */

import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axiosClient from "../api/axiosClient";

const emptyDraft = {
  doctor_name: "",
  hospital: "",
  interaction_type: "visit",
  products_discussed: [],
  raw_notes: "",
  follow_up_date: "",
  follow_up_action: "",
  sentiment: "",
};

// --- Thunks -----------------------------------------------------------

export const fetchInteractions = createAsyncThunk(
  "interactions/fetchAll",
  async (filters = {}, { rejectWithValue }) => {
    try {
      const response = await axiosClient.get("/interaction", { params: filters });
      return response.data;
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const fetchInteractionById = createAsyncThunk(
  "interactions/fetchOne",
  async (id, { rejectWithValue }) => {
    try {
      const response = await axiosClient.get(`/interaction/${id}`);
      return response.data;
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const createInteraction = createAsyncThunk(
  "interactions/create",
  async (payload, { rejectWithValue }) => {
    try {
      const response = await axiosClient.post("/interaction", payload);
      return response.data;
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const updateInteraction = createAsyncThunk(
  "interactions/update",
  async ({ id, changes }, { rejectWithValue }) => {
    try {
      const response = await axiosClient.put(`/interaction/${id}`, changes);
      return response.data;
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

// --- Slice --------------------------------------------------------------

const interactionSlice = createSlice({
  name: "interactions",
  initialState: {
    list: [],
    selected: null,
    draft: { ...emptyDraft },
    status: "idle", // idle | loading | succeeded | failed
    error: null,
    lastSavedId: null,
  },
  reducers: {
    updateDraftField: (state, action) => {
      const { field, value } = action.payload;
      state.draft[field] = value;
    },
    setDraftFromExtraction: (state, action) => {
      // Merges AI-extracted entities (from chat) into the draft without
      // wiping fields the user may have already typed manually.
      state.draft = { ...state.draft, ...action.payload };
    },
    resetDraft: (state) => {
      state.draft = { ...emptyDraft };
      state.lastSavedId = null;
    },
    clearSelected: (state) => {
      state.selected = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.list = action.payload;
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
      })
      .addCase(fetchInteractionById.fulfilled, (state, action) => {
        state.selected = action.payload;
      })
      .addCase(createInteraction.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.list.unshift(action.payload);
        state.lastSavedId = action.payload.id;
        state.draft = { ...emptyDraft };
      })
      .addCase(createInteraction.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
      })
      .addCase(updateInteraction.fulfilled, (state, action) => {
        const idx = state.list.findIndex((item) => item.id === action.payload.id);
        if (idx !== -1) state.list[idx] = action.payload;
        if (state.selected?.id === action.payload.id) state.selected = action.payload;
      });
  },
});

export const { updateDraftField, setDraftFromExtraction, resetDraft, clearSelected } =
  interactionSlice.actions;

export default interactionSlice.reducer;