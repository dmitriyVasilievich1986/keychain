/**
 * Credential exchange helpers for `POST /api/login`.
 *
 * Uses a dedicated `axios.post` rather than `apiClientInstance`: the shared client requires an
 * `accessToken` cookie and would redirect to `/login` before an unauthenticated call could complete.
 */

import axios from 'axios';

import { useApiClientWrapper } from '../base';
import { API_PREFIX, API_BASE_URL } from '../constants';

import type { LoginResponse } from './types';

/**
 * Hook that exposes login behind the global loading wrapper from {@link useApiClientWrapper}.
 *
 * @returns An object whose `login` method posts credentials and resolves with JWT metadata.
 */
export const useAuthAPIClient = () => {
  const { wrapper } = useApiClientWrapper();
  return {
    /**
     * Sends credentials to `/api/login` and returns parsed JSON on success (errors propagate after
     * the wrapper logs and resets loading).
     *
     * @param username - Value passed to the backend login handler.
     * @param password - Plain-text secret; rely on HTTPS in deployment for transport protection.
     * @returns A promise that resolves with the login response payload (`access_token`, etc.).
     */
    login: async (username: string, password: string) => {
      return wrapper(async () => {
        const response = await axios.post<LoginResponse>(
          `${API_BASE_URL}${API_PREFIX}/api/v1/user/login`,
          {
            username,
            password,
          },
          {
            headers: {
              'Content-Type': 'application/json',
            },
          }
        );
        return response.data;
      });
    },
  };
};
