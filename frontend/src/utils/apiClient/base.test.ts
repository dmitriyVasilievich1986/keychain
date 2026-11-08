/**
 * Tests for the shared API client: auth interceptors and the loading wrapper.
 */

import { act, renderHook } from '@testing-library/react';
import { AxiosError, AxiosHeaders, type InternalAxiosRequestConfig } from 'axios';
import Cookies from 'js-cookie';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { useUserStore } from '@store/user';

import { apiClientInstance, useApiClientWrapper } from './base';

/**
 * Replaces the network layer of `apiClientInstance` so requests resolve (or fail) with the given
 * status without leaving the test. Returns the adapter mock to inspect the outgoing config.
 */
function mockAdapter(status = 200, data: unknown = { ok: true }) {
  const adapter = vi.fn(async (config: InternalAxiosRequestConfig) => {
    const response = { data, status, statusText: '', headers: {}, config };
    if (status >= 400) {
      throw new AxiosError('Request failed', 'ERR_BAD_RESPONSE', config, null, response);
    }
    return response;
  });
  apiClientInstance.defaults.adapter = adapter;
  return adapter;
}

/** jsdom cannot navigate, so stub `window.location` to observe redirects. */
function stubLocation(pathname: string) {
  const location = { pathname, href: `http://localhost${pathname}` };
  vi.stubGlobal('location', location);
  return location;
}

describe('apiClientInstance', () => {
  const originalAdapter = apiClientInstance.defaults.adapter;

  afterEach(() => {
    apiClientInstance.defaults.adapter = originalAdapter;
    Cookies.remove('accessToken');
    vi.unstubAllGlobals();
  });

  it('sends the access token as a bearer Authorization header', async () => {
    Cookies.set('accessToken', 'token-123');
    const adapter = mockAdapter();

    const response = await apiClientInstance.get('/api/v1/user/me');

    expect(response.data).toEqual({ ok: true });
    const headers = adapter.mock.calls[0][0].headers as AxiosHeaders;
    expect(headers.get('Authorization')).toBe('Bearer token-123');
  });

  it('redirects to login and aborts the request when the cookie is missing', async () => {
    const location = stubLocation('/password/7');
    const adapter = mockAdapter();

    await expect(apiClientInstance.get('/api/v1/password/7')).rejects.toThrow('Unauthorized');

    expect(adapter).not.toHaveBeenCalled();
    expect(location.href).toBe('/login?redirectTo=%2Fpassword%2F7');
  });

  it('redirects to login on a 401 response and still rejects', async () => {
    Cookies.set('accessToken', 'expired');
    const location = stubLocation('/profile');
    mockAdapter(401);

    await expect(apiClientInstance.get('/api/v1/user/me')).rejects.toBeInstanceOf(AxiosError);

    expect(location.href).toBe('/login?redirectTo=%2Fprofile');
  });

  it('does not redirect on a 401 while already on the login page', async () => {
    Cookies.set('accessToken', 'expired');
    const location = stubLocation('/login');
    mockAdapter(401);

    await expect(apiClientInstance.get('/api/v1/user/me')).rejects.toBeInstanceOf(AxiosError);

    expect(location.href).toBe('http://localhost/login');
  });

  it('does not redirect on other error statuses', async () => {
    Cookies.set('accessToken', 'token-123');
    const location = stubLocation('/password');
    mockAdapter(500);

    await expect(apiClientInstance.get('/api/v1/password')).rejects.toBeInstanceOf(AxiosError);

    expect(location.href).toBe('http://localhost/password');
  });
});

describe('useApiClientWrapper', () => {
  beforeEach(() => {
    useUserStore.setState({ isLoading: false });
  });

  it('sets the loading flag while the call runs and returns its result', async () => {
    const { result } = renderHook(() => useApiClientWrapper());
    let loadingDuringCall: boolean | undefined;

    let value: string | undefined;
    await act(async () => {
      value = await result.current.wrapper(async () => {
        loadingDuringCall = useUserStore.getState().isLoading;
        return 'done';
      });
    });

    expect(value).toBe('done');
    expect(loadingDuringCall).toBe(true);
    expect(useUserStore.getState().isLoading).toBe(false);
  });

  it('logs and rethrows errors, then clears the loading flag', async () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    const error = new Error('boom');
    const { result } = renderHook(() => useApiClientWrapper());

    await act(async () => {
      await expect(result.current.wrapper(() => Promise.reject(error))).rejects.toBe(error);
    });

    expect(consoleError).toHaveBeenCalledWith('Error:', error);
    expect(useUserStore.getState().isLoading).toBe(false);
    consoleError.mockRestore();
  });
});
