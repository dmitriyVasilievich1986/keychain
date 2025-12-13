import axios from 'axios';
import { useCallback } from 'react';

import { useUserStore } from '@store/user';

export const useApiGet = () => {
  const { setIsLoading, accessToken } = useUserStore();

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
      } finally {
        setIsLoading(false);
      }
    },
    [accessToken, setIsLoading]
  );
};

export const useApiPut = () => {
  const { setIsLoading, accessToken } = useUserStore();

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
      } finally {
        setIsLoading(false);
      }
    },
    [accessToken, setIsLoading]
  );
};

export const useApiPost = () => {
  const { setIsLoading, accessToken } = useUserStore();

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
      } finally {
        setIsLoading(false);
      }
    },
    [accessToken, setIsLoading]
  );
};

export const useApiClient = () => {
  return {
    apiGet: useApiGet(),
    apiPut: useApiPut(),
    apiPost: useApiPost(),
  };
};
