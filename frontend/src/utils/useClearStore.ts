import Cookies from 'js-cookie';

import { usePasswordsStore } from '@store/passwords';
import { useUserStore } from '@store/user';

export function useClearStore() {
  const userStore = useUserStore();
  const passwordsStore = usePasswordsStore();

  function clearAllStores() {
    Cookies.remove('accessToken');
    userStore.clearStore();
    passwordsStore.clearStore();
  }

  return { clearAllStores };
}
