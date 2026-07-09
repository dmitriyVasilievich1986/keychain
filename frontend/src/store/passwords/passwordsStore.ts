/**
 * This file contains the passwords store.
 * It is used to store the passwords and the currently selected password.
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { Password, PasswordStore, PasswordSimple, PasswordField } from './types';

/**
 * Zustand store managing the list of passwords and the currently selected one.
 *
 * `passwords` holds the lightweight list view, while `currentPassword` holds
 * the full detail (including fields) for the entry being viewed or edited.
 * Wrapped in `devtools` for Redux DevTools inspection.
 */
export const usePasswordsStore = create<PasswordStore>()(
  devtools((set) => ({
    passwords: [],
    currentPassword: null,
    /** Replaces the entire list of passwords. */
    setPasswords: (passwords: PasswordSimple[]) => set({ passwords }, undefined, 'setPasswords'),
    /** Sets the currently selected password, or clears it when passed `null`. */
    setCurrentPassword: (password: Password | null) =>
      set({ currentPassword: password }, undefined, 'setCurrentPassword'),
    /** Removes the password with the given id from the list. */
    removePassword: (id: number) =>
      set(
        (state) => ({ passwords: state.passwords.filter((password) => password.id !== id) }),
        undefined,
        'removePassword'
      ),
    /** Appends a new password to the list. */
    addPassword: (password: PasswordSimple) =>
      set((state) => ({ passwords: [...state.passwords, password] }), undefined, 'addPassword'),
    /** Adds a field to the current password's list of fields. */
    addField: (field: PasswordField) =>
      set(
        (state) => ({
          currentPassword: {
            ...state.currentPassword,
            fields: [...(state.currentPassword?.fields || []), field],
          } as Password,
        }),
        undefined,
        'addField'
      ),
    /** Appends `field` and marks the field matching `id` as deleted. */
    updateField: (id: number, field: PasswordField) =>
      set(
        (state) => ({
          currentPassword: {
            ...state.currentPassword,
            fields:
              [...state.currentPassword!.fields, field].map((f) =>
                f.id === id ? { ...f, isDeleted: true } : f
              ) || [],
          } as Password,
        }),
        undefined,
        'updateField'
      ),
    /** Resets the store, clearing the list and the selected password. */
    clearStore: () => set({ passwords: [], currentPassword: null }, undefined, 'clearStore'),
  }))
);
