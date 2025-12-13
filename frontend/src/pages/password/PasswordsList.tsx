import Autocomplete from '@mui/material/Autocomplete';
import Box from '@mui/material/Box';
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
      <Autocomplete
        className={cx('passwords-list-autocomplete')}
        options={passwords}
        getOptionLabel={(option) => option.name}
        renderInput={(params) => <TextField {...params} label="Password" />}
        value={passwordId ? passwords.find((password) => password.id === Number(passwordId)) : null}
        onOpen={fetchPasswords}
        loading={isLoading}
        onChange={(_, value) => {
          if (value) {
            navigate(`/password/${value.id}`);
          } else {
            navigate('/password');
          }
        }}
      />
    </Box>
  );
}

export default PasswordsList;
