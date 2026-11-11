/**
 * Tests for PasswordCard: loading the routed password, field rendering, and saving all field edits
 * with the single update button.
 */

import { cleanup, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { usePasswordsStore, type Password } from '@store/passwords';
import { useUserStore } from '@store/user';

import { PasswordCard } from './PasswordCard';

const { getPassword, patchPassword } = vi.hoisted(() => ({
  getPassword: vi.fn(),
  patchPassword: vi.fn(),
}));

vi.mock('@utils/apiClient/password', () => ({
  usePasswordAPIClient: () => ({ getPassword, patchPassword }),
}));

const PASSWORD_ID = '5f1d7c2e-8b1a-4c3d-9e2f-1a2b3c4d5e6f';

const password: Password = {
  id: PASSWORD_ID,
  name: 'GitHub',
  createdAt: '2026-01-01T00:00:00Z',
  updatedAt: '2026-01-01T00:00:00Z',
  imageUrl: 'github.png',
  userId: 'u-1',
  fields: [
    {
      name: 'password',
      position: 1,
      values: [{ value: 'hunter2', createdAt: '2026-01-01T00:00:00Z' }],
      createdAt: '2026-01-01T00:00:00Z',
      updatedAt: '2026-01-01T00:00:00Z',
      deletedAt: null,
    },
    {
      name: 'username',
      position: 0,
      values: [
        { value: 'alice-old', createdAt: '2026-01-01T00:00:00Z' },
        { value: 'alice', createdAt: '2026-01-02T00:00:00Z' },
      ],
      createdAt: '2026-01-01T00:00:00Z',
      updatedAt: '2026-01-02T00:00:00Z',
      deletedAt: null,
    },
    {
      name: 'pin',
      position: 2,
      values: [{ value: '1234', createdAt: '2026-01-01T00:00:00Z' }],
      createdAt: '2026-01-01T00:00:00Z',
      updatedAt: '2026-01-01T00:00:00Z',
      deletedAt: '2026-01-03T00:00:00Z',
    },
  ],
};

const T1 = '2026-01-01T00:00:00Z';
const usernameValues = [
  { value: 'alice-old', createdAt: T1 },
  { value: 'alice', createdAt: '2026-01-02T00:00:00Z' },
];
const pinValues = [{ value: '1234', createdAt: T1 }];

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

/** Returns the accordion of the field whose summary is labelled `<name> history`. */
function getFieldRow(name: string) {
  const summary = screen.getByRole('button', { name: `${name} history` });
  return within(summary.closest('.MuiAccordion-root') as HTMLElement);
}

function getUpdateButton() {
  return screen.getByRole('button', { name: 'Update' });
}

describe('PasswordCard', () => {
  beforeEach(() => {
    getPassword.mockReset();
    patchPassword.mockReset();
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

    renderAt(`/password/${PASSWORD_ID}`);

    expect(await screen.findByRole('heading', { level: 6, name: 'GitHub' })).toBeInTheDocument();
    expect(getPassword).toHaveBeenCalledWith(PASSWORD_ID);
    expect(getFieldRow('username').getByLabelText('Field value')).toHaveValue('alice');
    expect(getFieldRow('password').getByLabelText('Field value')).toHaveValue('hunter2');
    expect(screen.getByLabelText('New field name')).toBeInTheDocument();
  });

  it('renders active fields in position order, then deleted fields in their own section', () => {
    usePasswordsStore.getState().setCurrentPassword(password);

    renderAt(`/password/${PASSWORD_ID}`);

    expect(
      screen
        .getAllByRole('button', { name: / history$/ })
        .map((el) => el.getAttribute('aria-label'))
    ).toEqual(['username history', 'password history', 'pin history']);
    expect(screen.getByText('Deleted fields')).toBeInTheDocument();
    expect(getFieldRow('pin').getByLabelText('Field name')).toHaveAttribute('readonly');
    expect(getFieldRow('pin').getByRole('button', { name: 'Restore pin' })).toBeInTheDocument();
  });

  it('hides the deleted section when no field is deleted', () => {
    usePasswordsStore
      .getState()
      .setCurrentPassword({ ...password, fields: password.fields.slice(0, 2) });

    renderAt(`/password/${PASSWORD_ID}`);

    expect(screen.queryByText('Deleted fields')).not.toBeInTheDocument();
  });

  it('marks a deleted field with deletedAt instead of removing it', async () => {
    vi.useFakeTimers({ toFake: ['Date'], now: new Date('2026-05-01T00:00:00Z') });
    patchPassword.mockResolvedValue({ ...password, updatedAt: '2026-05-01T00:00:00Z' });
    usePasswordsStore.getState().setCurrentPassword(password);
    const user = userEvent.setup();
    renderAt(`/password/${PASSWORD_ID}`);

    await user.click(screen.getByRole('button', { name: 'Delete password' }));

    // Moved to the deleted section, but nothing is sent until Update.
    expect(patchPassword).not.toHaveBeenCalled();
    expect(getFieldRow('password').getByText('Will be deleted on update')).toBeInTheDocument();
    expect(getUpdateButton()).toBeEnabled();

    await user.click(getUpdateButton());

    expect(patchPassword).toHaveBeenCalledWith(PASSWORD_ID, {
      fields: [
        { name: 'username', values: usernameValues, createdAt: T1, deletedAt: null },
        {
          name: 'password',
          values: [{ value: 'hunter2', createdAt: T1 }],
          createdAt: T1,
          deletedAt: '2026-05-01T00:00:00.000Z',
        },
        { name: 'pin', values: pinValues, createdAt: T1, deletedAt: '2026-01-03T00:00:00Z' },
      ],
    });
    vi.useRealTimers();
  });

  it('restores a deleted field', async () => {
    patchPassword.mockResolvedValue({ ...password, updatedAt: '2026-05-01T00:00:00Z' });
    usePasswordsStore.getState().setCurrentPassword(password);
    const user = userEvent.setup();
    renderAt(`/password/${PASSWORD_ID}`);

    await user.click(screen.getByRole('button', { name: 'Restore pin' }));
    expect(screen.queryByText('Deleted fields')).not.toBeInTheDocument();
    expect(getFieldRow('pin').getByLabelText('Field name')).not.toHaveAttribute('readonly');

    await user.click(getUpdateButton());

    expect(patchPassword).toHaveBeenCalledWith(PASSWORD_ID, {
      fields: expect.arrayContaining([
        { name: 'pin', values: pinValues, createdAt: T1, deletedAt: null },
      ]),
    });
  });

  it('drops a new, unsaved field when it is deleted', async () => {
    usePasswordsStore.getState().setCurrentPassword(password);
    const user = userEvent.setup();
    renderAt(`/password/${PASSWORD_ID}`);

    await user.type(screen.getByLabelText('New field name'), 'email');
    await user.type(screen.getByLabelText('New field value'), 'a@example.com');
    await user.click(screen.getByRole('button', { name: 'edit' }));
    await user.click(screen.getByRole('button', { name: 'Delete email' }));

    expect(screen.queryByRole('button', { name: 'email history' })).not.toBeInTheDocument();
    expect(getUpdateButton()).toBeDisabled();
  });

  it('has a single update button, disabled until something changes', async () => {
    usePasswordsStore.getState().setCurrentPassword(password);
    const user = userEvent.setup();
    renderAt(`/password/${PASSWORD_ID}`);

    expect(screen.getAllByRole('button', { name: 'Update' })).toHaveLength(1);
    expect(getUpdateButton()).toBeDisabled();

    await user.type(getFieldRow('password').getByLabelText('Field value'), '!');
    expect(getUpdateButton()).toBeEnabled();
  });

  it('saves renames, new values and new fields in one request, appending values to history', async () => {
    vi.useFakeTimers({ toFake: ['Date'], now: new Date('2026-05-01T00:00:00Z') });
    const now = '2026-05-01T00:00:00.000Z';
    const saved: Password = { ...password, updatedAt: '2026-02-01T00:00:00Z' };
    patchPassword.mockResolvedValue(saved);
    usePasswordsStore.getState().setCurrentPassword(password);
    const user = userEvent.setup();
    renderAt(`/password/${PASSWORD_ID}`);

    const username = getFieldRow('username');
    await user.clear(username.getByLabelText('Field name'));
    await user.type(username.getByLabelText('Field name'), 'login');
    const secret = getFieldRow('password');
    await user.clear(secret.getByLabelText('Field value'));
    await user.type(secret.getByLabelText('Field value'), 'correct-horse');
    await user.type(screen.getByLabelText('New field name'), 'email');
    await user.type(screen.getByLabelText('New field value'), 'a@example.com');
    await user.click(screen.getByRole('button', { name: 'edit' }));

    // Adding a field only adds a draft row; nothing is sent until Update.
    expect(patchPassword).not.toHaveBeenCalled();
    expect(getFieldRow('email').getByLabelText('Field value')).toHaveValue('a@example.com');

    await user.click(getUpdateButton());

    expect(patchPassword).toHaveBeenCalledTimes(1);
    expect(patchPassword).toHaveBeenCalledWith(PASSWORD_ID, {
      fields: [
        { name: 'login', values: usernameValues, createdAt: T1, deletedAt: null },
        {
          name: 'password',
          values: [
            { value: 'hunter2', createdAt: T1 },
            { value: 'correct-horse', createdAt: now },
          ],
          createdAt: T1,
          deletedAt: null,
        },
        { name: 'pin', values: pinValues, createdAt: T1, deletedAt: '2026-01-03T00:00:00Z' },
        {
          name: 'email',
          values: [{ value: 'a@example.com', createdAt: now }],
          createdAt: now,
          deletedAt: null,
        },
      ],
    });
    await waitFor(() => {
      expect(usePasswordsStore.getState().currentPassword).toEqual(saved);
    });
    vi.useRealTimers();
  });

  it('resets the drafts to the saved password after a successful update', async () => {
    const saved: Password = {
      ...password,
      updatedAt: '2026-02-01T00:00:00Z',
      fields: [
        password.fields[1],
        {
          ...password.fields[0],
          values: [
            ...password.fields[0].values,
            { value: 'hunter3', createdAt: '2026-02-01T00:00:00Z' },
          ],
        },
      ],
    };
    patchPassword.mockResolvedValue(saved);
    usePasswordsStore.getState().setCurrentPassword(password);
    const user = userEvent.setup();
    renderAt(`/password/${PASSWORD_ID}`);

    await user.clear(getFieldRow('password').getByLabelText('Field value'));
    await user.type(getFieldRow('password').getByLabelText('Field value'), 'hunter3');
    await user.click(getUpdateButton());

    await waitFor(() => {
      expect(getUpdateButton()).toBeDisabled();
    });
    expect(getFieldRow('password').getByLabelText('Field value')).toHaveValue('hunter3');
    expect(getFieldRow('password').getByDisplayValue('hunter2')).toHaveAttribute('readonly');
  });

  it('requires every field to have a name and a value', async () => {
    usePasswordsStore.getState().setCurrentPassword(password);
    const user = userEvent.setup();
    renderAt(`/password/${PASSWORD_ID}`);

    await user.clear(getFieldRow('password').getByLabelText('Field value'));
    await user.click(getUpdateButton());

    expect(screen.getByText('Please fill in all fields')).toBeInTheDocument();
    expect(getFieldRow('password').getByLabelText('Field value')).toHaveAttribute(
      'aria-invalid',
      'true'
    );
    expect(patchPassword).not.toHaveBeenCalled();
  });

  it('keeps the edits and shows an error when the update fails', async () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    patchPassword.mockRejectedValue(new Error('server error'));
    usePasswordsStore.getState().setCurrentPassword(password);
    const user = userEvent.setup();
    renderAt(`/password/${PASSWORD_ID}`);

    await user.type(getFieldRow('password').getByLabelText('Field value'), '!');
    await user.click(getUpdateButton());

    expect(await screen.findByText('Failed to update password')).toBeInTheDocument();
    expect(getFieldRow('password').getByLabelText('Field value')).toHaveValue('hunter2!');
    expect(usePasswordsStore.getState().currentPassword).toEqual(password);
    consoleError.mockRestore();
  });

  it('keeps the card mounted and the update button busy while a request is in progress', () => {
    usePasswordsStore.getState().setCurrentPassword(password);
    useUserStore.setState({ isLoading: true });

    renderAt(`/password/${PASSWORD_ID}`);

    expect(screen.getByRole('heading', { level: 6, name: 'GitHub' })).toBeInTheDocument();
    expect(getUpdateButton()).toBeDisabled();
  });

  it('does not refetch the password that is already loaded', () => {
    usePasswordsStore.getState().setCurrentPassword(password);

    renderAt(`/password/${PASSWORD_ID}`);

    expect(screen.getByRole('heading', { level: 6, name: 'GitHub' })).toBeInTheDocument();
    expect(getPassword).not.toHaveBeenCalled();
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
