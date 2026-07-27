/**
 * Password REST API client hook: HTTP calls to `/api/v1/password` and syncing results into the password store.
 */

import { usePasswordsStore, type PasswordSimple, type Password } from '@store/passwords';

import { apiClientInstance, useApiClientWrapper } from '../base';

import type { FilterType, PaginationMetadata } from '../types';
import type { PasswordPostRequest } from './types';

/**
 * Hook that exposes password API functions wired to the global password store.
 *
 * @returns Object with `getPassword`, `getPasswords`, `postPassword`, and `deletePassword` methods.
 */
export const usePasswordAPIClient = () => {
  const { passwords, addPassword } = usePasswordsStore();
  const { wrapper } = useApiClientWrapper();

  return {
    /**
     * Loads a single password by id and sets it as the current password in the store.
     *
     * @param {number} id - Password primary key.
     * @returns {Promise<Password>} Full password entity from the API.
     */
    getPassword: async (id: number): Promise<Password> => {
      const response = await apiClientInstance.get<Password>(`/api/v1/password/${id}`);
      return response.data;
    },
    /**
     * Loads a paginated list of passwords and updates the store with items and total count.
     *
     * @param {number} [limit] - Page size passed as a query parameter.
     * @param {number} [offset] - Skip offset passed as a query parameter.
     * @param {string} [sortBy] - Field name used for ordering results.
     * @param {string} [sortOrder] - Sort direction (e.g. ascending or descending).
     * @param {FilterType[]} [filters] - Filters to apply to the query.
     * @returns {Promise<PasswordSimple[]>} Passwords for the requested page.
     */
    getPasswords: async (
      limit?: number,
      offset?: number,
      sortBy?: string,
      sortOrder?: string,
      filters?: FilterType[]
    ): Promise<{ data: PasswordSimple[]; metadata: PaginationMetadata }> => {
      const response = await apiClientInstance.get<{
        data: PasswordSimple[];
        metadata: PaginationMetadata;
      }>(`/api/v1/password`, {
        params: {
          limit,
          offset,
          sortBy,
          sortOrder,
          filters: filters ? JSON.stringify(filters) : undefined,
        },
      });
      return response.data;
    },
    /**
     * Creates a password and appends it to the in-memory list when the list is already loaded.
     *
     * @param {PasswordPostRequest} request - Payload for `POST /api/v1/password`.
     * @returns {Promise<Password>} Created password entity.
     */
    postPassword: async (request: PasswordPostRequest): Promise<Password> => {
      return wrapper(async () => {
        const response = await apiClientInstance.post<Password>(`/api/v1/password`, request);
        if (passwords !== null) {
          addPassword(response.data);
        }
        return response.data;
      });
    },
  };
};
