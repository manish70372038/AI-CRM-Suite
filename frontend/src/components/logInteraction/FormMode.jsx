/**
 * FormMode — structured interaction logging form.
 *
 * Reads/writes the shared `draft` object in interactionSlice rather
 * than local component state. This is what makes cross-mode sync
 * work: when ChatMode dispatches `setDraftFromExtraction` after the
 * Log Interaction tool extracts entities from a chat message, this
 * form immediately reflects those values without any extra wiring.
 *
 * DUPLICATE-SAVE FIX: if `activeInteractionId` is set, it means Chat
 * Mode already saved this interaction to the DB. In that case,
 * submitting the form calls UPDATE (PUT /interaction/{id}) instead of
 * CREATE (POST /interaction) — so editing AI-extracted fields here
 * before saving never creates a second, duplicate record.
 */

import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import Input from "../common/Input";
import Button from "../common/Button";
import {
  updateDraftField,
  createInteraction,
  updateInteraction,
  resetDraft,
} from "../../store/interactionSlice";
import { fetchHcps } from "../../store/hcpSlice";

const INTERACTION_TYPE_OPTIONS = [
  { value: "visit", label: "In-Person Visit" },
  { value: "call", label: "Phone Call" },
  { value: "email", label: "Email" },
  { value: "virtual", label: "Virtual Meeting" },
];

const SENTIMENT_OPTIONS = [
  { value: "positive", label: "Positive" },
  { value: "neutral", label: "Neutral" },
  { value: "negative", label: "Negative" },
];

