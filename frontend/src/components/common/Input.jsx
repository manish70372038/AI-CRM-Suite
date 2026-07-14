/**
 * Reusable Input primitive.
 *
 * A single component handles text/date/number inputs, textareas, and
 * selects (via the `as` prop) so every form field in the app shares
 * consistent label/error/help-text styling instead of duplicating it
 * per field.
 */

import React from "react";

function Input({
  as = "input",
  label,
  name,
  value,
  onChange,
  type = "text",
  placeholder = "",
  error = "",
  helpText = "",
  options = [], // for as="select": [{ value, label }]
  rows = 4,
  required = false,
  ...rest
}) {
  const fieldId = `field-${name}`;

  return (
    <div className="field">
      {label && (
        <label htmlFor={fieldId} className="field__label">
          {label}
          {required && <span className="field__required">*</span>}
        </label>
      )}

      {as === "textarea" ? (
        <textarea
          id={fieldId}
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          rows={rows}
          className={`field__control${error ? " field__control--error" : ""}`}
          {...rest}
        />
      ) : as === "select" ? (
        <select
          id={fieldId}
          name={name}
          value={value}
          onChange={onChange}
          className={`field__control${error ? " field__control--error" : ""}`}
          {...rest}
        >
          <option value="" disabled>
            {placeholder || "Select..."}
          </option>
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      ) : (
        <input
          id={fieldId}
          name={name}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className={`field__control${error ? " field__control--error" : ""}`}
          {...rest}
        />
      )}

      {helpText && !error && <span className="field__help">{helpText}</span>}
      {error && <span className="field__error">{error}</span>}

      <style>{`
        .field {
          display: flex;
          flex-direction: column;
          gap: 6px;
          width: 100%;
        }

        .field__label {
          font-size: 13px;
          font-weight: 600;
          color: var(--color-text-primary);
        }

        .field__required {
          color: var(--color-danger);
          margin-left: 2px;
        }

        .field__control {
          border: 1px solid var(--color-border);
          border-radius: var(--radius-sm);
          padding: 10px 12px;
          font-size: 14px;
          background: var(--color-surface);
          color: var(--color-text-primary);
          transition: border-color 0.15s ease, box-shadow 0.15s ease;
          width: 100%;
        }

        .field__control:focus {
          outline: none;
          border-color: var(--color-primary);
          box-shadow: 0 0 0 3px var(--color-primary-light);
        }

        .field__control--error {
          border-color: var(--color-danger);
        }

        textarea.field__control {
          resize: vertical;
          font-family: var(--font-family);
        }

        .field__help {
          font-size: 12px;
          color: var(--color-text-secondary);
        }

        .field__error {
          font-size: 12px;
          color: var(--color-danger);
        }
      `}</style>
    </div>
  );
}

export default Input;