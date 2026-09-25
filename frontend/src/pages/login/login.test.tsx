/**
 * Tests for the Login page: store reset on mount, redirect navigation, and form behavior.
 */

import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Cookies from 'js-cookie';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { Login } from './login';

const { clearAllStores, login, navigate, searchParamsRef } = vi.hoisted(() => ({
  clearAllStores: vi.fn(),
  login: vi.fn(),
  navigate: vi.fn(),
  searchParamsRef: { current: new URLSearchParams() },
}));

vi.mock('@utils/useClearStore', () => ({
  useClearStore: () => ({ clearAllStores }),
}));

vi.mock('@utils/apiClient/auth', () => ({
  useAuthAPIClient: () => ({ login }),
}));

vi.mock('react-router', async () => {
  const actual = await vi.importActual<typeof import('react-router')>('react-router');
  return {
    ...actual,
    useNavigate: () => navigate,
    useSearchParams: () => [searchParamsRef.current],
  };
});

vi.mock('js-cookie', () => ({
  default: {
    set: vi.fn(),
  },
}));

function getUsernameField() {
  return screen.getByRole('textbox', { name: 'Login' });
}

function getPasswordField() {
  return screen.getByLabelText('Password');
}

async function submitLogin(username: string, password: string) {
  const user = userEvent.setup();
  await user.type(getUsernameField(), username);
  await user.type(getPasswordField(), password);
  await user.click(screen.getByRole('button', { name: 'Login' }));
  return user;
}

describe('Login', () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    clearAllStores.mockClear();
    login.mockReset();
    navigate.mockReset();
    searchParamsRef.current = new URLSearchParams();
    vi.mocked(Cookies.set).mockClear();
  });

  it('calls clearAllStores on mount', () => {
    render(<Login />);

    expect(clearAllStores).toHaveBeenCalledTimes(1);
  });

  it('renders the login form', () => {
    render(<Login />);

    expect(getUsernameField()).toBeInTheDocument();
    expect(getPasswordField()).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Login' })).toBeInTheDocument();
    expect(screen.getByAltText('avatar')).toBeInTheDocument();
  });

  it('toggles password visibility', async () => {
    const user = userEvent.setup();
    render(<Login />);

    const passwordField = getPasswordField();
    expect(passwordField).toHaveAttribute('type', 'password');

    await user.click(screen.getByLabelText('Toggle password visibility'));
    expect(passwordField).toHaveAttribute('type', 'text');

    await user.click(screen.getByLabelText('Toggle password visibility'));
    expect(passwordField).toHaveAttribute('type', 'password');
  });

  it('navigates to redirectTo from the query string on successful login', async () => {
    searchParamsRef.current = new URLSearchParams('redirectTo=/passwords');
    login.mockResolvedValue({
      accessToken: 'token-123',
      expiresAt: '2099-01-01T00:00:00.000Z',
    });

    render(<Login />);
    await submitLogin('alice', 'secret');

    await waitFor(() => {
      expect(login).toHaveBeenCalledWith('alice', 'secret');
      expect(Cookies.set).toHaveBeenCalledWith(
        'accessToken',
        'token-123',
        expect.objectContaining({ expires: expect.any(Date) })
      );
      expect(navigate).toHaveBeenCalledWith('/passwords');
    });
  });

  it('navigates to / when redirectTo is not provided', async () => {
    login.mockResolvedValue({
      accessToken: 'token-123',
      expiresAt: '2099-01-01T00:00:00.000Z',
    });

    render(<Login />);
    await submitLogin('alice', 'secret');

    await waitFor(() => {
      expect(navigate).toHaveBeenCalledWith('/');
    });
  });

  it('shows a server error when login fails', async () => {
    login.mockRejectedValue({
      isAxiosError: true,
      response: { data: { detail: 'Invalid credentials' } },
    });

    render(<Login />);
    await submitLogin('alice', 'wrong');

    await waitFor(() => {
      expect(screen.getAllByText('Invalid credentials').length).toBeGreaterThan(0);
    });
    expect(navigate).not.toHaveBeenCalled();
  });

  it('clears the error when the user types again', async () => {
    login.mockRejectedValue({
      isAxiosError: true,
      response: { data: { detail: 'Invalid credentials' } },
    });

    const user = userEvent.setup();
    render(<Login />);
    await submitLogin('alice', 'wrong');

    await waitFor(() => {
      expect(screen.getAllByText('Invalid credentials').length).toBeGreaterThan(0);
    });

    await user.type(getUsernameField(), 'x');

    await waitFor(() => {
      expect(screen.queryByText('Invalid credentials')).not.toBeInTheDocument();
    });
  });

  it('shows a fallback error for non-axios failures', async () => {
    login.mockRejectedValue(new Error('network down'));

    render(<Login />);
    await submitLogin('alice', 'secret');

    await waitFor(() => {
      expect(screen.getAllByText('An unknown error occurred').length).toBeGreaterThan(0);
    });
  });
});
