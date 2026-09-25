/**
 * This file contains the Login component.
 * It is used to render the login page.
 */

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
import axios from 'axios';
import classnames from 'classnames/bind';
import dayjs from 'dayjs';
import Cookies from 'js-cookie';
import { useState, useEffect, useActionState } from 'react';
import { useNavigate, useSearchParams } from 'react-router';

import avatar from '@assets/avatar.svg';
import { Image } from '@components/image';
import { useAuthAPIClient } from '@utils/apiClient/auth';
import { useClearStore } from '@utils/useClearStore';

import * as defaultStyle from './style.scss';

import type { LoginFormState } from './types';

const cx = classnames.bind(defaultStyle);

/**
 * Login page.
 *
 * Renders the username/password form with a show/hide password toggle, clears
 * any existing store state on mount, authenticates on submit via
 * `useActionState`, and redirects to the `redirectTo` query param (defaulting
 * to `/`) on success.
 *
 * @returns The login page.
 */
export function Login() {
  const [showPassword, setShowPassword] = useState(false);
  const [isDirty, setIsDirty] = useState(false);
  const { clearAllStores } = useClearStore();

  const [searchParams] = useSearchParams();
  const redirectTo = searchParams.get('redirectTo') ?? '/';

  const { login } = useAuthAPIClient();
  const navigate = useNavigate();

  // Reset all stores on mount so no stale session data leaks into a new login.
  useEffect(() => {
    clearAllStores();
  }, []);

  const [state, formAction, isPending] = useActionState(
    async (_prevState: LoginFormState, formData: FormData): Promise<LoginFormState> => {
      const username = String(formData.get('username') ?? '');
      const password = String(formData.get('password') ?? '');

      try {
        const response = await login(username, password);
        Cookies.set('accessToken', response.accessToken, {
          expires: dayjs(response.expiresAt).toDate(),
        });
        navigate(redirectTo);
        return { error: '' };
      } catch (error: unknown) {
        if (axios.isAxiosError(error)) {
          return {
            error:
              (error.response?.data as { detail?: string } | undefined)?.detail ||
              'An unknown error occurred',
          };
        }
        return { error: 'An unknown error occurred' };
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
            <Image src={avatar} alt="avatar" width={100} height={100} />
          </Box>
          <form action={formAction}>
            <Stack spacing={2} sx={{ marginTop: '1rem' }}>
              <TextField
                name="username"
                label="Login"
                variant="outlined"
                fullWidth
                error={!!error}
                helperText={error}
                disabled={isPending}
                onChange={() => setIsDirty(true)}
              />
              <TextField
                name="password"
                label="Password"
                variant="outlined"
                fullWidth
                type={showPassword ? 'text' : 'password'}
                error={!!error}
                helperText={error}
                autoComplete="off"
                onChange={() => setIsDirty(true)}
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
                disabled={isPending}
              />
            </Stack>
            <Button
              variant="contained"
              fullWidth
              sx={{ marginTop: '2rem' }}
              type="submit"
              disabled={isPending}
            >
              {isPending ? <CircularProgress size={20} /> : 'Login'}
            </Button>
          </form>
        </CardContent>
      </Paper>
    </Box>
  );
}
