/**
 * Tests for the user store: loading flag, user, and access-token cookie sync.
 */

import Cookies from 'js-cookie';
import { afterEach, beforeEach, describe, expect, it } from 'vite-plus/test';

import { useUserStore } from './userStore';

import type { User } from './types';

const user: User = { id: 'u-1', name: 'Alice', createdAt: '2026-01-01T00:00:00Z' };

describe('useUserStore', () => {
  beforeEach(() => {
    useUserStore.setState({ user: null, accessToken: null, isLoading: false });
  });

  afterEach(() => {
    Cookies.remove('accessToken');
  });

  it('starts signed out and not loading', () => {
    const state = useUserStore.getState();

    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
    expect(state.isLoading).toBe(false);
  });

  it('sets the loading flag', () => {
    useUserStore.getState().setIsLoading(true);
    expect(useUserStore.getState().isLoading).toBe(true);

    useUserStore.getState().setIsLoading(false);
    expect(useUserStore.getState().isLoading).toBe(false);
  });

  it('sets and clears the user', () => {
    useUserStore.getState().setUser(user);
    expect(useUserStore.getState().user).toEqual(user);

    useUserStore.getState().setUser(null);
    expect(useUserStore.getState().user).toBeNull();
  });

  it('persists the access token to the cookie', () => {
    useUserStore.getState().setAccessToken('token-123');

    expect(useUserStore.getState().accessToken).toBe('token-123');
    expect(Cookies.get('accessToken')).toBe('token-123');
  });

  it('clearStore resets the state and removes the cookie', () => {
    useUserStore.getState().setAccessToken('token-123');
    useUserStore.getState().setUser(user);

    useUserStore.getState().clearStore();

    expect(useUserStore.getState().user).toBeNull();
    expect(useUserStore.getState().accessToken).toBeNull();
    expect(Cookies.get('accessToken')).toBeUndefined();
  });
});
