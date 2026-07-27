/**
 * This file contains the CreatePassword component.
 * It is used to render the create password page.
 */

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import classnames from 'classnames/bind';
import { useActionState, useEffect, useState } from 'react';
import { useNavigate } from 'react-router';

import { usePasswordsStore } from '@store/passwords';
import { usePasswordAPIClient } from '@utils/apiClient/password';

import * as defaultStyle from './style.scss';

import type { CreatePasswordFormState } from './types';

const cx = classnames.bind(defaultStyle);

/**
 * Page for creating a new password entry.
 *
 * Renders a form with name and image URL inputs, submits the new entry via
 * `useActionState`, and on success adds it to the store and navigates to its
 * detail view.
 *
 * @returns The create-password page.
 */
export function CreatePassword() {
  const [isDirty, setIsDirty] = useState(false);
  const { setCurrentPassword, addPassword } = usePasswordsStore();
  const navigate = useNavigate();
  const { postPassword } = usePasswordAPIClient();

  const [state, formAction, isPending] = useActionState(
    async (
      _prevState: CreatePasswordFormState,
      formData: FormData
    ): Promise<CreatePasswordFormState> => {
      const name = String(formData.get('name') ?? '');
      const imageUrl = String(formData.get('imageUrl') ?? '');

      try {
        const response = await postPassword({ name, imageUrl });
        addPassword(response);
        setCurrentPassword(null);
        navigate(`/password/${response.id}`);
        return { error: '' };
      } catch (error: unknown) {
        console.error(error);
        return { error: 'Failed to create password' };
      }
    },
    { error: '' }
  );

  // Re-show action errors after a fresh submit; typing dismisses them via `isDirty`.
  useEffect(() => {
    setIsDirty(false);
  }, [state]);

  const error = isDirty ? '' : state.error;

  return (
    <Box className={cx('create-password-container')}>
      <Paper elevation={10} className={cx('create-password-paper')}>
        <form action={formAction}>
          <Typography variant="h6" align="center" sx={{ marginBottom: '2rem' }}>
            Create a new password
          </Typography>
          <Stack spacing={2} sx={{ marginTop: '1rem' }}>
            <TextField
              name="name"
              label="PasswordName"
              variant="outlined"
              fullWidth
              error={!!error}
              helperText={error}
              disabled={isPending}
              onChange={() => setIsDirty(true)}
            />
            <TextField
              name="imageUrl"
              label="Password Image URL"
              variant="outlined"
              fullWidth
              error={!!error}
              helperText={error}
              disabled={isPending}
              onChange={() => setIsDirty(true)}
            />
            <Box>
              <Button
                variant="contained"
                fullWidth
                sx={{ marginTop: '2rem' }}
                type="submit"
                disabled={isPending}
              >
                {isPending ? <CircularProgress size={20} /> : 'Create'}
              </Button>
            </Box>
          </Stack>
        </form>
      </Paper>
    </Box>
  );
}
