import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CardContent from '@mui/material/CardContent';
import CircularProgress from '@mui/material/CircularProgress';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import classnames from 'classnames/bind';
import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router';
import Cookies from 'js-cookie';
import { useAuthAPIClient } from '@utils/apiClient/auth';
import { Image } from '@components/image';

import { useUserStore } from '@store/user';

import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

export function Login() {
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  const { isLoading } = useUserStore();

  const [searchParams] = useSearchParams();
  const redirectTo = searchParams.get('redirectTo') ?? '/';

  const { login } = useAuthAPIClient();

  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    login(username, password)
      .then((response) => {
        Cookies.set('accessToken', response.accessToken);
        navigate(redirectTo);
      })
      .catch((error) => {
        setError(error.response.data.detail || 'An unknown error occurred');
      });
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
            <Image
              src={`${import.meta.env.VITE_IMAGES_HOST}/avatar.svg`}
              alt="avatar"
              width={100}
              height={100}
            />
          </Box>
          <form onSubmit={handleSubmit}>
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
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setError('');
                }}
                error={!!error}
                helperText={error}
                autoComplete="off"
                slotProps={{
                  input: {
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          aria-label="Toggle password visibility"
                        >
                          {showPassword ? <Visibility /> : <VisibilityOff />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  },
                }}
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
