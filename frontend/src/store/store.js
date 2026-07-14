/**
 * Root Redux store.
 *
 * Combines all feature slices. This is the only file that assembles
 * the store — components and thunks never construct state manually.
 */

import { configureStore } from "@reduxjs/toolkit";
import interactionReducer from "./interactionSlice";
import chatReducer from "./chatSlice";
import hcpReducer from "./hcpSlice";

export const store = configureStore({
  reducer: {
    interactions: interactionReducer,
    chat: chatReducer,
    hcps: hcpReducer,
  },
});

export default store;