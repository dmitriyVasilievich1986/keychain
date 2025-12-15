import axios, { AxiosError } from 'axios';
import { useCallback } from 'react';

import { usePasswordsStore } from '@store/passwords';
import { useUserStore } from '@store/user';

export const useApiGet = () => {
  const { setIsLoading, accessToken, clearStore } = useUserStore();
  const { clearStore: clearPasswordStore } = usePasswordsStore();

  return useCallback(
    async <T>(url: string): Promise<T> => {
      setIsLoading(true);

      try {
        const response = await axios.get(`${import.meta.env.VITE_API_HOST}${url}`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        return response.data;
      } catch (error) {
        if (error instanceof AxiosError && error.response?.status === 401) {
          clearStore();
          clearPasswordStore();
        } else {
          console.error(error);
        }
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
    [accessToken, setIsLoading, clearStore, clearPasswordStore]
  );
};

export const useApiPut = () => {
  const { setIsLoading, accessToken, clearStore } = useUserStore();
  const { clearStore: clearPasswordStore } = usePasswordsStore();

  return useCallback(
    async <D, T>(url: string, data: D): Promise<T> => {
      setIsLoading(true);

      try {
        const response = await axios.put(`${import.meta.env.VITE_API_HOST}${url}`, data, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        return response.data;
      } catch (error) {
        if (error instanceof AxiosError && error.response?.status === 401) {
          clearStore();
          clearPasswordStore();
        } else {
          console.error(error);
        }
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
    [accessToken, setIsLoading, clearStore, clearPasswordStore]
  );
};

export const useApiPost = () => {
  const { setIsLoading, accessToken, clearStore } = useUserStore();
  const { clearStore: clearPasswordStore } = usePasswordsStore();

  return useCallback(
    async <D, T>(url: string, data: D): Promise<T> => {
      setIsLoading(true);

      try {
        const response = await axios.post(`${import.meta.env.VITE_API_HOST}${url}`, data, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        return response.data;
      } catch (error) {
        if (error instanceof AxiosError && error.response?.status === 401) {
          clearStore();
          clearPasswordStore();
        } else {
          console.error(error);
        }
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
    [accessToken, setIsLoading, clearStore, clearPasswordStore]
  );
};

export const useApiClient = () => {
  return {
    apiGet: useApiGet(),
    apiPut: useApiPut(),
    apiPost: useApiPost(),
  };
};
