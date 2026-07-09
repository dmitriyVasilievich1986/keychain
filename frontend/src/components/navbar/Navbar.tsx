/**
 * This file contains the Navbar component.
 * It is used to render the application top navigation bar.
 */

import LogoutIcon from '@mui/icons-material/Logout';
import AppBar from '@mui/material/AppBar';
import Container from '@mui/material/Container';
import IconButton from '@mui/material/IconButton';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import classnames from 'classnames/bind';
import Cookies from 'js-cookie';
import { useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router';

import { Image } from '@components/image';
import { useUserStore } from '@store/user';
import { useUserAPIClient } from '@utils/apiClient/user';

import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

/**
 * Application top navigation bar.
 *
 * Renders a sticky app bar with the Keychain brand (logo + link to the
 * passwords page). When an authenticated user is present, it also shows the
 * user's name and a logout button that navigates to the login page.
 *
 * On mount (and whenever the user or access token changes) it lazily fetches
 * the current user via the user API and populates the user store if a valid
 * `accessToken` cookie exists but the store is still empty.
 */
export function Navbar() {
  const { user, setUser } = useUserStore();
  const { getUser } = useUserAPIClient();
  const navigate = useNavigate();

  useEffect(() => {
    if (user === null && !!Cookies.get('accessToken')) {
      getUser().then((user) => {
        setUser(user);
      });
    }
  }, [user, Cookies.get('accessToken')]);

  return (
    <AppBar position="sticky">
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <div className={cx('navbar-inner')}>
            <div className={cx('navbar-brand')}>
              <Image
                src={`${import.meta.env.VITE_IMAGES_HOST}/padlock.png`}
                alt="padlock"
                width={20}
                height={20}
              />
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                <NavLink to="/password" className={cx('navbar-link')}>
                  Keychain
                </NavLink>
              </Typography>
            </div>
            {user !== null && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                  {user?.name}
                </Typography>
                <IconButton size="small" onClick={() => navigate('/login')}>
                  <LogoutIcon />
                </IconButton>
              </div>
            )}
          </div>
        </Toolbar>
      </Container>
    </AppBar>
  );
}