function FormMode() {
  const dispatch = useDispatch();
  const { draft, activeInteractionId, status, error } = useSelector((state) => state.interactions);
  const [productsText, setProductsText] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");

  useEffect(() => {
    dispatch(fetchHcps());
  }, [dispatch]);

  // Keep the free-text products input in sync if the draft was
  // populated externally (e.g. from chat extraction).
  useEffect(() => {
    setProductsText((draft.products_discussed || []).join(", "));
  }, [draft.products_discussed]);

  const handleChange = (field) => (e) => {
    dispatch(updateDraftField({ field, value: e.target.value }));
  };

  const handleProductsChange = (e) => {
    setProductsText(e.target.value);
    const products = e.target.value
      .split(",")
      .map((p) => p.trim())
      .filter(Boolean);
    dispatch(updateDraftField({ field: "products_discussed", value: products }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitted(true);
    setSuccessMsg("");

    if (!draft.doctor_name.trim() || !draft.raw_notes.trim()) {
      return; // basic client-side validation
    }

    if (activeInteractionId) {
      // Already saved via AI Chat — UPDATE the same record, don't duplicate.
      const changes = {
        doctor_name: draft.doctor_name,
        hospital: draft.hospital || null,
        interaction_type: draft.interaction_type,
        products_discussed: draft.products_discussed,
        summary: draft.raw_notes, // form's "Notes" maps to the record's summary/raw_notes
        raw_notes: draft.raw_notes,
        follow_up_date: draft.follow_up_date || null,
        follow_up_action: draft.follow_up_action || null,
        sentiment: draft.sentiment || null,
      };
      const result = await dispatch(updateInteraction({ id: activeInteractionId, changes }));
      if (updateInteraction.fulfilled.match(result)) {
        setSuccessMsg(`✓ Interaction #${activeInteractionId} updated successfully.`);
        dispatch(resetDraft());
        setProductsText("");
      }
    } else {
      // Fresh entry — CREATE a new record.
      const payload = {
        ...draft,
        rep_id: 1, // single-tenant default rep, per architecture scope
        source: "form",
        follow_up_date: draft.follow_up_date || null,
        sentiment: draft.sentiment || null,
      };
      const result = await dispatch(createInteraction(payload));
      if (createInteraction.fulfilled.match(result)) {
        setSuccessMsg(`✓ Interaction #${result.payload.id} saved successfully.`);
        setProductsText("");
      }
    }

    setSubmitted(false);
  };

  const handleReset = () => {
    dispatch(resetDraft());
    setProductsText("");
    setSubmitted(false);
    setSuccessMsg("");
  };

  return (
    <form className="form-mode" onSubmit={handleSubmit}>
      {activeInteractionId && (
        <div className="form-mode__notice">
          ℹ️ This interaction was already logged via AI Chat (#{activeInteractionId}). Saving here
          will <strong>update</strong> that record, not create a new one.
        </div>
      )}

      {successMsg && <div className="form-mode__success">{successMsg}</div>}
      {error && <div className="form-mode__error">{error}</div>}

      <div className="form-mode__grid">
        <Input
          label="Doctor Name"
          name="doctor_name"
          value={draft.doctor_name}
          onChange={handleChange("doctor_name")}
          placeholder="Dr. Ayesha Sharma"
          required
          error={submitted && !draft.doctor_name.trim() ? "Doctor name is required" : ""}
        />

        <Input
          label="Hospital / Clinic"
          name="hospital"
          value={draft.hospital}
          onChange={handleChange("hospital")}
          placeholder="Apollo Hospital"
        />

        <Input
          as="select"
          label="Interaction Type"
          name="interaction_type"
          value={draft.interaction_type}
          onChange={handleChange("interaction_type")}
          options={INTERACTION_TYPE_OPTIONS}
        />

        <Input
          label="Products Discussed"
          name="products_discussed"
          value={productsText}
          onChange={handleProductsChange}
          placeholder="Cardivex, Neurotol (comma-separated)"
          helpText="Separate multiple products with commas"
        />

        <Input
          type="date"
          label="Follow-up Date"
          name="follow_up_date"
          value={draft.follow_up_date}
          onChange={handleChange("follow_up_date")}
        />

        <Input
          as="select"
          label="Sentiment"
          name="sentiment"
          value={draft.sentiment}
          onChange={handleChange("sentiment")}
          options={SENTIMENT_OPTIONS}
          placeholder="Select sentiment (optional)"
        />
      </div>

      <Input
        as="textarea"
        label="Notes"
        name="raw_notes"
        rows={5}
        value={draft.raw_notes}
        onChange={handleChange("raw_notes")}
        placeholder="Describe what was discussed during the interaction..."
        required
        error={submitted && !draft.raw_notes.trim() ? "Notes are required" : ""}
      />

      <Input
        as="textarea"
        label="Follow-up Action"
        name="follow_up_action"
        rows={2}
        value={draft.follow_up_action}
        onChange={handleChange("follow_up_action")}
        placeholder="e.g. Send clinical trial data for Neurotol"
      />

      <div className="form-mode__actions">
        <Button variant="secondary" type="button" onClick={handleReset}>
          Clear
        </Button>
        <Button variant="primary" type="submit" disabled={status === "loading"}>
          {status === "loading"
            ? "Saving..."
            : activeInteractionId
            ? "Update Interaction"
            : "Save Interaction"}
        </Button>
      </div>

      <style>{`
        .form-mode {
          display: flex;
          flex-direction: column;
          gap: var(--space-md);
        }

        .form-mode__grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: var(--space-md);
        }

        .form-mode__actions {
          display: flex;
          justify-content: flex-end;
          gap: var(--space-sm);
          padding-top: var(--space-sm);
        }

        .form-mode__notice {
          background: var(--color-primary-light);
          color: var(--color-primary);
          padding: var(--space-sm) var(--space-md);
          border-radius: var(--radius-sm);
          font-size: 13px;
          line-height: 1.5;
        }

        .form-mode__success {
          background: var(--color-success-light);
          color: var(--color-success);
          padding: var(--space-sm) var(--space-md);
          border-radius: var(--radius-sm);
          font-size: 13px;
          font-weight: 600;
        }

        .form-mode__error {
          background: var(--color-danger-light);
          color: var(--color-danger);
          padding: var(--space-sm) var(--space-md);
          border-radius: var(--radius-sm);
          font-size: 13px;
          font-weight: 600;
        }

        @media (max-width: 720px) {
          .form-mode__grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </form>
  );
}

export default FormMode;