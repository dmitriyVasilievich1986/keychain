import Cookies from 'js-cookie';
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { User, UserStore } from './types';

export const useUserStore = create<UserStore>()(
  devtools((set) => ({
    user: null,
    accessToken: Cookies.get('accessToken') || null,
    isLoading: false,
    setIsLoading: (isLoading: boolean) => set({ isLoading }, undefined, 'setIsLoading'),
    setUser: (user: User | null) => set({ user }, undefined, 'setUser'),
    removeAccessToken: () => {
      Cookies.remove('accessToken');
      set({ accessToken: null, user: null }, undefined, 'removeAccessToken');
    },
    setAccessToken: (accessToken: string) => {
      Cookies.set('accessToken', accessToken);
      set({ accessToken }, undefined, 'setAccessToken');
    },
  }))
);
