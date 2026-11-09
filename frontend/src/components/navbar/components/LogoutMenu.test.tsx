/**
 * Tests for LogoutMenu: user hydration from the API and menu navigation.
 */

import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Cookies from 'js-cookie';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { useUserStore } from '@store/user';
import { version } from '@utils/application-version.json';

import { LogoutMenu } from './LogoutMenu';

const { getUser, navigate } = vi.hoisted(() => ({
  getUser: vi.fn(),
  navigate: vi.fn(),
}));

vi.mock('@utils/apiClient/user', () => ({
  useUserAPIClient: () => ({ getUser }),
}));

vi.mock('react-router', async () => {
  const actual = await vi.importActual<typeof import('react-router')>('react-router');
  return { ...actual, useNavigate: () => navigate };
});

const user = { id: 'u-1', name: 'Alice', createdAt: '2026-01-01T00:00:00Z' };

// jsdom's getComputedStyle crashes on MUI's open menu popover, so role queries made while the
// menu is open skip the accessibility check (`hidden: true`).
const HIDDEN = { hidden: true } as const;

async function openMenu() {
  const events = userEvent.setup();
  await events.click(screen.getByRole('button', { name: 'Alice' }));
  return events;
}

describe('LogoutMenu', () => {
  beforeEach(() => {
    getUser.mockReset();
    navigate.mockReset();
    useUserStore.setState({ user: null });
  });

  afterEach(() => {
    cleanup();
    Cookies.remove('accessToken');
  });

  it('renders nothing and fetches nothing without a session', () => {
    const { container } = render(<LogoutMenu />);

    expect(container).toBeEmptyDOMElement();
    expect(getUser).not.toHaveBeenCalled();
  });

  it('loads the user when a session cookie exists but the store is empty', async () => {
    Cookies.set('accessToken', 'token-123');
    getUser.mockResolvedValue(user);

    render(<LogoutMenu />);

    expect(await screen.findByRole('button', { name: 'Alice' })).toBeInTheDocument();
    expect(getUser).toHaveBeenCalledTimes(1);
    expect(useUserStore.getState().user).toEqual(user);
  });

  it('does not refetch when the user is already loaded', () => {
    Cookies.set('accessToken', 'token-123');
    useUserStore.setState({ user });

    render(<LogoutMenu />);

    expect(screen.getByRole('button', { name: 'Alice' })).toBeInTheDocument();
    expect(getUser).not.toHaveBeenCalled();
  });

  it('opens a menu with the application version', async () => {
    useUserStore.setState({ user });
    render(<LogoutMenu />);

    await openMenu();

    expect(screen.getByRole('menu', HIDDEN)).toBeInTheDocument();
    expect(screen.getByText(`version: ${version}`)).toBeInTheDocument();
    expect(screen.getByRole('button', { ...HIDDEN, name: 'Alice' })).toHaveAttribute(
      'aria-expanded',
      'true'
    );
  });

  it.each([
    ['Profile', '/profile'],
    ['Passwords', '/passwords'],
    ['Logout', '/login'],
  ])('navigates from the %s item and closes the menu', async (item, path) => {
    useUserStore.setState({ user });
    render(<LogoutMenu />);

    const events = await openMenu();
    await events.click(screen.getByRole('menuitem', { ...HIDDEN, name: item }));

    expect(navigate).toHaveBeenCalledWith(path);
    await waitFor(() => {
      expect(screen.queryByRole('menu', HIDDEN)).not.toBeInTheDocument();
    });
  });
});
