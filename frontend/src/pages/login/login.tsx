import avatar from '@assets/avatar.svg';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CardContent from '@mui/material/CardContent';
import CircularProgress from '@mui/material/CircularProgress';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import axios from 'axios';
import classnames from 'classnames/bind';
import { useState } from 'react';
import { useNavigate } from 'react-router';

import { useUserStore } from '@store/user';

import * as defaultStyle from './style.scss';

import type { LoginResponse } from './types';

const cx = classnames.bind(defaultStyle);

export function Login() {
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  const { setAccessToken } = useUserStore();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (isLoading) return;

    setIsLoading(true);
    const data = { username, password };
    try {
      const response = await axios.post<LoginResponse>(
        `${import.meta.env.VITE_API_HOST}/api/v1/user/login`,
        data
      );
      setAccessToken(response.data.accessToken);
      navigate('/');
    } catch (error) {
      console.error(error);
      setError('Invalid username or password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box className={cx('login-container')}>
      <Paper elevation={10} className={cx('login-paper')}>
        <CardContent>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
            }}
          >
            <img src={avatar} alt="avatar" width={100} height={100} />
          </Box>
          <form onSubmit={handleLogin}>
            <Stack spacing={2} sx={{ marginTop: '1rem' }}>
              <TextField
                label="Login"
                variant="outlined"
                fullWidth
                value={username}
                onChange={(e) => {
                  setUsername(e.target.value);
                  setError('');
                }}
                error={!!error}
                helperText={error}
                disabled={isLoading}
              />
              <TextField
                label="Password"
                variant="outlined"
                fullWidth
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setError('');
                }}
                error={!!error}
                helperText={error}
                disabled={isLoading}
              />
            </Stack>
            <Button
              variant="contained"
              fullWidth
              sx={{ marginTop: '2rem' }}
              type="submit"
              disabled={isLoading}
            >
              {isLoading ? <CircularProgress size={20} /> : 'Login'}
            </Button>
          </form>
        </CardContent>
      </Paper>
    </Box>
  );
}
