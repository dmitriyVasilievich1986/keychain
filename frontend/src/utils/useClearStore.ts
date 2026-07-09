/**
 * This file contains the useClearStore hook.
 * It is used to clear all stores when the user logs out or the session expires.
 */

import Cookies from 'js-cookie';

import { usePasswordsStore } from '@store/passwords';
import { useUserStore } from '@store/user';

/**
 * Hook that provides a helper for resetting all client-side state.
 *
 * Useful during logout or session expiry to ensure no user data lingers.
 *
 * @returns An object exposing `clearAllStores`.
 */
export function useClearStore() {
  const userStore = useUserStore();
  const passwordsStore = usePasswordsStore();

  /**
   * Clears all persisted authentication and application state.
   *
   * Removes the `accessToken` cookie and resets the user and passwords stores.
   */
  function clearAllStores() {
    Cookies.remove('accessToken');
    userStore.clearStore();
    passwordsStore.clearStore();
  }

  return { clearAllStores };
}
