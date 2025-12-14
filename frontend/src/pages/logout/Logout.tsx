import { useEffect } from 'react';
import { useNavigate } from 'react-router';

import { useUserStore } from '@store/user';

export function Logout() {
  const { removeAccessToken } = useUserStore();
  const navigate = useNavigate();

  useEffect(() => {
    removeAccessToken();
    navigate('/login');
  }, [navigate, removeAccessToken]);

  return null;
}
