/**
 * Field REST API client hook: HTTP calls to `/api/v1/field` and syncing results into the field store.
 */

import { type PasswordField } from '@store/passwords';

import { apiClientInstance, useApiClientWrapper } from '../base';

import type { FieldPostRequest, FieldPutRequest } from './types';

/**
 * Hook that exposes field API functions wired to the global field store.
 *
 * @returns Object with `postField`, `putField` methods.
 */
export const useFieldAPIClient = () => {
  const { wrapper } = useApiClientWrapper();

  return {
    postField: async (request: FieldPostRequest): Promise<PasswordField> => {
      return wrapper(async () => {
        const response = await apiClientInstance.post<PasswordField>(`/api/v1/field`, request);
        return response.data;
      });
    },
    putField: async (id: number, request: FieldPutRequest): Promise<PasswordField> => {
      return wrapper(async () => {
        const response = await apiClientInstance.put<PasswordField>(`/api/v1/field/${id}`, request);
        return response.data;
      });
    },
  };
};
