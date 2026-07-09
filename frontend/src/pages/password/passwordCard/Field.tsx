/**
 * This file contains the Field component.
 * It is used to render a single password field.
 */

import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import EditIcon from '@mui/icons-material/Edit';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import { useState } from 'react';

import { FloatingButton } from '@components/floatingButton';
import { usePasswordsStore, type PasswordField } from '@store/passwords';
import { useUserStore } from '@store/user';
import { useFieldAPIClient } from '@utils/apiClient/field';

/**
 * Editable row for a single password field.
 *
 * Renders the field value as a masked input with actions to toggle visibility,
 * copy the decrypted value to the clipboard, and save edits. Deleted fields are
 * shown struck through and read-only.
 *
 * @param props - Component props.
 * @param props.field - The password field to display and edit.
 * @returns The field row.
 */
export function Field(props: { field: PasswordField }) {
  const [value, setValue] = useState(props.field.valueDecrypted);
  const [updateFieldError, setUpdateFieldError] = useState<string>('');
  const [show, setShow] = useState<boolean>(false);

  const { isLoading } = useUserStore();
  const { updateField } = usePasswordsStore();
  const { putField } = useFieldAPIClient();

  /**
   * Persists the edited field value to the API.
   *
   * Does nothing while a request is in flight and requires a non-empty value.
   * On success the store and local input are synced with the response, and on
   * failure an error message is shown.
   */
  const handleUpdateField = async () => {
    if (isLoading) return;
    if (!value) {
      setUpdateFieldError('Please fill in all fields');
      return;
    }
    putField(props.field.id, { value })
      .then((response) => {
        updateField(props.field.id, response);
        setValue(response.valueDecrypted);
      })
      .catch((error) => {
        console.error(error);
        setUpdateFieldError('Failed to update field');
      });
  };

  return (
    <Stack spacing={2} sx={{ marginTop: '2rem' }} direction="row">
      <TextField
        key={props.field.id}
        label={props.field.name}
        type={show ? 'text' : 'password'}
        fullWidth
        variant="outlined"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        sx={{ textDecoration: props.field.isDeleted ? 'line-through' : 'none' }}
        disabled={props.field.isDeleted}
        color={value !== props.field.valueDecrypted ? 'secondary' : 'primary'}
        error={!!updateFieldError}
        helperText={updateFieldError}
        slotProps={{
          input: {
            endAdornment: (
              <Stack direction="row" spacing={1}>
                <IconButton size="small" onClick={() => setShow(!show)}>
                  {show ? (
                    <VisibilityIcon onClick={() => setShow(false)} />
                  ) : (
                    <VisibilityOffIcon onClick={() => setShow(true)} />
                  )}
                </IconButton>
                <IconButton
                  onClick={() => navigator.clipboard.writeText(props.field.valueDecrypted)}
                >
                  <ContentCopyIcon />
                </IconButton>
              </Stack>
            ),
          },
        }}
      />
      {props.field.isDeleted ? null : (
        <FloatingButton
          color="secondary"
          onClick={handleUpdateField}
          disabled={value === props.field.valueDecrypted}
        >
          <EditIcon />
        </FloatingButton>
      )}
    </Stack>
  );
}
