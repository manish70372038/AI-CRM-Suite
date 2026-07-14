/**
 * Dashboard — landing page showing summary stats and recent
 * interactions, with a search box for filtering.
 *
 * The search box triggers `fetchInteractions` with a `q` filter,
 * which the backend routes through the Search Interaction tool for
 * natural-language-aware filtering (falls back to simple substring
 * match on doctor_name/hospital if the query isn't NL-style).
 */

import React, { useEffect, useMemo, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import InteractionTable from "./InteractionTable";
import Input from "../common/Input";
import { fetchInteractions } from "../../store/interactionSlice";

function StatCard({ label, value, tone }) {
  return (
    <div className="stat-card card">
      <div className="stat-card__label">{label}</div>
      <div className={`stat-card__value stat-card__value--${tone}`}>{value}</div>
    </div>
  );
}

function Dashboard() {
  const dispatch = useDispatch();
  const { list, status } = useSelector((state) => state.interactions);
  const [query, setQuery] = useState("");

  useEffect(() => {
    dispatch(fetchInteractions());
  }, [dispatch]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    dispatch(fetchInteractions(query ? { q: query } : {}));
  };

  const stats = useMemo(() => {
    const total = list.length;
    const today = new Date().toISOString().slice(0, 10);
    const pendingFollowUps = list.filter(
      (item) => item.follow_up_date && item.follow_up_date >= today
    ).length;
    const positive = list.filter((item) => item.sentiment === "positive").length;

    return { total, pendingFollowUps, positive };
  }, [list]);

  return (
    <div className="dashboard">
      <div className="dashboard__stats">
        <StatCard label="Total Interactions" value={stats.total} tone="primary" />
        <StatCard label="Pending Follow-ups" value={stats.pendingFollowUps} tone="warning" />
        <StatCard label="Positive Sentiment" value={stats.positive} tone="success" />
      </div>

      <form className="dashboard__search" onSubmit={handleSearchSubmit}>
        <Input
          name="search"
          placeholder="Search by doctor, hospital, or e.g. 'meetings about Cardivex last month'"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </form>

      <div className="dashboard__section-header">
        <h2>Recent Interactions</h2>
      </div>

      {status === "loading" ? (
        <div className="empty-state">Loading interactions...</div>
      ) : (
        <InteractionTable interactions={list} />
      )}

      <style>{`
        .dashboard {
          display: flex;
          flex-direction: column;
          gap: var(--space-lg);
        }

        .dashboard__stats {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: var(--space-md);
        }

        .stat-card {
          padding: var(--space-lg);
        }

        .stat-card__label {
          font-size: 12px;
          color: var(--color-text-secondary);
          margin-bottom: 6px;
        }

        .stat-card__value {
          font-size: 28px;
          font-weight: 800;
        }

        .stat-card__value--primary { color: var(--color-primary); }
        .stat-card__value--warning { color: var(--color-warning); }
        .stat-card__value--success { color: var(--color-success); }

        .dashboard__search {
          max-width: 480px;
        }

        .dashboard__section-header h2 {
          font-size: 15px;
          font-weight: 700;
          color: var(--color-text-primary);
        }

        .empty-state {
          padding: var(--space-2xl);
          text-align: center;
          color: var(--color-text-secondary);
          font-size: 13px;
        }
      `}</style>
    </div>
  );
}

export default Dashboard;