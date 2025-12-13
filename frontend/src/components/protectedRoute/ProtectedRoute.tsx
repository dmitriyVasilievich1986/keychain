import { Navigate } from 'react-router';

import { useUserStore } from '@store/user';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { accessToken } = useUserStore();

  if (!accessToken) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
