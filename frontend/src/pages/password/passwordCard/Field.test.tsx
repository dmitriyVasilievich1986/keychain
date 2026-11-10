/**
 * Tests for Field: editing the name and current value, visibility/copy actions, and the history
 * list.
 */

import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { afterEach, describe, expect, it, vi } from 'vite-plus/test';

import { type PasswordField } from '@store/passwords';

import { Field } from './Field';
import { createDrafts, type FieldDraft } from './fields';

const field: PasswordField = {
  name: 'username',
  position: 0,
  values: [
    { value: 'alice-old', createdAt: '2026-01-01T10:00:00Z' },
    { value: 'alice', createdAt: '2026-02-01T10:00:00Z' },
  ],
  createdAt: '2026-01-01T10:00:00Z',
  updatedAt: '2026-02-01T10:00:00Z',
  deletedAt: null,
};

const [draft] = createDrafts([field]);

/** Renders Field with local draft state, reporting every change to `onChange`. */
function ControlledField(props: {
  initial: FieldDraft;
  onChange?: (draft: FieldDraft) => void;
  onDelete?: () => void;
  onRestore?: () => void;
  showErrors?: boolean;
}) {
  const [current, setCurrent] = useState(props.initial);
  return (
    <Field
      draft={current}
      showErrors={props.showErrors}
      onChange={(next) => {
        setCurrent(next);
        props.onChange?.(next);
      }}
      onDelete={props.onDelete ?? (() => {})}
      onRestore={props.onRestore ?? (() => {})}
    />
  );
}

function getNameInput() {
  return screen.getByLabelText('Field name');
}

function getValueInput() {
  return screen.getByLabelText('Field value');
}

describe('Field', () => {
  afterEach(() => {
    cleanup();
  });

  it('shows the name and the masked current value', () => {
    render(<ControlledField initial={draft} />);

    expect(getNameInput()).toHaveValue('username');
    expect(getValueInput()).toHaveValue('alice');
    expect(getValueInput()).toHaveAttribute('type', 'password');
  });

  it('reports name and value edits', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(<ControlledField initial={draft} onChange={onChange} />);

    await user.clear(getNameInput());
    await user.type(getNameInput(), 'login');
    await user.clear(getValueInput());
    await user.type(getValueInput(), 'bob');

    expect(onChange).toHaveBeenLastCalledWith({ ...draft, name: 'login', value: 'bob' });
  });

  it('toggles the value visibility without expanding the accordion', async () => {
    const user = userEvent.setup();
    render(<ControlledField initial={draft} />);
    const toggle = screen.getByRole('button', { name: 'username history' });

    await user.click(screen.getAllByTestId('VisibilityOffIcon')[0]);
    expect(getValueInput()).toHaveAttribute('type', 'text');
    expect(toggle).toHaveAttribute('aria-expanded', 'false');

    await user.click(screen.getByTestId('VisibilityIcon'));
    expect(getValueInput()).toHaveAttribute('type', 'password');
  });

  it('copies the current value to the clipboard', async () => {
    const user = userEvent.setup();
    render(<ControlledField initial={draft} />);

    await user.click(screen.getAllByTestId('ContentCopyIcon')[0]);

    await expect(navigator.clipboard.readText()).resolves.toBe('alice');
  });

  it('lists previous values read-only inside the accordion', async () => {
    const user = userEvent.setup();
    render(<ControlledField initial={draft} />);
    const history = screen.getByDisplayValue('alice-old');
    expect(history).not.toBeVisible();

    await user.click(screen.getByRole('button', { name: 'username history' }));

    await waitFor(() => {
      expect(history).toBeVisible();
    });
    expect(history).toHaveAttribute('readonly');
  });

  it('shows placeholders for fields without history and for new fields', () => {
    const [single] = createDrafts([{ ...field, values: [field.values[1]] }]);
    const { unmount } = render(<ControlledField initial={single} />);
    expect(screen.getByText('No previous values')).toBeInTheDocument();
    unmount();

    render(
      <ControlledField
        initial={{ key: 'new-0', name: 'email', value: 'a@b.c', deleted: false, field: null }}
      />
    );
    expect(screen.getByText('New field, not saved yet')).toBeInTheDocument();
  });

  it('marks empty inputs as errors when requested', () => {
    render(<ControlledField initial={{ ...draft, name: '', value: '' }} showErrors />);

    expect(getNameInput()).toHaveAttribute('aria-invalid', 'true');
    expect(getValueInput()).toHaveAttribute('aria-invalid', 'true');
  });

  it('has a delete button for active fields', async () => {
    const onDelete = vi.fn();
    const user = userEvent.setup();
    render(<ControlledField initial={draft} onDelete={onDelete} />);

    expect(screen.queryByRole('button', { name: 'Restore username' })).not.toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'Delete username' }));

    expect(onDelete).toHaveBeenCalledTimes(1);
    expect(screen.getByRole('button', { name: 'username history' })).toHaveAttribute(
      'aria-expanded',
      'false'
    );
  });

  it('shows a deleted field read-only and struck through, with a restore button', async () => {
    const onRestore = vi.fn();
    const user = userEvent.setup();
    const [deleted] = createDrafts([{ ...field, deletedAt: '2026-03-01T10:00:00Z' }]);
    render(<ControlledField initial={deleted} onRestore={onRestore} />);

    expect(getNameInput()).toHaveAttribute('readonly');
    expect(getValueInput()).toHaveAttribute('readonly');
    expect(getNameInput()).toHaveStyle({ textDecoration: 'line-through' });
    expect(screen.getByText(/^Deleted 2026-03-01/)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Delete username' })).not.toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: 'Restore username' }));
    expect(onRestore).toHaveBeenCalledTimes(1);
  });

  it('says a field deleted in the drafts is only removed on update', () => {
    render(<ControlledField initial={{ ...draft, deleted: true }} />);

    expect(screen.getByText('Will be deleted on update')).toBeInTheDocument();
  });
});
