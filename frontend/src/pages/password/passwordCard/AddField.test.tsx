/**
 * Tests for AddField: validation, creating a field, and error handling.
 */

import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { usePasswordsStore } from '@store/passwords';
import { useUserStore } from '@store/user';

import { AddField } from './AddField';

const { postField } = vi.hoisted(() => ({ postField: vi.fn() }));

vi.mock('@utils/apiClient/field', () => ({
  useFieldAPIClient: () => ({ postField }),
}));

function getNameInput() {
  return screen.getByLabelText('New field name');
}

function getValueInput() {
  return screen.getByLabelText('New field value');
}

function getAddButton() {
  return screen.getByRole('button', { name: 'edit' });
}

describe('AddField', () => {
  beforeEach(() => {
    postField.mockReset();
    useUserStore.setState({ isLoading: false });
    usePasswordsStore.getState().setCurrentPassword({
      id: 7,
      name: 'GitHub',
      createdAt: '2026-01-01T00:00:00Z',
      imageUrl: 'github.png',
      fields: [],
    });
  });

  afterEach(() => {
    cleanup();
  });

  it('requires both a name and a value', async () => {
    const user = userEvent.setup();
    render(<AddField />);

    await user.type(getNameInput(), 'username');
    await user.click(getAddButton());

    // The message is shown under both inputs.
    expect(screen.getAllByText('Please fill in all fields')).toHaveLength(2);
    expect(postField).not.toHaveBeenCalled();
  });

  it('creates the field, adds it to the store, and resets the form', async () => {
    const created = {
      id: 11,
      name: 'username',
      isDeleted: false,
      valueDecrypted: 'alice',
      createdAt: '2026-01-01T00:00:00Z',
    };
    postField.mockResolvedValue(created);
    const user = userEvent.setup();
    render(<AddField />);

    await user.click(getAddButton());
    expect(screen.getAllByText('Please fill in all fields')).toHaveLength(2);

    await user.type(getNameInput(), 'username');
    await user.type(getValueInput(), 'alice');
    await user.click(getAddButton());

    expect(postField).toHaveBeenCalledWith({ passwordId: 7, name: 'username', value: 'alice' });
    expect(usePasswordsStore.getState().currentPassword?.fields).toEqual([created]);
    expect(getNameInput()).toHaveValue('');
    expect(getValueInput()).toHaveValue('');
    expect(screen.queryByText('Please fill in all fields')).not.toBeInTheDocument();
  });

  it('shows an error when creating fails', async () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    postField.mockRejectedValue(new Error('server error'));
    const user = userEvent.setup();
    render(<AddField />);

    await user.type(getNameInput(), 'username');
    await user.type(getValueInput(), 'alice');
    await user.click(getAddButton());

    expect(await screen.findAllByText('Failed to add field')).toHaveLength(2);
    expect(getNameInput()).toHaveValue('username');
    consoleError.mockRestore();
  });
});
