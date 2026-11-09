/**
 * Tests for PasswordCard: loading the routed password, the loading skeleton, and field grouping.
 */

import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { usePasswordsStore, type Password } from '@store/passwords';
import { useUserStore } from '@store/user';

import { PasswordCard } from './PasswordCard';

const { getPassword } = vi.hoisted(() => ({ getPassword: vi.fn() }));

vi.mock('@utils/apiClient/password', () => ({
  usePasswordAPIClient: () => ({ getPassword }),
}));

vi.mock('@utils/apiClient/field', () => ({
  useFieldAPIClient: () => ({ postField: vi.fn(), putField: vi.fn() }),
}));

const password: Password = {
  id: 7,
  name: 'GitHub',
  createdAt: '2026-01-01T00:00:00Z',
  imageUrl: 'github.png',
  fields: [
    {
      id: 1,
      name: 'username',
      isDeleted: false,
      valueDecrypted: 'alice',
      createdAt: '2026-01-01T00:00:00Z',
    },
    {
      id: 2,
      name: 'old password',
      isDeleted: true,
      valueDecrypted: 'hunter2',
      createdAt: '2026-01-01T00:00:00Z',
    },
  ],
};

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/password" element={<PasswordCard />} />
        <Route path="/password/:passwordId" element={<PasswordCard />} />
      </Routes>
    </MemoryRouter>
  );
}

describe('PasswordCard', () => {
  beforeEach(() => {
    getPassword.mockReset();
    usePasswordsStore.getState().clearStore();
    useUserStore.setState({ isLoading: false });
  });

  afterEach(() => {
    cleanup();
  });

  it('renders nothing and clears the selection without a password id', () => {
    usePasswordsStore.getState().setCurrentPassword(password);

    const { container } = renderAt('/password');

    expect(container).toBeEmptyDOMElement();
    expect(usePasswordsStore.getState().currentPassword).toBeNull();
    expect(getPassword).not.toHaveBeenCalled();
  });

  it('loads the routed password and shows its active fields', async () => {
    getPassword.mockResolvedValue(password);

    renderAt('/password/7');

    expect(await screen.findByRole('heading', { name: 'GitHub' })).toBeInTheDocument();
    expect(getPassword).toHaveBeenCalledWith(7);
    expect(usePasswordsStore.getState().currentPassword).toEqual(password);
    expect(screen.getByLabelText('username')).toHaveValue('alice');
    expect(screen.getByLabelText('New field name')).toBeInTheDocument();
  });

  it('lists deleted fields as read-only in the collapsed section', async () => {
    usePasswordsStore.getState().setCurrentPassword(password);
    renderAt('/password/7');

    const deleted = screen.getByLabelText('old password');
    expect(deleted).toBeDisabled();
    expect(deleted).not.toBeVisible();

    await userEvent.click(screen.getByRole('button', { name: 'Deleted Fields' }));

    await waitFor(() => {
      expect(deleted).toBeVisible();
    });
  });

  it('does not refetch the password that is already loaded', () => {
    usePasswordsStore.getState().setCurrentPassword(password);

    renderAt('/password/7');

    expect(screen.getByRole('heading', { name: 'GitHub' })).toBeInTheDocument();
    expect(getPassword).not.toHaveBeenCalled();
  });

  it('shows a skeleton while a request is in progress', () => {
    usePasswordsStore.getState().setCurrentPassword(password);
    useUserStore.setState({ isLoading: true });

    const { container } = renderAt('/password/7');

    expect(screen.queryByRole('heading', { name: 'GitHub' })).not.toBeInTheDocument();
    expect(container.querySelector('.MuiSkeleton-root')).toBeInTheDocument();
  });

  it('logs and renders nothing when loading fails', async () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    const error = new Error('not found');
    getPassword.mockRejectedValue(error);

    const { container } = renderAt('/password/404');

    await waitFor(() => {
      expect(consoleError).toHaveBeenCalledWith(error);
    });
    expect(container).toBeEmptyDOMElement();
    consoleError.mockRestore();
  });
});
