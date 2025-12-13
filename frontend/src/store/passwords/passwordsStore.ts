import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { Password, PasswordStore, PasswordSimple } from './types';

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
  }))
);
