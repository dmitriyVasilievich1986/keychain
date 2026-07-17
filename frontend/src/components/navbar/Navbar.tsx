/**
 * This file contains the Navbar component.
 * It is used to render the application top navigation bar.
 */

import padlock from '@assets/padlock.svg';
import AppBar from '@mui/material/AppBar';
import Container from '@mui/material/Container';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import classnames from 'classnames/bind';
import { NavLink } from 'react-router';

import { Image } from '@components/image';

import { LogoutMenu } from './components';
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
  return (
    <AppBar position="sticky">
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <div className={cx('navbar-inner')}>
            <div className={cx('navbar-brand')}>
              <Image src={padlock} alt="padlock" width={25} height={25} />
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                <NavLink to="/password" className={cx('navbar-link')}>
                  Keychain
                </NavLink>
              </Typography>
            </div>
            <LogoutMenu />
          </div>
        </Toolbar>
      </Container>
    </AppBar>
  );
}
