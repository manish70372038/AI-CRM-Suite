/**
 * DashboardPage — route-level wrapper for the Dashboard component.
 *
 * Kept thin on purpose: pages are responsible for route wiring only,
 * while actual UI/logic lives in components/. This separation makes
 * it easy to add page-level concerns later (e.g. breadcrumbs, meta
 * tags) without touching the Dashboard component itself.
 */

import React from "react";
import Dashboard from "../components/dashboard/Dashboard";

function DashboardPage() {
  return <Dashboard />;
}

export default DashboardPage;