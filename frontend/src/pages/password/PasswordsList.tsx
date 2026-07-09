/**
 * This file contains the PasswordsList component.
 * It is used to render a searchable list of the user's saved passwords.
 */

import AddIcon from '@mui/icons-material/Add';
import Autocomplete from '@mui/material/Autocomplete';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import classnames from 'classnames/bind';
import { useNavigate } from 'react-router';

import { FloatingButton } from '@components/floatingButton';
import { Image } from '@components/image';
import { usePasswordsStore } from '@store/passwords';
import { useUserStore } from '@store/user';
import { usePasswordAPIClient } from '@utils/apiClient/password';

import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

/**
 * Page component that renders a searchable list of the user's saved passwords.
 *
 * Displays an autocomplete field for selecting a password (navigating to its
 * detail view on selection) alongside a floating button for creating a new one.
 *
 * @returns The passwords list page.
 */
function PasswordsList() {
  const { passwords, setPasswords, currentPassword } = usePasswordsStore();
  const { isLoading } = useUserStore();
  const navigate = useNavigate();
  const { getPasswords } = usePasswordAPIClient();

  /**
   * Lazily loads the passwords from the API and stores them.
   *
   * Only performs the request when no passwords have been fetched yet, avoiding
   * redundant calls each time the autocomplete is opened. Errors are logged.
   */
  const fetchPasswords = () => {
    if (passwords.length === 0) {
      getPasswords()
        .then((response) => {
          setPasswords(response.data);
        })
        .catch((error) => {
          console.error(error);
        });
    }
  };

  return (
    <Box className={cx('passwords-list-container')}>
      <Stack spacing={2} direction="row" className={cx('passwords-list-autocomplete-container')}>
        <Autocomplete
          fullWidth
          options={passwords}
          getOptionLabel={(option) => option.name}
          renderInput={(params) => <TextField {...params} label="Password" />}
          value={currentPassword}
          onOpen={fetchPasswords}
          loading={isLoading}
          onChange={(_, value) => {
            if (value) {
              navigate(`/password/${value.id}`);
            } else {
              navigate('/password');
            }
          }}
          renderOption={(props, option) => (
            <li {...props} key={option.id}>
              <Image
                src={`${import.meta.env.VITE_IMAGES_HOST}/${option.imageUrl}`}
                alt={option.name}
                width={25}
                height={25}
              />
              <span style={{ marginLeft: '0.5rem' }}>{option.name}</span>
            </li>
          )}
        />
        <FloatingButton onClick={() => navigate('/password/create')} color="primary">
          <AddIcon />
        </FloatingButton>
      </Stack>
    </Box>
  );
}

export default PasswordsList;
