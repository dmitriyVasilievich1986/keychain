/**
 * Helpers for reading password fields, tracking unsaved edits as drafts, and building the
 * `fields` list sent to the password API.
 *
 * The API replaces a password's whole field list on update, so all edits are sent together as the
 * full list of active fields, in position order.
 */

import type { PasswordField } from '@store/passwords';
import type { PasswordFieldRequest } from '@utils/apiClient/password/types';

/** Name/value split of a field row: 30% for the name, 70% for the value. */
export const NAME_INPUT_SX = { flex: 3, minWidth: 0 } as const;
export const VALUE_INPUT_SX = { flex: 7, minWidth: 0 } as const;

/**
 * Editable state of one field row in the password card.
 *
 * @property {string} key - Stable React key for the row.
 * @property {string} name - Field name as currently typed.
 * @property {string} value - Current value as currently typed.
 * @property {PasswordField | null} field - The saved field this draft edits, or `null` for a new
 * field that has not been saved yet.
 */
export type FieldDraft = {
  key: string;
  name: string;
  value: string;
  field: PasswordField | null;
};

/**
 * Returns the fields that are not deleted, ordered by their position.
 *
 * @param fields - All fields of a password.
 * @returns Active fields sorted by `position`.
 */
export function getActiveFields(fields: PasswordField[]): PasswordField[] {
  return fields.filter((field) => field.deletedAt === null).sort((a, b) => a.position - b.position);
}

/**
 * Returns the current value of a field: the last entry of its value history.
 *
 * @param field - The field to read.
 * @returns The latest value, or an empty string when the field has no values.
 */
export function getCurrentValue(field: PasswordField): string {
  return field.values.at(-1)?.value ?? '';
}

/**
 * Returns the previous values of a field (everything but the current one), newest first.
 *
 * @param field - The field to read.
 * @returns The field's value history without the current value.
 */
export function getHistoryValues(field: PasswordField): PasswordField['values'] {
  return field.values.slice(0, -1).reverse();
}

/**
 * Creates one draft per active field, initialised with the saved name and current value.
 *
 * @param fields - All fields of a password.
 * @returns Drafts for the active fields, in position order.
 */
export function createDrafts(fields: PasswordField[]): FieldDraft[] {
  return getActiveFields(fields).map((field) => ({
    key: `field-${field.position}`,
    name: field.name,
    value: getCurrentValue(field),
    field,
  }));
}

/**
 * Whether a draft differs from its saved field (always true for a new field).
 *
 * @param draft - The draft to check.
 * @returns `true` when the draft has unsaved changes.
 */
export function isDraftChanged(draft: FieldDraft): boolean {
  if (!draft.field) return true;
  return draft.name !== draft.field.name || draft.value !== getCurrentValue(draft.field);
}

/**
 * Whether a draft has both a name and a value.
 *
 * @param draft - The draft to check.
 * @returns `true` when the draft can be saved.
 */
export function isDraftValid(draft: FieldDraft): boolean {
  return draft.name.length > 0 && draft.value.length > 0;
}

/**
 * Builds the `fields` payload from the drafts.
 *
 * A changed value is appended to the field's value history instead of replacing the current value,
 * so the previous value is kept as history. A renamed field keeps its history. New fields are sent
 * with a single value.
 *
 * @param drafts - Drafts in the desired field order.
 * @returns The `fields` payload for a password patch request.
 */
export function toFieldRequests(drafts: FieldDraft[]): PasswordFieldRequest[] {
  return drafts.map((draft) => {
    if (!draft.field) return { name: draft.name, values: [{ value: draft.value }] };
    const values = draft.field.values.map(({ value }) => ({ value }));
    if (draft.value !== getCurrentValue(draft.field)) values.push({ value: draft.value });
    return { name: draft.name, values };
  });
}
