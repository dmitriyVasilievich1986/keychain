/**
 * This file contains the user store.
 * It is used to store the authenticated user and access token.
 */

import Cookies from 'js-cookie';
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { User, UserStore } from './types';

/**
 * Zustand store holding the authenticated user and access token.
 *
 * The access token is synced with the `accessToken` cookie so the session
 * survives page reloads. Wrapped in `devtools` for Redux DevTools inspection.
 */
export const useUserStore = create<UserStore>()(
  devtools((set) => ({
    user: null,
    accessToken: Cookies.get('accessToken') || null,
    isLoading: false,
    /** Sets the global loading flag. */
    setIsLoading: (isLoading: boolean) => set({ isLoading }, undefined, 'setIsLoading'),
    /** Sets the current user, or clears it when passed `null`. */
    setUser: (user: User | null) => set({ user }, undefined, 'setUser'),
    /** Resets the store and removes the `accessToken` cookie. */
    clearStore: () => {
      Cookies.remove('accessToken');
      set({ accessToken: null, user: null }, undefined, 'clearStore');
    },
    /** Persists the access token to a cookie and updates the store. */
    setAccessToken: (accessToken: string) => {
      Cookies.set('accessToken', accessToken);
      set({ accessToken }, undefined, 'setAccessToken');
    },
  }))
);
