/**
 * HCP slice.
 *
 * Holds the list of known Healthcare Professionals, fetched once and
 * used to power autocomplete suggestions in Form Mode (so reps can
 * select an existing doctor instead of retyping details already on
 * file). Kept intentionally small — this is a read-only lookup list,
 * not a full HCP management module (out of scope for this task).
 */

import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axiosClient from "../api/axiosClient";

export const fetchHcps = createAsyncThunk(
  "hcps/fetchAll",
  async (_, { rejectWithValue }) => {
    try {
      const response = await axiosClient.get("/hcp");
      return response.data;
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

const hcpSlice = createSlice({
  name: "hcps",
  initialState: {
    list: [],
    status: "idle", // idle | loading | succeeded | failed
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchHcps.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchHcps.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.list = action.payload;
      })
      .addCase(fetchHcps.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
      });
  },
});

export default hcpSlice.reducer;