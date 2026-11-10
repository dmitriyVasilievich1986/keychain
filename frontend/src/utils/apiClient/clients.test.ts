/**
 * Tests for the resource API client hooks (auth, user, password): request shapes, returned
 * data, and store side effects. The network layer is replaced with spies on the shared client.
 */

import { act, renderHook } from '@testing-library/react';
import axios from 'axios';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { useUserStore } from '@store/user';

import { useAuthAPIClient } from './auth';
import { apiClientInstance } from './base';
import { usePasswordAPIClient } from './password';
import { useUserAPIClient } from './user';

/** Shapes a value like an Axios response so spied methods can resolve with it. */
function response<T>(data: T) {
  return { data, status: 200, statusText: 'OK', headers: {}, config: {} } as never;
}

const user = { id: 'u-1', name: 'Alice', createdAt: '2026-01-01T00:00:00Z' };

const PASSWORD_ID = '5f1d7c2e-8b1a-4c3d-9e2f-1a2b3c4d5e6f';

const field = {
  name: 'username',
  position: 0,
  values: [{ value: 'alice', createdAt: '2026-01-01T00:00:00Z' }],
  createdAt: '2026-01-01T00:00:00Z',
  updatedAt: '2026-01-01T00:00:00Z',
  deletedAt: null,
};

const password = {
  id: PASSWORD_ID,
  name: 'GitHub',
  createdAt: '2026-01-01T00:00:00Z',
  updatedAt: '2026-01-01T00:00:00Z',
  imageUrl: 'github.png',
  userId: 'u-1',
  fields: [field],
};

const fieldsRequest = [{ name: 'username', values: [{ value: 'alice' }] }];

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

describe('usePasswordAPIClient', () => {
  it('getPassword fetches a password by id', async () => {
    const get = vi.spyOn(apiClientInstance, 'get').mockResolvedValue(response(password));
    const { result } = renderHook(() => usePasswordAPIClient());

    await expect(result.current.getPassword(PASSWORD_ID)).resolves.toEqual(password);

    expect(get).toHaveBeenCalledWith(
      expect.stringMatching(new RegExp(`/api/v1/password/${PASSWORD_ID}$`))
    );
  });

  it('getPasswords sends paging, sorting and JSON-encoded filters', async () => {
    const page = {
      data: [{ id: PASSWORD_ID, name: 'GitHub', imageUrl: 'github.png' }],
      metadata: { total: 1, offset: 0, limit: 10, sortBy: 'name', sortOrder: 'asc', filters: null },
    };
    const get = vi.spyOn(apiClientInstance, 'get').mockResolvedValue(response(page));
    const filters = [{ column: 'name', operator: 'eq', value: 'GitHub' }];
    const { result } = renderHook(() => usePasswordAPIClient());

    await expect(result.current.getPasswords(10, 0, 'name', 'asc', filters, true)).resolves.toEqual(
      page
    );

    expect(get).toHaveBeenCalledWith(expect.stringMatching(/\/api\/v1\/password$/), {
      params: {
        limit: 10,
        offset: 0,
        sortBy: 'name',
        sortOrder: 'asc',
        filters: JSON.stringify(filters),
        showDeleted: true,
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
        showDeleted: undefined,
      },
    });
  });

  it('postPassword creates a password and returns it', async () => {
    const request = { name: 'GitHub', imageUrl: 'github.png', fields: fieldsRequest };
    const post = vi.spyOn(apiClientInstance, 'post').mockResolvedValue(response(password));
    const { result } = renderHook(() => usePasswordAPIClient());

    let data: unknown;
    await act(async () => {
      data = await result.current.postPassword(request);
    });

    expect(data).toEqual(password);
    expect(post).toHaveBeenCalledWith(expect.stringMatching(/\/api\/v1\/password$/), request);
  });

  it('putPassword replaces the password by id and returns it', async () => {
    const request = { name: 'GitHub', imageUrl: null, fields: fieldsRequest };
    const put = vi.spyOn(apiClientInstance, 'put').mockResolvedValue(response(password));
    const { result } = renderHook(() => usePasswordAPIClient());

    let data: unknown;
    await act(async () => {
      data = await result.current.putPassword(PASSWORD_ID, request);
    });

    expect(data).toEqual(password);
    expect(put).toHaveBeenCalledWith(
      expect.stringMatching(new RegExp(`/api/v1/password/${PASSWORD_ID}$`)),
      request
    );
  });

  it('patchPassword sends only the given properties and returns the password', async () => {
    const request = { fields: fieldsRequest };
    const patch = vi.spyOn(apiClientInstance, 'patch').mockResolvedValue(response(password));
    const { result } = renderHook(() => usePasswordAPIClient());

    let data: unknown;
    await act(async () => {
      data = await result.current.patchPassword(PASSWORD_ID, request);
    });

    expect(data).toEqual(password);
    expect(patch).toHaveBeenCalledWith(
      expect.stringMatching(new RegExp(`/api/v1/password/${PASSWORD_ID}$`)),
      request
    );
  });

  it('deletePassword deletes the password by id', async () => {
    const del = vi.spyOn(apiClientInstance, 'delete').mockResolvedValue(response(undefined));
    const { result } = renderHook(() => usePasswordAPIClient());

    await act(async () => {
      await result.current.deletePassword(PASSWORD_ID);
    });

    expect(del).toHaveBeenCalledWith(
      expect.stringMatching(new RegExp(`/api/v1/password/${PASSWORD_ID}$`))
    );
  });
});
