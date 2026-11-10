/**
 * This file contains the passwords store.
 * It is used to store the passwords and the currently selected password.
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { Password, PasswordStore, PasswordSimple } from './types';

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
    removePassword: (id: string) =>
      set(
        (state) => ({ passwords: state.passwords.filter((password) => password.id !== id) }),
        undefined,
        'removePassword'
      ),
    /** Appends a new password to the list. */
    addPassword: (password: PasswordSimple) =>
      set((state) => ({ passwords: [...state.passwords, password] }), undefined, 'addPassword'),
    /**
     * Stores the API's updated password as the current one and syncs its `name`/`imageUrl` into
     * the matching list entry. Fields are taken as-is from the API response.
     */
    updatePassword: (password: Password) =>
      set(
        (state) => ({
          currentPassword: password,
          passwords: state.passwords.map((item) =>
            item.id === password.id
              ? { ...item, name: password.name, imageUrl: password.imageUrl }
              : item
          ),
        }),
        undefined,
        'updatePassword'
      ),
    /** Resets the store, clearing the list and the selected password. */
    clearStore: () => set({ passwords: [], currentPassword: null }, undefined, 'clearStore'),
  }))
);
