import { useEffect } from 'react';
import { useNavigate } from 'react-router';

import { usePasswordsStore } from '@store/passwords';
import { useUserStore } from '@store/user';

export function Logout() {
  const { clearStore } = useUserStore();
  const { clearStore: clearPasswordStore } = usePasswordsStore();
  const navigate = useNavigate();

  useEffect(() => {
    clearStore();
    clearPasswordStore();
    navigate('/login');
  }, [navigate, clearStore, clearPasswordStore]);

  return null;
}
