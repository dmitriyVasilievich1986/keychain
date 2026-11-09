/**
 * Tests for the resource API client hooks (auth, user, field, password): request shapes, returned
 * data, and store side effects. The network layer is replaced with spies on the shared client.
 */

import { act, renderHook } from '@testing-library/react';
import axios from 'axios';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { useUserStore } from '@store/user';

import { useAuthAPIClient } from './auth';
import { apiClientInstance } from './base';
import { useFieldAPIClient } from './field';
import { usePasswordAPIClient } from './password';
import { useUserAPIClient } from './user';

/** Shapes a value like an Axios response so spied methods can resolve with it. */
function response<T>(data: T) {
  return { data, status: 200, statusText: 'OK', headers: {}, config: {} } as never;
}

const user = { id: 'u-1', name: 'Alice', createdAt: '2026-01-01T00:00:00Z' };

const field = {
  id: 10,
  name: 'username',
  isDeleted: false,
  valueDecrypted: 'alice',
  createdAt: '2026-01-01T00:00:00Z',
};

const password = {
  id: 1,
  name: 'GitHub',
  createdAt: '2026-01-01T00:00:00Z',
  imageUrl: 'github.png',
  fields: [field],
};

beforeEach(() => {
  useUserStore.setState({ user: null, isLoading: false });
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('useAuthAPIClient', () => {
  it('posts credentials to the login endpoint without the auth-guarded client', async () => {
    const payload = { accessToken: 'token-123', expiresAt: '2099-01-01T00:00:00Z' };
    const post = vi.spyOn(axios, 'post').mockResolvedValue(response(payload));
    const guardedPost = vi.spyOn(apiClientInstance, 'post');
    const { result } = renderHook(() => useAuthAPIClient());

    let data: unknown;
    await act(async () => {
      data = await result.current.login('alice', 'secret');
    });

    expect(data).toEqual(payload);
    expect(post).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/v1\/user\/login$/),
      { username: 'alice', password: 'secret' },
      { headers: { 'Content-Type': 'application/json' } }
    );
    expect(guardedPost).not.toHaveBeenCalled();
  });
});

describe('useUserAPIClient', () => {
  it('getUser fetches the current user without touching the store', async () => {
    const get = vi.spyOn(apiClientInstance, 'get').mockResolvedValue(response(user));
    const { result } = renderHook(() => useUserAPIClient());

    await expect(result.current.getUser()).resolves.toEqual(user);

    expect(get).toHaveBeenCalledWith(expect.stringMatching(/\/api\/v1\/user\/me$/));
    expect(useUserStore.getState().user).toBeNull();
  });

  it('putUser sends the update and writes the returned user to the store', async () => {
    const request = { name: 'Alice' };
    const put = vi.spyOn(apiClientInstance, 'put').mockResolvedValue(response(user));
    const { result } = renderHook(() => useUserAPIClient());

    await act(async () => {
      await result.current.putUser(request);
    });

    expect(put).toHaveBeenCalledWith(expect.stringMatching(/\/api\/v1\/user$/), request);
    expect(useUserStore.getState().user).toEqual(user);
  });
});

describe('useFieldAPIClient', () => {
  it('postField creates a field and returns it', async () => {
    const request = { passwordId: 1, name: 'username', value: 'alice' };
    const post = vi.spyOn(apiClientInstance, 'post').mockResolvedValue(response(field));
    const { result } = renderHook(() => useFieldAPIClient());

    let data: unknown;
    await act(async () => {
      data = await result.current.postField(request);
    });

    expect(data).toEqual(field);
    expect(post).toHaveBeenCalledWith(expect.stringMatching(/\/api\/v1\/field$/), request);
  });

  it('putField updates the field by id and returns it', async () => {
    const put = vi.spyOn(apiClientInstance, 'put').mockResolvedValue(response(field));
    const { result } = renderHook(() => useFieldAPIClient());

    let data: unknown;
    await act(async () => {
      data = await result.current.putField(10, { value: 'bob' });
    });

    expect(data).toEqual(field);
    expect(put).toHaveBeenCalledWith(expect.stringMatching(/\/api\/v1\/field\/10$/), {
      value: 'bob',
    });
  });
});

describe('usePasswordAPIClient', () => {
  it('getPassword fetches a password by id', async () => {
    const get = vi.spyOn(apiClientInstance, 'get').mockResolvedValue(response(password));
    const { result } = renderHook(() => usePasswordAPIClient());

    await expect(result.current.getPassword(1)).resolves.toEqual(password);

    expect(get).toHaveBeenCalledWith(expect.stringMatching(/\/api\/v1\/password\/1$/));
  });

  it('getPasswords sends paging, sorting and JSON-encoded filters', async () => {
    const page = {
      data: [{ id: 1, name: 'GitHub', imageUrl: 'github.png' }],
      metadata: { total: 1, offset: 0, limit: 10, sort_by: 'name', sort_order: 'asc' },
    };
    const get = vi.spyOn(apiClientInstance, 'get').mockResolvedValue(response(page));
    const filters = [{ column: 'name', operator: 'contains', value: 'Git' }];
    const { result } = renderHook(() => usePasswordAPIClient());

    await expect(result.current.getPasswords(10, 0, 'name', 'asc', filters)).resolves.toEqual(page);

    expect(get).toHaveBeenCalledWith(expect.stringMatching(/\/api\/v1\/password$/), {
      params: {
        limit: 10,
        offset: 0,
        sortBy: 'name',
        sortOrder: 'asc',
        filters: JSON.stringify(filters),
      },
    });
  });

  it('getPasswords omits filters when none are given', async () => {
    const get = vi
      .spyOn(apiClientInstance, 'get')
      .mockResolvedValue(response({ data: [], metadata: {} }));
    const { result } = renderHook(() => usePasswordAPIClient());

    await result.current.getPasswords();

    expect(get).toHaveBeenCalledWith(expect.any(String), {
      params: {
        limit: undefined,
        offset: undefined,
        sortBy: undefined,
        sortOrder: undefined,
        filters: undefined,
      },
    });
  });

  it('postPassword creates a password and returns it', async () => {
    const request = { name: 'GitHub', imageUrl: 'github.png' };
    const post = vi.spyOn(apiClientInstance, 'post').mockResolvedValue(response(password));
    const { result } = renderHook(() => usePasswordAPIClient());

    let data: unknown;
    await act(async () => {
      data = await result.current.postPassword(request);
    });

    expect(data).toEqual(password);
    expect(post).toHaveBeenCalledWith(expect.stringMatching(/\/api\/v1\/password$/), request);
  });
});
