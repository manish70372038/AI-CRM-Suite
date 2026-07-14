/**
 * InteractionTable — reusable list view for interactions.
 *
 * Used by the Dashboard (recent interactions) and can be reused
 * anywhere a filtered list of interactions needs to be shown (e.g.
 * search results). Clicking a row opens a detail/edit modal; saving
 * changes dispatches `updateInteraction`, which calls
 * PUT /interaction/{id} (the Edit Interaction tool path).
 */

import React, { useState } from "react";
import { useDispatch } from "react-redux";

import Badge from "../common/Badge";
import Modal from "../common/Modal";
import Input from "../common/Input";
import Button from "../common/Button";
import { updateInteraction } from "../../store/interactionSlice";

const SENTIMENT_TONE = {
  positive: "success",
  neutral: "neutral",
  negative: "danger",
};

const TYPE_TONE = {
  visit: "primary",
  call: "warning",
  email: "neutral",
  virtual: "success",
};

function formatDate(dateStr) {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return dateStr;
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

function InteractionTable({ interactions, emptyMessage = "No interactions found." }) {
  const dispatch = useDispatch();
  const [selected, setSelected] = useState(null);
  const [editForm, setEditForm] = useState(null);
  const [saving, setSaving] = useState(false);

  const openRow = (item) => {
    setSelected(item);
    setEditForm({
      follow_up_date: item.follow_up_date || "",
      follow_up_action: item.follow_up_action || "",
      summary: item.summary || "",
    });
  };

  const closeModal = () => {
    setSelected(null);
    setEditForm(null);
  };

  const handleFieldChange = (field, value) => {
    setEditForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    if (!selected) return;
    setSaving(true);
    try {
      await dispatch(updateInteraction({ id: selected.id, changes: editForm })).unwrap();
      closeModal();
    } catch (err) {
      // Error surfaced via slice state; keep modal open so user can retry.
      console.error("Failed to update interaction:", err);
    } finally {
      setSaving(false);
    }
  };

  if (!interactions || interactions.length === 0) {
    return <div className="empty-state">{emptyMessage}</div>;
  }

  return (
    <>
      <div className="table-wrapper card">
        <table className="interaction-table">
          <thead>
            <tr>
              <th>Doctor</th>
              <th>Hospital</th>
              <th>Type</th>
              <th>Products</th>
              <th>Follow-up</th>
              <th>Sentiment</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {interactions.map((item) => (
              <tr key={item.id} onClick={() => openRow(item)}>
                <td className="cell-strong">{item.doctor_name}</td>
                <td className="text-muted">{item.hospital || "—"}</td>
                <td>
                  <Badge tone={TYPE_TONE[item.interaction_type] || "neutral"}>
                    {item.interaction_type}
                  </Badge>
                </td>
                <td className="text-muted">
                  {(item.products_discussed || []).join(", ") || "—"}
                </td>
                <td className="text-muted">{formatDate(item.follow_up_date)}</td>
                <td>
                  {item.sentiment ? (
                    <Badge tone={SENTIMENT_TONE[item.sentiment] || "neutral"}>
                      {item.sentiment}
                    </Badge>
                  ) : (
                    "—"
                  )}
                </td>
                <td>
                  <Badge tone="neutral">{item.source}</Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal
        isOpen={!!selected}
        onClose={closeModal}
        title={selected ? `${selected.doctor_name} — Interaction Detail` : ""}
        footer={
          <>
            <Button variant="secondary" onClick={closeModal}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSave} disabled={saving}>
              {saving ? "Saving..." : "Save Changes"}
            </Button>
          </>
        }
      >
        {selected && editForm && (
          <>
            <div className="detail-meta">
              <span className="text-muted text-sm">Hospital: {selected.hospital || "—"}</span>
              <span className="text-muted text-sm">
                Products: {(selected.products_discussed || []).join(", ") || "—"}
              </span>
            </div>

            <Input
              as="textarea"
              label="Summary"
              name="summary"
              rows={3}
              value={editForm.summary}
              onChange={(e) => handleFieldChange("summary", e.target.value)}
            />

            <Input
              type="date"
              label="Follow-up Date"
              name="follow_up_date"
              value={editForm.follow_up_date}
              onChange={(e) => handleFieldChange("follow_up_date", e.target.value)}
            />

            <Input
              as="textarea"
              label="Follow-up Action"
              name="follow_up_action"
              rows={2}
              value={editForm.follow_up_action}
              onChange={(e) => handleFieldChange("follow_up_action", e.target.value)}
            />
          </>
        )}
      </Modal>

      <style>{`
        .table-wrapper {
          overflow-x: auto;
        }

        .interaction-table {
          width: 100%;
          border-collapse: collapse;
        }

        .interaction-table th {
          text-align: left;
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 0.03em;
          color: var(--color-text-secondary);
          padding: 12px 16px;
          border-bottom: 1px solid var(--color-border);
          white-space: nowrap;
        }

        .interaction-table td {
          padding: 14px 16px;
          border-bottom: 1px solid var(--color-border);
          font-size: 13px;
          vertical-align: middle;
        }

        .interaction-table tbody tr {
          cursor: pointer;
          transition: background-color 0.12s ease;
        }

        .interaction-table tbody tr:hover {
          background: var(--color-bg);
        }

        .interaction-table tbody tr:last-child td {
          border-bottom: none;
        }

        .cell-strong {
          font-weight: 600;
          color: var(--color-text-primary);
        }

        .empty-state {
          padding: var(--space-2xl);
          text-align: center;
          color: var(--color-text-secondary);
          font-size: 13px;
        }

        .detail-meta {
          display: flex;
          flex-direction: column;
          gap: 4px;
          padding-bottom: var(--space-sm);
          border-bottom: 1px solid var(--color-border);
        }
      `}</style>
    </>
  );
}

export default InteractionTable;