/**
 * This file contains the PasswordCard component.
 * It is used to render the detail card for the password selected via the `:passwordId` route param.
 */

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import classnames from 'classnames/bind';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router';

import { Image } from '@components/image';
import { usePasswordsStore, type Password } from '@store/passwords';
import { useUserStore } from '@store/user';
import { usePasswordAPIClient } from '@utils/apiClient/password';

import { AddField } from './AddField';
import { Field } from './Field';
import {
  createDrafts,
  deleteDraft,
  isDraftChanged,
  isDraftValid,
  restoreDraft,
  toFieldRequests,
  type FieldDraft,
} from './fields';
import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

/**
 * Body of the password card: header, editable fields, add-field form and the update button.
 *
 * Holds one draft per field so every edit (renames, new values, new fields, deletions) stays local
 * until the single update button sends them all in one `PATCH /api/v1/password/{id}`. A changed
 * value is appended to the field's history rather than replacing the current value. Deleting a
 * field only marks it as deleted (`deletedAt`), so it keeps its history and can be restored;
 * deleted fields are listed in their own section below the active ones. The parent remounts
 * this component (via `key`) when the saved password changes, which resets the drafts.
 *
 * @param props - Component props.
 * @param props.password - The saved password being edited.
 * @returns The card body.
 */
function PasswordCardContent(props: { password: Password }) {
  const { password } = props;
  const [drafts, setDrafts] = useState<FieldDraft[]>(() => createDrafts(password.fields));
  const [newFieldCount, setNewFieldCount] = useState(0);
  const [error, setError] = useState<string>('');
  const [showErrors, setShowErrors] = useState(false);

  const { isLoading } = useUserStore();
  const { updatePassword } = usePasswordsStore();
  const { patchPassword } = usePasswordAPIClient();

  // New fields always count as changed, and only new fields are ever removed from the drafts (a
  // removed new field leaves nothing to save), so this covers every edit.
  const hasChanges = drafts.some(isDraftChanged);
  const activeDrafts = drafts.filter((draft) => !draft.deleted);
  const deletedDrafts = drafts.filter((draft) => draft.deleted);

  /** Replaces the draft with the same key. */
  const handleFieldChange = (next: FieldDraft) => {
    setDrafts((current) => current.map((draft) => (draft.key === next.key ? next : draft)));
  };

  /**
   * Marks the field as deleted, dropping its unsaved edits; an unsaved new field is removed.
   * Nothing is sent until the update button is pressed.
   */
  const handleDeleteField = (key: string) => {
    setDrafts((current) =>
      current.flatMap((draft) => {
        if (draft.key !== key) return [draft];
        const deleted = deleteDraft(draft);
        return deleted ? [deleted] : [];
      })
    );
  };

  /** Makes a deleted field active again. */
  const handleRestoreField = (key: string) => {
    setDrafts((current) =>
      current.map((draft) => (draft.key === key ? restoreDraft(draft) : draft))
    );
  };

  /** Appends an unsaved field after the existing ones. */
  const handleAddField = (name: string, value: string) => {
    setDrafts((current) => [
      ...current,
      { key: `new-${newFieldCount}`, name, value, deleted: false, field: null },
    ]);
    setNewFieldCount((count) => count + 1);
  };

  /**
   * Saves all drafts in one patch request. Requires every field to have a name and a value. On
   * success the store is synced with the returned password (which resets the drafts); on failure
   * the drafts are kept and an error message is shown.
   */
  const handleUpdate = () => {
    if (isLoading || !hasChanges) return;
    if (!drafts.every(isDraftValid)) {
      setShowErrors(true);
      setError('Please fill in all fields');
      return;
    }
    setShowErrors(false);
    setError('');
    patchPassword(password.id, { fields: toFieldRequests(drafts) })
      .then((response) => {
        updatePassword(response);
      })
      .catch((err) => {
        console.error(err);
        setError('Failed to update password');
      });
  };

  return (
    <Paper elevation={10} sx={{ padding: '1rem' }}>
      <Box className={cx('password-card-header')}>
        {password.imageUrl && (
          <Image
            src={`${import.meta.env.VITE_IMAGES_HOST}/${password.imageUrl}`}
            alt={password.name}
            width={25}
            height={25}
          />
        )}
        <Typography variant="h6">{password.name}</Typography>
      </Box>
      <Stack spacing={2} sx={{ marginTop: '2rem' }}>
        {activeDrafts.map((draft) => (
          <Field
            key={draft.key}
            draft={draft}
            onChange={handleFieldChange}
            onDelete={() => handleDeleteField(draft.key)}
            onRestore={() => handleRestoreField(draft.key)}
            showErrors={showErrors}
          />
        ))}
      </Stack>
      <AddField onAdd={handleAddField} />
      {deletedDrafts.length > 0 && (
        <Box sx={{ marginTop: '2rem' }}>
          <Divider textAlign="left" sx={{ marginBottom: 2, color: 'text.disabled' }}>
            <Typography variant="caption">Deleted fields</Typography>
          </Divider>
          <Stack spacing={2}>
            {deletedDrafts.map((draft) => (
              <Field
                key={draft.key}
                draft={draft}
                onChange={handleFieldChange}
                onDelete={() => handleDeleteField(draft.key)}
                onRestore={() => handleRestoreField(draft.key)}
              />
            ))}
          </Stack>
        </Box>
      )}
      <Stack direction="row" spacing={2} sx={{ marginTop: '2rem', alignItems: 'center' }}>
        <Button
          variant="contained"
          color="secondary"
          onClick={handleUpdate}
          disabled={!hasChanges}
          loading={isLoading}
        >
          Update
        </Button>
        {error && (
          <Typography variant="body2" color="error">
            {error}
          </Typography>
        )}
      </Stack>
    </Paper>
  );
}

/**
 * Detail card for the password selected via the `:passwordId` route param.
 *
 * Fetches the password when the route changes and renders the card body for it. Each field is an
 * accordion with editable name and current value in the header and the value history inside;
 * all changes are saved together with a single update button. Renders nothing when no password is
 * selected.
 *
 * @returns The password detail card, or `null`.
 */
export function PasswordCard() {
  const { passwordId } = useParams();
  const { currentPassword, setCurrentPassword } = usePasswordsStore();
  const { getPassword } = usePasswordAPIClient();

  // Loads the selected password when the route param changes, clearing it when
  // no id is present and skipping the fetch when one is already loaded.
  useEffect(() => {
    if (!passwordId) {
      setCurrentPassword(null);
      return;
    }
    if (currentPassword !== null && currentPassword.id === passwordId) return;
    getPassword(passwordId)
      .then((response) => {
        setCurrentPassword(response);
      })
      .catch((error) => {
        console.error(error);
      });
  }, [passwordId, currentPassword]);

  if (!currentPassword) return null;

  return (
    <Box sx={{ padding: '1rem' }}>
      {/* Remount on every saved change so the drafts start from the saved password. */}
      <PasswordCardContent
        key={`${currentPassword.id}-${currentPassword.updatedAt}`}
        password={currentPassword}
      />
    </Box>
  );
}
