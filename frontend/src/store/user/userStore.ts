import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { User, UserStore } from './types';

export const useUserStore = create<UserStore>()(
  devtools((set) => ({
    user: null,
    accessToken: null,
    setUser: (user: User) => set({ user }, undefined, 'setUser'),
    setAccessToken: (accessToken: string) => set({ accessToken }, undefined, 'setAccessToken'),
  }))
);
