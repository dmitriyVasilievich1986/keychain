/**
 * Password REST API client hook: HTTP calls to `/api/v1/password`.
 *
 * Password fields have no endpoint of their own: they are created, changed and removed by sending
 * the password's full field list through `postPassword`, `putPassword` or `patchPassword`.
 */

import { type PasswordSimple, type Password } from '@store/passwords';

import { apiClientInstance, useApiClientWrapper } from '../base';
import { API_PREFIX } from '../constants';

import type { FilterType, PaginationMetadata } from '../types';
import type {
  PasswordPatchRequest,
  PasswordPostRequest,
  PasswordPutRequest,
  PasswordSortBy,
  PasswordSortOrder,
} from './types';

const PASSWORD_URL = `${API_PREFIX}/api/v1/password`;

/**
 * Hook that exposes password API functions. Mutating calls run inside the global loading wrapper.
 *
 * @returns Object with `getPassword`, `getPasswords`, `postPassword`, `putPassword`,
 * `patchPassword` and `deletePassword` methods.
 */
export const usePasswordAPIClient = () => {
  const { wrapper } = useApiClientWrapper();

  return {
    /**
     * Loads a single password, including its fields and their value history.
     *
     * @param id - Password UUID.
     * @returns Full password entity from the API.
     */
    getPassword: async (id: string): Promise<Password> => {
      const response = await apiClientInstance.get<Password>(`${PASSWORD_URL}/${id}`);
      return response.data;
    },
    /**
     * Loads a paginated list of the current user's passwords.
     *
     * @param limit - Page size (1–100; backend default 100).
     * @param offset - Number of items to skip (backend default 0).
     * @param sortBy - Column used for ordering results.
     * @param sortOrder - Sort direction.
     * @param filters - Filters to apply; sent JSON-encoded.
     * @param showDeleted - Whether to include passwords marked as deleted.
     * @returns Passwords for the requested page plus pagination metadata.
     */
    getPasswords: async (
      limit?: number,
      offset?: number,
      sortBy?: PasswordSortBy,
      sortOrder?: PasswordSortOrder,
      filters?: FilterType[],
      showDeleted?: boolean
    ): Promise<{ data: PasswordSimple[]; metadata: PaginationMetadata }> => {
      const response = await apiClientInstance.get<{
        data: PasswordSimple[];
        metadata: PaginationMetadata;
      }>(PASSWORD_URL, {
        params: {
          limit,
          offset,
          sortBy,
          sortOrder,
          filters: filters ? JSON.stringify(filters) : undefined,
          showDeleted,
        },
      });
      return response.data;
    },
    /**
     * Creates a password, optionally together with its fields.
     *
     * @param request - Payload for `POST /api/v1/password`.
     * @returns Created password entity.
     */
    postPassword: async (request: PasswordPostRequest): Promise<Password> => {
      return wrapper(async () => {
        const response = await apiClientInstance.post<Password>(PASSWORD_URL, request);
        return response.data;
      });
    },
    /**
     * Fully replaces a password, including its whole field list.
     *
     * @param id - Password UUID.
     * @param request - Payload for `PUT /api/v1/password/{id}`.
     * @returns Updated password entity.
     */
    putPassword: async (id: string, request: PasswordPutRequest): Promise<Password> => {
      return wrapper(async () => {
        const response = await apiClientInstance.put<Password>(`${PASSWORD_URL}/${id}`, request);
        return response.data;
      });
    },
    /**
     * Partially updates a password. Send `fields` to replace the field list (e.g. to add, edit or
     * remove a field).
     *
     * @param id - Password UUID.
     * @param request - Payload for `PATCH /api/v1/password/{id}`.
     * @returns Updated password entity.
     */
    patchPassword: async (id: string, request: PasswordPatchRequest): Promise<Password> => {
      return wrapper(async () => {
        const response = await apiClientInstance.patch<Password>(`${PASSWORD_URL}/${id}`, request);
        return response.data;
      });
    },
    /**
     * Marks a password as deleted (`DELETE /api/v1/password/{id}`, responds with 204).
     *
     * @param id - Password UUID.
     */
    deletePassword: async (id: string): Promise<void> => {
      return wrapper(async () => {
        await apiClientInstance.delete(`${PASSWORD_URL}/${id}`);
      });
    },
  };
};
