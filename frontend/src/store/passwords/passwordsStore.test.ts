/**
 * Tests for the passwords store: list management and current-password field updates.
 */

import { beforeEach, describe, expect, it } from 'vite-plus/test';

import { usePasswordsStore } from './passwordsStore';

import type { Password, PasswordField, PasswordSimple } from './types';

const github: PasswordSimple = { id: 1, name: 'GitHub', imageUrl: 'github.png' };
const gitlab: PasswordSimple = { id: 2, name: 'GitLab', imageUrl: 'gitlab.png' };

function makeField(overrides: Partial<PasswordField> = {}): PasswordField {
  return {
    id: 10,
    name: 'username',
    isDeleted: false,
    valueDecrypted: 'alice',
    createdAt: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

function makePassword(fields: PasswordField[] = []): Password {
  return {
    id: 1,
    name: 'GitHub',
    createdAt: '2026-01-01T00:00:00Z',
    imageUrl: 'github.png',
    fields,
  };
}

describe('usePasswordsStore', () => {
  beforeEach(() => {
    usePasswordsStore.getState().clearStore();
  });

  it('starts empty', () => {
    expect(usePasswordsStore.getState().passwords).toEqual([]);
    expect(usePasswordsStore.getState().currentPassword).toBeNull();
  });

  it('replaces the password list', () => {
    usePasswordsStore.getState().setPasswords([github, gitlab]);

    expect(usePasswordsStore.getState().passwords).toEqual([github, gitlab]);
  });

  it('appends a password', () => {
    usePasswordsStore.getState().setPasswords([github]);
    usePasswordsStore.getState().addPassword(gitlab);

    expect(usePasswordsStore.getState().passwords).toEqual([github, gitlab]);
  });

  it('removes a password by id', () => {
    usePasswordsStore.getState().setPasswords([github, gitlab]);
    usePasswordsStore.getState().removePassword(1);

    expect(usePasswordsStore.getState().passwords).toEqual([gitlab]);
  });

  it('sets and clears the current password', () => {
    const password = makePassword();

    usePasswordsStore.getState().setCurrentPassword(password);
    expect(usePasswordsStore.getState().currentPassword).toEqual(password);

    usePasswordsStore.getState().setCurrentPassword(null);
    expect(usePasswordsStore.getState().currentPassword).toBeNull();
  });

  it('adds a field to the current password', () => {
    const existing = makeField({ id: 10 });
    const added = makeField({ id: 11, name: 'password', valueDecrypted: 'secret' });
    usePasswordsStore.getState().setCurrentPassword(makePassword([existing]));

    usePasswordsStore.getState().addField(added);

    expect(usePasswordsStore.getState().currentPassword?.fields).toEqual([existing, added]);
  });

  it('adds a field even when the current password has no fields loaded', () => {
    const added = makeField({ id: 11 });

    usePasswordsStore.getState().addField(added);

    expect(usePasswordsStore.getState().currentPassword?.fields).toEqual([added]);
  });

  it('updateField appends the new field and marks the old one as deleted', () => {
    const old = makeField({ id: 10, valueDecrypted: 'alice' });
    const untouched = makeField({ id: 12, name: 'email', valueDecrypted: 'a@example.com' });
    const replacement = makeField({ id: 13, valueDecrypted: 'bob' });
    usePasswordsStore.getState().setCurrentPassword(makePassword([old, untouched]));

    usePasswordsStore.getState().updateField(10, replacement);

    expect(usePasswordsStore.getState().currentPassword?.fields).toEqual([
      { ...old, isDeleted: true },
      untouched,
      replacement,
    ]);
  });

  it('clearStore resets the list and the current password', () => {
    usePasswordsStore.getState().setPasswords([github]);
    usePasswordsStore.getState().setCurrentPassword(makePassword());

    usePasswordsStore.getState().clearStore();

    expect(usePasswordsStore.getState().passwords).toEqual([]);
    expect(usePasswordsStore.getState().currentPassword).toBeNull();
  });
});
