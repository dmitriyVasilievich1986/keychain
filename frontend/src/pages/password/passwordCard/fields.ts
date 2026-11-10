/**
 * Helpers for reading password fields, tracking unsaved edits as drafts, and building the
 * `fields` list sent to the password API.
 *
 * The API replaces a password's whole field list on update, so all edits are sent together as the
 * full list of fields, in position order. Deleted fields are sent too, with their `deletedAt`, so
 * they stay soft-deleted (with their history) instead of being erased.
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
 * @property {boolean} deleted - Whether the field is (or will be, after saving) marked as deleted.
 * @property {PasswordField | null} field - The saved field this draft edits, or `null` for a new
 * field that has not been saved yet.
 */
export type FieldDraft = {
  key: string;
  name: string;
  value: string;
  deleted: boolean;
  field: PasswordField | null;
};

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
 * Creates one draft per field, deleted ones included, initialised with the saved name and current
 * value.
 *
 * @param fields - All fields of a password.
 * @returns Drafts for all fields, in position order.
 */
export function createDrafts(fields: PasswordField[]): FieldDraft[] {
  return [...fields]
    .sort((a, b) => a.position - b.position)
    .map((field) => ({
      key: `field-${field.position}`,
      name: field.name,
      value: getCurrentValue(field),
      deleted: field.deletedAt !== null,
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
  if (draft.deleted !== (draft.field.deletedAt !== null)) return true;
  return draft.name !== draft.field.name || draft.value !== getCurrentValue(draft.field);
}

/**
 * Whether a draft can be saved: deleted fields always can, others need a name and a value.
 *
 * @param draft - The draft to check.
 * @returns `true` when the draft can be saved.
 */
export function isDraftValid(draft: FieldDraft): boolean {
  return draft.deleted || (draft.name.length > 0 && draft.value.length > 0);
}

/**
 * Marks a draft as deleted, dropping its unsaved name/value edits. A new, unsaved field has
 * nothing to keep, so it is removed instead.
 *
 * @param draft - The draft to delete.
 * @returns The deleted draft, or `null` when the draft should be removed.
 */
export function deleteDraft(draft: FieldDraft): FieldDraft | null {
  if (!draft.field) return null;
  return {
    ...draft,
    name: draft.field.name,
    value: getCurrentValue(draft.field),
    deleted: true,
  };
}

/**
 * Makes a deleted draft active again.
 *
 * @param draft - The draft to restore.
 * @returns The active draft.
 */
export function restoreDraft(draft: FieldDraft): FieldDraft {
  return { ...draft, deleted: false };
}

/**
 * Builds the `fields` payload from the drafts.
 *
 * A changed value is appended to the field's value history instead of replacing the current value,
 * so the previous value is kept as history. A renamed field keeps its history. New fields are sent
 * with a single value. Deleted fields keep their saved name and values and are sent with their
 * original `deletedAt`, or `now` when they are deleted by this update.
 *
 * @param drafts - Drafts in the desired field order.
 * @param now - Timestamp used for fields deleted by this update; defaults to the current time.
 * @returns The `fields` payload for a password patch request.
 */
export function toFieldRequests(
  drafts: FieldDraft[],
  now: string = new Date().toISOString()
): PasswordFieldRequest[] {
  return drafts.map((draft) => {
    if (!draft.field) {
      return { name: draft.name, values: [{ value: draft.value }], deletedAt: null };
    }
    const values = draft.field.values.map(({ value }) => ({ value }));
    if (draft.deleted) {
      return { name: draft.field.name, values, deletedAt: draft.field.deletedAt ?? now };
    }
    if (draft.value !== getCurrentValue(draft.field)) values.push({ value: draft.value });
    return { name: draft.name, values, deletedAt: null };
  });
}
