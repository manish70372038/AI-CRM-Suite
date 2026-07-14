/**
 * Application entrypoint.
 *
 * Mounts the React tree, wrapping App with:
 * - Redux `Provider` so every component can access the store
 * - `BrowserRouter` so routing (React Router) is available app-wide
 *
 * Global styles are imported once here.
 */

import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";
import { BrowserRouter } from "react-router-dom";

import App from "./App";
import store from "./store/store";
import "./styles/globals.css";

const root = ReactDOM.createRoot(document.getElementById("root"));

root.render(
  <React.StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </Provider>
  </React.StrictMode>
);