/**
 * Tests for ProtectedRoute: renders children with a session, otherwise clears state and redirects
 * to login with the requested location preserved.
 */

import { cleanup, render, screen } from '@testing-library/react';
import Cookies from 'js-cookie';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { ProtectedRoute } from './ProtectedRoute';

const { clearAllStores } = vi.hoisted(() => ({ clearAllStores: vi.fn() }));

vi.mock('@utils/useClearStore', () => ({
  useClearStore: () => ({ clearAllStores }),
}));

function LoginPage() {
  const location = useLocation();
  return <div>login page {location.search}</div>;
}

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="*"
          element={
            <ProtectedRoute>
              <div>secret content</div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </MemoryRouter>
  );
}

describe('ProtectedRoute', () => {
  beforeEach(() => {
    clearAllStores.mockClear();
  });

  afterEach(() => {
    cleanup();
    Cookies.remove('accessToken');
  });

  it('renders children when an access token cookie is present', () => {
    Cookies.set('accessToken', 'token-123');

    renderAt('/password');

    expect(screen.getByText('secret content')).toBeInTheDocument();
    expect(clearAllStores).not.toHaveBeenCalled();
  });

  it('clears stores and redirects to login with path and query preserved', () => {
    renderAt('/password/7?tab=fields');

    expect(screen.queryByText('secret content')).not.toBeInTheDocument();
    expect(
      screen.getByText(`login page ?redirectTo=${encodeURIComponent('/password/7?tab=fields')}`)
    ).toBeInTheDocument();
    expect(clearAllStores).toHaveBeenCalled();
  });
});
