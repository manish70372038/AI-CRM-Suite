/**
 * LogInteractionPage — route-level wrapper for LogInteractionScreen.
 *
 * Kept thin, consistent with DashboardPage, so routing concerns stay
 * separate from the screen's actual implementation.
 */

import React from "react";
import LogInteractionScreen from "../components/logInteraction/LogInteractionScreen";

function LogInteractionPage() {
  return <LogInteractionScreen />;
}

export default LogInteractionPage;