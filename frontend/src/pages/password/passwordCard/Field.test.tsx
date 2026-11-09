/**
 * Tests for Field: visibility toggle, copy to clipboard, and saving edits.
 */

import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { usePasswordsStore, type PasswordField } from '@store/passwords';
import { useUserStore } from '@store/user';

import { Field } from './Field';

const { putField } = vi.hoisted(() => ({ putField: vi.fn() }));

vi.mock('@utils/apiClient/field', () => ({
  useFieldAPIClient: () => ({ putField }),
}));

const field: PasswordField = {
  id: 1,
  name: 'username',
  isDeleted: false,
  valueDecrypted: 'alice',
  createdAt: '2026-01-01T00:00:00Z',
};

function getInput() {
  return screen.getByLabelText('username');
}

function getSaveButton() {
  return screen.getByRole('button', { name: 'edit' });
}

describe('Field', () => {
  beforeEach(() => {
    putField.mockReset();
    useUserStore.setState({ isLoading: false });
    usePasswordsStore.getState().setCurrentPassword({
      id: 7,
      name: 'GitHub',
      createdAt: '2026-01-01T00:00:00Z',
      imageUrl: 'github.png',
      fields: [field],
    });
  });

  afterEach(() => {
    cleanup();
  });

  it('shows the value masked with saving disabled until it changes', () => {
    render(<Field field={field} />);

    expect(getInput()).toHaveValue('alice');
    expect(getInput()).toHaveAttribute('type', 'password');
    expect(getSaveButton()).toBeDisabled();
  });

  it('toggles the value visibility', async () => {
    const user = userEvent.setup();
    render(<Field field={field} />);

    await user.click(screen.getByTestId('VisibilityOffIcon'));
    expect(getInput()).toHaveAttribute('type', 'text');

    await user.click(screen.getByTestId('VisibilityIcon'));
    expect(getInput()).toHaveAttribute('type', 'password');
  });

  it('copies the decrypted value to the clipboard', async () => {
    const user = userEvent.setup();
    render(<Field field={field} />);

    await user.click(screen.getByTestId('ContentCopyIcon'));

    await expect(navigator.clipboard.readText()).resolves.toBe('alice');
  });

  it('saves an edited value and syncs the store', async () => {
    const updated = { ...field, id: 3, valueDecrypted: 'bob' };
    putField.mockResolvedValue(updated);
    const user = userEvent.setup();
    render(<Field field={field} />);

    await user.clear(getInput());
    await user.type(getInput(), 'bob');
    await user.click(getSaveButton());

    expect(putField).toHaveBeenCalledWith(1, { value: 'bob' });
    await waitFor(() => {
      expect(usePasswordsStore.getState().currentPassword?.fields).toEqual([
        { ...field, isDeleted: true },
        updated,
      ]);
    });
    expect(getInput()).toHaveValue('bob');
  });

  it('requires a value before saving', async () => {
    const user = userEvent.setup();
    render(<Field field={field} />);

    await user.clear(getInput());
    await user.click(getSaveButton());

    expect(screen.getByText('Please fill in all fields')).toBeInTheDocument();
    expect(putField).not.toHaveBeenCalled();
  });

  it('shows an error when saving fails', async () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    putField.mockRejectedValue(new Error('server error'));
    const user = userEvent.setup();
    render(<Field field={field} />);

    await user.type(getInput(), '2');
    await user.click(getSaveButton());

    expect(await screen.findByText('Failed to update field')).toBeInTheDocument();
    consoleError.mockRestore();
  });

  it('renders deleted fields read-only without a save button', () => {
    render(<Field field={{ ...field, isDeleted: true }} />);

    expect(getInput()).toBeDisabled();
    expect(screen.queryByRole('button', { name: 'edit' })).not.toBeInTheDocument();
  });
});
