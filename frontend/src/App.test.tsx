/**
 * Tests for App routing: lazy pages, redirects, and the auth guard on protected routes.
 */

import { cleanup, render, screen } from '@testing-library/react';
import Cookies from 'js-cookie';
import { MemoryRouter } from 'react-router';
import { afterEach, describe, expect, it, vi } from 'vite-plus/test';

import { usePasswordsStore } from '@store/passwords';
import { useUserStore } from '@store/user';

import App from './App';

vi.mock('@components/navbar', () => ({ Navbar: () => <nav>navbar</nav> }));
vi.mock('@pages/login', () => ({ Login: () => <div>login page</div> }));
vi.mock('@pages/password', () => ({ Password: () => <div>password page</div> }));
vi.mock('@pages/createPassword', () => ({
  CreatePassword: () => <div>create password page</div>,
}));
vi.mock('@pages/profile', () => ({ Profile: () => <div>profile page</div> }));

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>
  );
}

describe('App', () => {
  afterEach(() => {
    cleanup();
    Cookies.remove('accessToken');
  });

  it('always renders the navbar', async () => {
    renderAt('/login');

    expect(screen.getByText('navbar')).toBeInTheDocument();
    expect(await screen.findByText('login page')).toBeInTheDocument();
  });

  describe('with a session', () => {
    it.each([
      ['/', 'password page'],
      ['/password', 'password page'],
      ['/password/7', 'password page'],
      ['/password/create', 'create password page'],
      ['/profile', 'profile page'],
      ['/does-not-exist', 'password page'],
    ])('renders %s as the %s', async (path, page) => {
      Cookies.set('accessToken', 'token-123');

      renderAt(path);

      expect(await screen.findByText(page)).toBeInTheDocument();
    });
  });

  describe('without a session', () => {
    it.each(['/password', '/password/7', '/password/create', '/profile'])(
      'redirects %s to the login page',
      async (path) => {
        renderAt(path);

        expect(await screen.findByText('login page')).toBeInTheDocument();
      }
    );

    // Regression: ProtectedRoute used to clear the stores during render, which re-rendered it in
    // a loop until React aborted with "Maximum update depth exceeded".
    it('clears the stores without a render loop', async () => {
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
      const reported: unknown[] = [];
      const onError = (event: ErrorEvent) => reported.push(event.error);
      window.addEventListener('error', onError);
      useUserStore.setState({
        user: { id: 'u-1', name: 'Alice', createdAt: '2026-01-01T00:00:00Z' },
      });
      usePasswordsStore.setState({
        passwords: [{ id: 'p-1', name: 'GitHub', imageUrl: 'github.png' }],
      });

      try {
        renderAt('/password');

        expect(await screen.findByText('login page')).toBeInTheDocument();
        expect(useUserStore.getState().user).toBeNull();
        expect(usePasswordsStore.getState().passwords).toEqual([]);
        expect(consoleError).not.toHaveBeenCalled();
        expect(reported).toEqual([]);
      } finally {
        window.removeEventListener('error', onError);
        consoleError.mockRestore();
      }
    });
  });
});
