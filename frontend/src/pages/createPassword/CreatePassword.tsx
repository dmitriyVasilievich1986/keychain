import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import classnames from 'classnames/bind';
import { useState } from 'react';
import { useNavigate } from 'react-router';

import { usePasswordsStore, type Password } from '@store/passwords';
import { useUserStore } from '@store/user';
import { useApiClient } from '@utils/apiClient';

import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

export function CreatePassword() {
  const [name, setName] = useState<string>('');
  const [imageUrl, setImageUrl] = useState<string>('');
  const [error, setError] = useState<string>('');

  const { setCurrentPassword, addPassword } = usePasswordsStore();
  const { isLoading } = useUserStore();
  const navigate = useNavigate();
  const { apiPost } = useApiClient();

  const handleCreatePassword = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (isLoading) return;

    const data = { name, imageUrl };
    try {
      const response = await apiPost<{ name: string; imageUrl: string }, Password>(
        '/api/v1/password',
        data
      );
      addPassword({
        id: response.id,
        name: response.name,
        imageUrl: response.imageUrl,
      });
      setCurrentPassword(response);
      navigate(`/password/${response.id}`);
    } catch (error) {
      setError('Failed to create password');
      console.error(error);
    }
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
