/**
 * This file contains the ProtectedRoute component.
 * It is used to protect routes that require authentication.
 */

import Cookies from 'js-cookie';
import { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router';

import { useClearStore } from '@utils/useClearStore';

/**
 * Guards routes that require authentication.
 *
 * If no `accessToken` cookie is present, it clears all persisted stores and
 * redirects to the login page, preserving the originally requested path and
 * query string via a `redirectTo` param so the user can be sent back after
 * logging in. Otherwise it renders the protected `children`.
 *
 * @param children - The protected content to render when authenticated.
 */
export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const accessToken = Cookies.get('accessToken');
  const { clearAllStores } = useClearStore();

  // Reset the stores after render, not during it: this component subscribes to them, so clearing
  // them while rendering re-renders it and clears them again, until React aborts the loop.
  useEffect(() => {
    if (!accessToken) {
      clearAllStores();
    }
  }, [accessToken]);

  if (!accessToken) {
    const redirectTo = encodeURIComponent(`${location.pathname}${location.search}`);
    return <Navigate to={`/login?redirectTo=${redirectTo}`} replace />;
  }

  return <>{children}</>;
}
