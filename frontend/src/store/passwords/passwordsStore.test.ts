/**
 * Tests for the passwords store: list management and current-password updates.
 */

import { beforeEach, describe, expect, it } from 'vite-plus/test';

import { usePasswordsStore } from './passwordsStore';

import type { Password, PasswordField, PasswordSimple } from './types';

const GITHUB_ID = '5f1d7c2e-8b1a-4c3d-9e2f-1a2b3c4d5e6f';
const GITLAB_ID = '8a2b3c4d-1e2f-4a5b-8c6d-7e8f9a0b1c2d';

const github: PasswordSimple = { id: GITHUB_ID, name: 'GitHub', imageUrl: 'github.png' };
const gitlab: PasswordSimple = { id: GITLAB_ID, name: 'GitLab', imageUrl: null };

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

function makePassword(overrides: Partial<Password> = {}): Password {
  return {
    id: GITHUB_ID,
    name: 'GitHub',
    createdAt: '2026-01-01T00:00:00Z',
    updatedAt: '2026-01-01T00:00:00Z',
    imageUrl: 'github.png',
    userId: 'u-1',
    fields: [],
    ...overrides,
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
    usePasswordsStore.getState().removePassword(GITHUB_ID);

    expect(usePasswordsStore.getState().passwords).toEqual([gitlab]);
  });

  it('sets and clears the current password', () => {
    const password = makePassword();

    usePasswordsStore.getState().setCurrentPassword(password);
    expect(usePasswordsStore.getState().currentPassword).toEqual(password);

    usePasswordsStore.getState().setCurrentPassword(null);
    expect(usePasswordsStore.getState().currentPassword).toBeNull();
  });

  it('updatePassword replaces the current password with the API response', () => {
    const before = makePassword({ fields: [makeField()] });
    const after = makePassword({
      updatedAt: '2026-02-01T00:00:00Z',
      fields: [
        makeField({
          values: [
            { value: 'alice', createdAt: '2026-01-01T00:00:00Z' },
            { value: 'bob', createdAt: '2026-02-01T00:00:00Z' },
          ],
          updatedAt: '2026-02-01T00:00:00Z',
        }),
        makeField({ name: 'password', position: 1 }),
      ],
    });
    usePasswordsStore.getState().setCurrentPassword(before);

    usePasswordsStore.getState().updatePassword(after);

    expect(usePasswordsStore.getState().currentPassword).toEqual(after);
  });

  it('updatePassword syncs name and imageUrl into the matching list entry only', () => {
    usePasswordsStore.getState().setPasswords([github, gitlab]);

    usePasswordsStore
      .getState()
      .updatePassword(makePassword({ name: 'GitHub Enterprise', imageUrl: null }));

    expect(usePasswordsStore.getState().passwords).toEqual([
      { id: GITHUB_ID, name: 'GitHub Enterprise', imageUrl: null },
      gitlab,
    ]);
  });

  it('updatePassword leaves the list untouched when the password is not in it', () => {
    usePasswordsStore.getState().setPasswords([gitlab]);

    usePasswordsStore.getState().updatePassword(makePassword());

    expect(usePasswordsStore.getState().passwords).toEqual([gitlab]);
    expect(usePasswordsStore.getState().currentPassword).toEqual(makePassword());
  });

  it('clearStore resets the list and the current password', () => {
    usePasswordsStore.getState().setPasswords([github]);
    usePasswordsStore.getState().setCurrentPassword(makePassword());

    usePasswordsStore.getState().clearStore();

    expect(usePasswordsStore.getState().passwords).toEqual([]);
    expect(usePasswordsStore.getState().currentPassword).toBeNull();
  });
});
