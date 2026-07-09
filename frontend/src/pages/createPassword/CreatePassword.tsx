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
import classnames from 'classnames/bind';
import { useState } from 'react';
import { useNavigate } from 'react-router';

import { usePasswordsStore } from '@store/passwords';
import { useUserStore } from '@store/user';
import { usePasswordAPIClient } from '@utils/apiClient/password';

import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

/**
 * Page for creating a new password entry.
 *
 * Renders a form with name and image URL inputs, submits the new entry to the
 * API, and on success adds it to the store and navigates to its detail view.
 *
 * @returns The create-password page.
 */
export function CreatePassword() {
  const [name, setName] = useState<string>('');
  const [imageUrl, setImageUrl] = useState<string>('');
  const [error, setError] = useState<string>('');

  const { setCurrentPassword, addPassword } = usePasswordsStore();
  const { isLoading } = useUserStore();
  const navigate = useNavigate();
  const { postPassword } = usePasswordAPIClient();

  /**
   * Creates the password on form submit.
   *
   * Prevents the default form navigation and does nothing while a request is in
   * flight. On success the new password is added to the store, the current
   * selection is reset, and the user is navigated to the new entry; on failure
   * an error message is shown.
   *
   * @param e - The form submit event.
   */
  const handleCreatePassword = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (isLoading) return;

    const data = { name, imageUrl };
    postPassword(data)
      .then((response) => {
        addPassword(response);
        setCurrentPassword(null);
        navigate(`/password/${response.id}`);
      })
      .catch((error) => {
        setError('Failed to create password');
        console.error(error);
      });
  };

  return (
    <Box className={cx('create-password-container')}>
      <Paper elevation={10} className={cx('create-password-paper')}>
        <form onSubmit={handleCreatePassword}>
          <Stack spacing={2} sx={{ marginTop: '1rem' }}>
            <TextField
              label="PasswordName"
              variant="outlined"
              fullWidth
              value={name}
              onChange={(e) => setName(e.target.value)}
              error={!!error}
              helperText={error}
            />
            <TextField
              label="Password Image URL"
              variant="outlined"
              fullWidth
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              error={!!error}
              helperText={error}
            />
            <Box>
              <Button
                variant="contained"
                fullWidth
                sx={{ marginTop: '2rem' }}
                type="submit"
                disabled={isLoading}
              >
                {isLoading ? <CircularProgress size={20} /> : 'Create Password'}
              </Button>
            </Box>
          </Stack>
        </form>
      </Paper>
    </Box>
  );
}
