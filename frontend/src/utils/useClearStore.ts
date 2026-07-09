import { useUserStore } from '@store/user';
import { usePasswordsStore } from '@store/passwords';
import Cookies from 'js-cookie';

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
