/**
 * Tests for PasswordsList: lazy loading on open, selection navigation, and the create button.
 */

import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { usePasswordsStore, type PasswordSimple } from '@store/passwords';
import { useUserStore } from '@store/user';

import PasswordsList from './PasswordsList';

const { getPasswords, navigate } = vi.hoisted(() => ({
  getPasswords: vi.fn(),
  navigate: vi.fn(),
}));

vi.mock('@utils/apiClient/password', () => ({
  usePasswordAPIClient: () => ({ getPasswords }),
}));

vi.mock('react-router', async () => {
  const actual = await vi.importActual<typeof import('react-router')>('react-router');
  return { ...actual, useNavigate: () => navigate };
});

const passwords: PasswordSimple[] = [
  { id: 'p-1', name: 'GitHub', imageUrl: 'github.png' },
  { id: 'p-2', name: 'GitLab', imageUrl: 'gitlab.png' },
];

// jsdom's getComputedStyle crashes on MUI's open listbox popper whenever an accessible name or
// visibility is computed, so elements inside it are found by text or label instead of role.
function getInput() {
  return screen.getByLabelText('Password');
}

describe('PasswordsList', () => {
  beforeEach(() => {
    getPasswords.mockReset();
    navigate.mockReset();
    usePasswordsStore.getState().clearStore();
    useUserStore.setState({ isLoading: false });
  });

  afterEach(() => {
    cleanup();
  });

  it('loads passwords the first time the list opens and shows them', async () => {
    getPasswords.mockResolvedValue({ data: passwords, metadata: {} });
    render(<PasswordsList />);

    await userEvent.click(getInput());

    expect(await screen.findByText('GitHub')).toBeInTheDocument();
    expect(screen.getByText('GitLab')).toBeInTheDocument();
    expect(getPasswords).toHaveBeenCalledTimes(1);
    expect(usePasswordsStore.getState().passwords).toEqual(passwords);
  });

  it('does not refetch when passwords are already loaded', async () => {
    usePasswordsStore.getState().setPasswords(passwords);
    render(<PasswordsList />);

    await userEvent.click(getInput());

    expect(screen.getByText('GitHub')).toBeInTheDocument();
    expect(getPasswords).not.toHaveBeenCalled();
  });

  it('logs and keeps the list empty when loading fails', async () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    const error = new Error('network down');
    getPasswords.mockRejectedValue(error);
    render(<PasswordsList />);

    await userEvent.click(getInput());

    await waitFor(() => {
      expect(consoleError).toHaveBeenCalledWith(error);
    });
    expect(usePasswordsStore.getState().passwords).toEqual([]);
    consoleError.mockRestore();
  });

  it('navigates to the selected password', async () => {
    usePasswordsStore.getState().setPasswords(passwords);
    const user = userEvent.setup();
    render(<PasswordsList />);

    await user.click(getInput());
    await user.click(screen.getByText('GitLab'));

    expect(navigate).toHaveBeenCalledWith('/password/p-2');
  });

  it('navigates back to the list when the selection is cleared', async () => {
    usePasswordsStore.setState({
      passwords,
      currentPassword: {
        ...passwords[0],
        createdAt: '2026-01-01T00:00:00Z',
        updatedAt: '2026-01-01T00:00:00Z',
        userId: 'u-1',
        fields: [],
      },
    });
    const user = userEvent.setup();
    render(<PasswordsList />);

    expect(getInput()).toHaveValue('GitHub');
    await user.click(screen.getByLabelText('Clear'));

    expect(navigate).toHaveBeenCalledWith('/password');
  });

  it('opens the create page from the floating button', async () => {
    render(<PasswordsList />);

    await userEvent.click(screen.getByRole('button', { name: 'edit' }));

    expect(navigate).toHaveBeenCalledWith('/password/create');
  });
});
