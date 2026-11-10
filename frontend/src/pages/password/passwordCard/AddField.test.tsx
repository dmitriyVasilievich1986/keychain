/**
 * Tests for AddField: validation and handing a new field to the card.
 */

import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { useUserStore } from '@store/user';

import { AddField } from './AddField';

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
    useUserStore.setState({ isLoading: false });
  });

  afterEach(() => {
    cleanup();
  });

  it('requires both a name and a value', async () => {
    const onAdd = vi.fn();
    const user = userEvent.setup();
    render(<AddField onAdd={onAdd} />);

    await user.type(getNameInput(), 'username');
    await user.click(getAddButton());

    // The message is shown under both inputs.
    expect(screen.getAllByText('Please fill in all fields')).toHaveLength(2);
    expect(onAdd).not.toHaveBeenCalled();
  });

  it('hands the field to onAdd and resets the form', async () => {
    const onAdd = vi.fn();
    const user = userEvent.setup();
    render(<AddField onAdd={onAdd} />);

    await user.click(getAddButton());
    expect(screen.getAllByText('Please fill in all fields')).toHaveLength(2);

    await user.type(getNameInput(), 'username');
    await user.type(getValueInput(), 'alice');
    await user.click(getAddButton());

    expect(onAdd).toHaveBeenCalledWith('username', 'alice');
    expect(getNameInput()).toHaveValue('');
    expect(getValueInput()).toHaveValue('');
    expect(screen.queryByText('Please fill in all fields')).not.toBeInTheDocument();
  });
});
