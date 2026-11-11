/**
 * Tests for useClearStore: logout/session-expiry reset of cookies and stores.
 */

import { act, renderHook } from '@testing-library/react';
import Cookies from 'js-cookie';
import { describe, expect, it } from 'vite-plus/test';

import { usePasswordsStore } from '@store/passwords';
import { useUserStore } from '@store/user';

import { useClearStore } from './useClearStore';

describe('useClearStore', () => {
  it('removes the access token cookie and resets both stores', () => {
    Cookies.set('accessToken', 'token-123');
    useUserStore.setState({
      accessToken: 'token-123',
      user: { id: 'u-1', name: 'Alice', createdAt: '2026-01-01T00:00:00Z' },
    });
    usePasswordsStore.setState({
      passwords: [{ id: 'p-1', name: 'GitHub', imageUrl: 'github.png' }],
      currentPassword: {
        id: 'p-1',
        name: 'GitHub',
        createdAt: '2026-01-01T00:00:00Z',
        updatedAt: '2026-01-01T00:00:00Z',
        imageUrl: 'github.png',
        userId: 'u-1',
        fields: [],
      },
    });

    const { result } = renderHook(() => useClearStore());
    act(() => result.current.clearAllStores());

    expect(Cookies.get('accessToken')).toBeUndefined();
    expect(useUserStore.getState().user).toBeNull();
    expect(useUserStore.getState().accessToken).toBeNull();
    expect(usePasswordsStore.getState().passwords).toEqual([]);
    expect(usePasswordsStore.getState().currentPassword).toBeNull();
  });
});
