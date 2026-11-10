/**
 * Tests for the password field helpers: active-field ordering, current/history values, drafts,
 * and the `fields` payload sent to the password API.
 */

import { describe, expect, it } from 'vite-plus/test';

import {
  createDrafts,
  getActiveFields,
  getCurrentValue,
  getHistoryValues,
  isDraftChanged,
  isDraftValid,
  toFieldRequests,
  type FieldDraft,
} from './fields';

import type { PasswordField } from '@store/passwords';

function makeField(overrides: Partial<PasswordField> = {}): PasswordField {
  return {
    name: 'username',
    position: 0,
    values: [{ value: 'alice', createdAt: '2026-01-01T00:00:00Z' }],
    createdAt: '2026-01-01T00:00:00Z',
    updatedAt: '2026-01-01T00:00:00Z',
    deletedAt: null,
    ...overrides,
  };
}

const username = makeField({
  values: [
    { value: 'alice', createdAt: '2026-01-01T00:00:00Z' },
    { value: 'alice2', createdAt: '2026-02-01T00:00:00Z' },
    { value: 'alice3', createdAt: '2026-03-01T00:00:00Z' },
  ],
});
const secret = makeField({
  name: 'password',
  position: 1,
  values: [{ value: 'hunter2', createdAt: '2026-01-01T00:00:00Z' }],
});
const deleted = makeField({ name: 'pin', position: 2, deletedAt: '2026-02-01T00:00:00Z' });

function draftOf(field: PasswordField, overrides: Partial<FieldDraft> = {}): FieldDraft {
  return {
    key: `field-${field.position}`,
    name: field.name,
    value: getCurrentValue(field),
    field,
    ...overrides,
  };
}

describe('password field helpers', () => {
  it('getActiveFields drops deleted fields and orders by position', () => {
    expect(getActiveFields([deleted, secret, username])).toEqual([username, secret]);
  });

  it('getCurrentValue returns the last value, or an empty string without values', () => {
    expect(getCurrentValue(username)).toBe('alice3');
    expect(getCurrentValue(makeField({ values: [] }))).toBe('');
  });

  it('getHistoryValues returns the previous values newest first', () => {
    expect(getHistoryValues(username).map((v) => v.value)).toEqual(['alice2', 'alice']);
    expect(getHistoryValues(secret)).toEqual([]);
  });

  it('createDrafts starts from the saved names and current values of active fields', () => {
    expect(createDrafts([deleted, secret, username])).toEqual([draftOf(username), draftOf(secret)]);
  });

  it('isDraftChanged detects renamed, re-valued and new fields', () => {
    expect(isDraftChanged(draftOf(username))).toBe(false);
    expect(isDraftChanged(draftOf(username, { name: 'login' }))).toBe(true);
    expect(isDraftChanged(draftOf(username, { value: 'bob' }))).toBe(true);
    expect(isDraftChanged({ key: 'new-0', name: 'email', value: 'a@b.c', field: null })).toBe(true);
  });

  it('isDraftValid requires a name and a value', () => {
    expect(isDraftValid(draftOf(username))).toBe(true);
    expect(isDraftValid(draftOf(username, { name: '' }))).toBe(false);
    expect(isDraftValid(draftOf(username, { value: '' }))).toBe(false);
  });

  it('toFieldRequests keeps unchanged fields as they are', () => {
    expect(toFieldRequests([draftOf(username), draftOf(secret)])).toEqual([
      {
        name: 'username',
        values: [{ value: 'alice' }, { value: 'alice2' }, { value: 'alice3' }],
      },
      { name: 'password', values: [{ value: 'hunter2' }] },
    ]);
  });

  it('toFieldRequests appends a changed value to the history instead of replacing it', () => {
    expect(toFieldRequests([draftOf(secret, { value: 'correct-horse' })])).toEqual([
      { name: 'password', values: [{ value: 'hunter2' }, { value: 'correct-horse' }] },
    ]);
  });

  it('toFieldRequests renames a field while keeping its history', () => {
    expect(toFieldRequests([draftOf(username, { name: 'login' })])).toEqual([
      { name: 'login', values: [{ value: 'alice' }, { value: 'alice2' }, { value: 'alice3' }] },
    ]);
  });

  it('toFieldRequests sends new fields with a single value', () => {
    expect(
      toFieldRequests([{ key: 'new-0', name: 'email', value: 'a@example.com', field: null }])
    ).toEqual([{ name: 'email', values: [{ value: 'a@example.com' }] }]);
  });
});
