import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { Password, PasswordStore, PasswordSimple, PasswordField } from './types';

export const usePasswordsStore = create<PasswordStore>()(
  devtools((set) => ({
    passwords: [],
    currentPassword: null,
    setPasswords: (passwords: PasswordSimple[]) => set({ passwords }, undefined, 'setPasswords'),
    setCurrentPassword: (password: Password | null) =>
      set({ currentPassword: password }, undefined, 'setCurrentPassword'),
    removePassword: (id: number) =>
      set(
        (state) => ({ passwords: state.passwords.filter((password) => password.id !== id) }),
        undefined,
        'removePassword'
      ),
    addPassword: (password: PasswordSimple) =>
      set((state) => ({ passwords: [...state.passwords, password] }), undefined, 'addPassword'),
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
    clearStore: () => set({ passwords: [], currentPassword: null }, undefined, 'clearStore'),
  }))
);
