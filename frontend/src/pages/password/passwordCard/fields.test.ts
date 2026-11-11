/**
 * Tests for the password field helpers: active-field ordering, current/history values, drafts,
 * and the `fields` payload sent to the password API.
 */

import { describe, expect, it } from 'vite-plus/test';

import {
  createDrafts,
  deleteDraft,
  getCurrentValue,
  getHistoryValues,
  isDraftChanged,
  isDraftValid,
  restoreDraft,
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
    deleted: field.deletedAt !== null,
    field,
    ...overrides,
  };
}

describe('password field helpers', () => {
  it('getCurrentValue returns the last value, or an empty string without values', () => {
    expect(getCurrentValue(username)).toBe('alice3');
    expect(getCurrentValue(makeField({ values: [] }))).toBe('');
  });

  it('getHistoryValues returns the previous values newest first', () => {
    expect(getHistoryValues(username).map((v) => v.value)).toEqual(['alice2', 'alice']);
    expect(getHistoryValues(secret)).toEqual([]);
  });

  it('createDrafts covers all fields in position order, marking deleted ones', () => {
    const drafts = createDrafts([deleted, secret, username]);
    expect(drafts).toEqual([draftOf(username), draftOf(secret), draftOf(deleted)]);
    expect(drafts.map((d) => d.deleted)).toEqual([false, false, true]);
  });

  it('isDraftChanged detects renamed, re-valued and new fields', () => {
    expect(isDraftChanged(draftOf(username))).toBe(false);
    expect(isDraftChanged(draftOf(username, { name: 'login' }))).toBe(true);
    expect(isDraftChanged(draftOf(username, { value: 'bob' }))).toBe(true);
    expect(
      isDraftChanged({ key: 'new-0', name: 'email', value: 'a@b.c', deleted: false, field: null })
    ).toBe(true);
  });

  it('isDraftChanged detects deleting and restoring a field', () => {
    expect(isDraftChanged(draftOf(deleted))).toBe(false);
    expect(isDraftChanged(draftOf(username, { deleted: true }))).toBe(true);
    expect(isDraftChanged(draftOf(deleted, { deleted: false }))).toBe(true);
  });

  it('deleteDraft marks a saved field deleted and drops its unsaved edits', () => {
    expect(deleteDraft(draftOf(username, { name: 'login', value: 'bob' }))).toEqual(
      draftOf(username, { deleted: true })
    );
  });

  it('deleteDraft removes a new field', () => {
    expect(
      deleteDraft({ key: 'new-0', name: 'email', value: 'a@b.c', deleted: false, field: null })
    ).toBeNull();
  });

  it('restoreDraft makes a deleted field active again', () => {
    expect(restoreDraft(draftOf(deleted))).toEqual(draftOf(deleted, { deleted: false }));
  });

  it('isDraftValid requires a name and a value', () => {
    expect(isDraftValid(draftOf(username))).toBe(true);
    expect(isDraftValid(draftOf(username, { name: '' }))).toBe(false);
    expect(isDraftValid(draftOf(username, { value: '' }))).toBe(false);
    expect(isDraftValid(draftOf(username, { value: '', deleted: true }))).toBe(true);
  });

  const T1 = '2026-01-01T00:00:00Z';
  const usernameValues = [
    { value: 'alice', createdAt: T1 },
    { value: 'alice2', createdAt: '2026-02-01T00:00:00Z' },
    { value: 'alice3', createdAt: '2026-03-01T00:00:00Z' },
  ];

  it('toFieldRequests keeps unchanged fields as they are', () => {
    expect(toFieldRequests([draftOf(username), draftOf(secret)])).toEqual([
      { name: 'username', values: usernameValues, createdAt: T1, deletedAt: null },
      {
        name: 'password',
        values: [{ value: 'hunter2', createdAt: T1 }],
        createdAt: T1,
        deletedAt: null,
      },
    ]);
  });

  it('toFieldRequests appends a changed value to the history instead of replacing it', () => {
    const now = '2026-05-01T00:00:00.000Z';
    expect(toFieldRequests([draftOf(secret, { value: 'correct-horse' })], now)).toEqual([
      {
        name: 'password',
        values: [
          { value: 'hunter2', createdAt: T1 },
          { value: 'correct-horse', createdAt: now },
        ],
        createdAt: T1,
        deletedAt: null,
      },
    ]);
  });

  it('toFieldRequests renames a field while keeping its history', () => {
    expect(toFieldRequests([draftOf(username, { name: 'login' })])).toEqual([
      { name: 'login', values: usernameValues, createdAt: T1, deletedAt: null },
    ]);
  });

  it('toFieldRequests sends new fields with a single value created now', () => {
    const now = '2026-05-01T00:00:00.000Z';
    expect(
      toFieldRequests(
        [{ key: 'new-0', name: 'email', value: 'a@example.com', deleted: false, field: null }],
        now
      )
    ).toEqual([
      {
        name: 'email',
        values: [{ value: 'a@example.com', createdAt: now }],
        createdAt: now,
        deletedAt: null,
      },
    ]);
  });

  it('toFieldRequests keeps deleted fields with their original deletedAt', () => {
    expect(toFieldRequests([draftOf(deleted)], '2026-05-01T00:00:00.000Z')).toEqual([
      {
        name: 'pin',
        values: [{ value: 'alice', createdAt: T1 }],
        createdAt: T1,
        deletedAt: '2026-02-01T00:00:00Z',
      },
    ]);
  });

  it('toFieldRequests stamps newly deleted fields and sends their saved name and values', () => {
    const now = '2026-05-01T00:00:00.000Z';
    expect(toFieldRequests([draftOf(secret, { deleted: true, value: 'x' })], now)).toEqual([
      {
        name: 'password',
        values: [{ value: 'hunter2', createdAt: T1 }],
        createdAt: T1,
        deletedAt: now,
      },
    ]);
  });

  it('toFieldRequests sends restored fields as active', () => {
    expect(toFieldRequests([draftOf(deleted, { deleted: false })])).toEqual([
      { name: 'pin', values: [{ value: 'alice', createdAt: T1 }], createdAt: T1, deletedAt: null },
    ]);
  });
});
