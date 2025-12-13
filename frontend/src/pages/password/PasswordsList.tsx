import AddIcon from '@mui/icons-material/Add';
import Autocomplete from '@mui/material/Autocomplete';
import Box from '@mui/material/Box';
import Fab from '@mui/material/Fab';
import TextField from '@mui/material/TextField';
import axios from 'axios';
import classnames from 'classnames/bind';
import { useState } from 'react';
import { useNavigate, useParams } from 'react-router';

import { usePasswordsStore, type PasswordSimple } from '@store/passwords';
import { useUserStore } from '@store/user';

import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

function PasswordsList() {
  const [isLoading, setIsLoading] = useState(false);

  const { passwords, setPasswords } = usePasswordsStore();
  const { accessToken } = useUserStore();
  const { passwordId } = useParams();
  const navigate = useNavigate();

  const fetchPasswords = async () => {
    if (!accessToken || passwords.length) return;
    setIsLoading(true);
    try {
      const response = await axios.get<PasswordSimple[]>(
        `${import.meta.env.VITE_API_HOST}/api/v1/password`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );
      setPasswords(response.data);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box className={cx('passwords-list-container')}>
      <Box className={cx('passwords-list-autocomplete-container')}>
        <Box className={cx('passwords-list-autocomplete-box')}>
          <Autocomplete
            fullWidth
            className={cx('passwords-list-autocomplete')}
            options={passwords}
            getOptionLabel={(option) => option.name}
            renderInput={(params) => <TextField {...params} label="Password" />}
            value={
              passwordId ? passwords.find((password) => password.id === Number(passwordId)) : null
            }
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
              <li {...props}>
                <img
                  src={`${import.meta.env.VITE_IMAGES_HOST}/${option.imageUrl}`}
                  alt={option.name}
                  style={{ marginRight: '0.5rem' }}
                  width={25}
                  height={25}
                />
                <span>{option.name}</span>
              </li>
            )}
          />
          <Box className={cx('passwords-list-fab-container')}>
            <Fab
              color="primary"
              aria-label="add"
              size="small"
              onClick={() => navigate('/password/create')}
            >
              <AddIcon />
            </Fab>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}

export default PasswordsList;
