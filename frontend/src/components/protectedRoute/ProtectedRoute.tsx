import Cookies from 'js-cookie';
import { Navigate, useLocation } from 'react-router';
import { useClearStore } from '@utils/useClearStore';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const accessToken = Cookies.get('accessToken');
  const { clearAllStores } = useClearStore();

  if (!accessToken) {
    const redirectTo = encodeURIComponent(`${location.pathname}${location.search}`);
    clearAllStores();
    return <Navigate to={`/login?redirectTo=${redirectTo}`} replace />;
  }

  return <>{children}</>;
}
