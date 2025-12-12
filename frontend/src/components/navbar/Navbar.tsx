import AppBar from '@mui/material/AppBar';
import Container from '@mui/material/Container';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import axios from 'axios';
import classnames from 'classnames/bind';
import { useEffect } from 'react';

import { useUserStore, type User } from '@store/user';

import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

export function Navbar() {
  const { user, accessToken, setUser } = useUserStore();

  useEffect(() => {
    if (accessToken) {
      axios
        .get<User>(`${import.meta.env.VITE_API_HOST}/api/v1/user/me`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        })
        .then((response) => {
          setUser(response.data);
        })
        .catch((error) => {
          console.error(error);
        });
    }
  }, [accessToken]);

  return (
    <AppBar position="sticky">
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <div className={cx('navbar-inner')}>
            <div className={cx('navbar-brand')}>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                <a href="/password/" className={cx('navbar-link')}>
                  Password
                </a>
              </Typography>
            </div>
            <div>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                <a href="/logout" className={cx('navbar-link')}>
                  {user?.name}
                </a>
              </Typography>
            </div>
          </div>
        </Toolbar>
      </Container>
    </AppBar>
  );
}
