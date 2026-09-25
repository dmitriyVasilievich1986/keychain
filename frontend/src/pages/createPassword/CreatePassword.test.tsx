/**
 * Tests for the CreatePassword page: form rendering, create success path, and errors.
 */

import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { CreatePassword } from './CreatePassword';

const { addPassword, setCurrentPassword, postPassword, navigate } = vi.hoisted(() => ({
  addPassword: vi.fn(),
  setCurrentPassword: vi.fn(),
  postPassword: vi.fn(),
  navigate: vi.fn(),
}));

vi.mock('@store/passwords', () => ({
  usePasswordsStore: () => ({ addPassword, setCurrentPassword }),
}));

vi.mock('@utils/apiClient/password', () => ({
  usePasswordAPIClient: () => ({ postPassword }),
}));

vi.mock('react-router', async () => {
  const actual = await vi.importActual<typeof import('react-router')>('react-router');
  return {
    ...actual,
    useNavigate: () => navigate,
  };
});

function getNameField() {
  return screen.getByLabelText('PasswordName');
}

function getImageUrlField() {
  return screen.getByLabelText('Password Image URL');
}

async function submitCreatePassword(name: string, imageUrl: string) {
  const user = userEvent.setup();
  await user.type(getNameField(), name);
  await user.type(getImageUrlField(), imageUrl);
  await user.click(screen.getByRole('button', { name: 'Create' }));
  return user;
}

describe('CreatePassword', () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    addPassword.mockReset();
    setCurrentPassword.mockReset();
    postPassword.mockReset();
    navigate.mockReset();
  });

  it('renders the create password form', () => {
    render(<CreatePassword />);

    expect(screen.getByText('Create a new password')).toBeInTheDocument();
    expect(getNameField()).toBeInTheDocument();
    expect(getImageUrlField()).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create' })).toBeInTheDocument();
  });

  it('creates a password and navigates to its detail page on success', async () => {
    const created = {
      id: 42,
      name: 'GitHub',
      imageUrl: 'https://example.com/github.png',
    };
    postPassword.mockResolvedValue(created);

    render(<CreatePassword />);
    await submitCreatePassword('GitHub', 'https://example.com/github.png');

    await waitFor(() => {
      expect(postPassword).toHaveBeenCalledWith({
        name: 'GitHub',
        imageUrl: 'https://example.com/github.png',
      });
      expect(addPassword).toHaveBeenCalledWith(created);
      expect(setCurrentPassword).toHaveBeenCalledWith(null);
      expect(navigate).toHaveBeenCalledWith('/password/42');
    });
  });

  it('shows an error when create fails', async () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    postPassword.mockRejectedValue(new Error('create failed'));

    render(<CreatePassword />);
    await submitCreatePassword('GitHub', 'https://example.com/github.png');

    await waitFor(() => {
      expect(screen.getAllByText('Failed to create password').length).toBeGreaterThan(0);
    });
    expect(navigate).not.toHaveBeenCalled();
    expect(addPassword).not.toHaveBeenCalled();

    consoleError.mockRestore();
  });

  it('clears the error when the user types again', async () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    postPassword.mockRejectedValue(new Error('create failed'));

    const user = userEvent.setup();
    render(<CreatePassword />);
    await submitCreatePassword('GitHub', 'https://example.com/github.png');

    await waitFor(() => {
      expect(screen.getAllByText('Failed to create password').length).toBeGreaterThan(0);
    });

    await user.type(getNameField(), 'x');

    await waitFor(() => {
      expect(screen.queryByText('Failed to create password')).not.toBeInTheDocument();
    });

    consoleError.mockRestore();
  });
});
