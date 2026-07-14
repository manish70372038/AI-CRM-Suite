/**
 * Root App component.
 *
 * Renders the persistent layout shell (Sidebar + TopBar) and the
 * routed page content via React Router. New pages should be added
 * to the <Routes> block here.
 */

import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import Sidebar from "./components/layout/Sidebar";
import TopBar from "./components/layout/TopBar";
import DashboardPage from "./pages/DashboardPage";
import LogInteractionPage from "./pages/LogInteractionPage";

function App() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <TopBar />
        <div className="app-content">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/log-interaction" element={<LogInteractionPage />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}

export default App;