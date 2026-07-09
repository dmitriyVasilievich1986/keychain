/**
 * This file contains the LogoutMenu component.
 */

import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import Cookies from 'js-cookie';
import { useEffect, useId, useState } from 'react';
import { useNavigate } from 'react-router';

import { useUserStore } from '@store/user';
import { useUserAPIClient } from '@utils/apiClient/user';
import { version } from '@utils/application-version.json';

/**
 * Navbar user menu showing the current user's name and account actions.
 *
 * Displays the signed-in user's name as a button that opens a dropdown menu
 * with navigation to the profile page, a logout action, and the current
 * application version. If no user is loaded but an `accessToken` cookie is
 * present, it fetches the user and hydrates the user store. Renders nothing
 * while there is no authenticated user.
 *
 * @returns The user menu, or `null` when no user is available.
 */
export function LogoutMenu() {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const { user, setUser } = useUserStore();
  const { getUser } = useUserAPIClient();
  const navigate = useNavigate();

  const open = Boolean(anchorEl);
  const id = useId();
  const buttonId = `${id}-button`;
  const menuId = `${id}-menu`;

  useEffect(() => {
    if (user === null && !!Cookies.get('accessToken')) {
      getUser().then((user) => {
        setUser(user);
      });
    }
  }, [user, Cookies.get('accessToken')]);

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleProfile = () => {
    handleClose();
    navigate('/profile');
  };

  const handlePasswords = () => {
    handleClose();
    navigate('/passwords');
  };

  const handleLogout = () => {
    handleClose();
    navigate('/login');
  };

  if (user === null) return null;
  return (
    <>
      <IconButton
        id={buttonId}
        aria-controls={open ? menuId : undefined}
        aria-haspopup="true"
        aria-expanded={open}
        onClick={handleClick}
      >
        <Typography variant="h6" component="div" sx={{ flexGrow: 1, color: 'white' }}>
          {user?.name}
        </Typography>
      </IconButton>
      <Menu
        id={menuId}
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        slotProps={{
          list: {
            'aria-labelledby': buttonId,
          },
        }}
      >
        <MenuItem onClick={handleProfile}>Profile</MenuItem>
        <MenuItem onClick={handlePasswords}>Passwords</MenuItem>
        <MenuItem onClick={handleLogout}>Logout</MenuItem>
        <Divider />
        <Typography
          variant="subtitle2"
          align="center"
          component="div"
          sx={{ color: 'text.secondary', px: 2 }}
        >
          version: {version}
        </Typography>
      </Menu>
    </>
  );
}
