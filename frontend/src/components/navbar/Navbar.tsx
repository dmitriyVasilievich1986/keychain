import AppBar from '@mui/material/AppBar';
import Container from '@mui/material/Container';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import classnames from 'classnames/bind';
import { useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router';
import Cookies from 'js-cookie';
import LogoutIcon from '@mui/icons-material/Logout';

import { useUserStore } from '@store/user';
import { useUserAPIClient } from '@utils/apiClient/user';
import { useClearStore } from '@utils/useClearStore';
import IconButton from '@mui/material/IconButton';
import { Image } from '@components/image';

import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

export function Navbar() {
  const { user, setUser } = useUserStore();
  const { getUser } = useUserAPIClient();
  const navigate = useNavigate();
  const { clearAllStores } = useClearStore();

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
                <IconButton
                  size="small"
                  onClick={() => {
                    clearAllStores();
                    navigate('/login');
                  }}
                >
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
