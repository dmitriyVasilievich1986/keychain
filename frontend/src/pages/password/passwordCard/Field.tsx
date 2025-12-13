import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import EditIcon from '@mui/icons-material/Edit';
import Box from '@mui/material/Box';
import Fab from '@mui/material/Fab';
import TextField from '@mui/material/TextField';
import axios from 'axios';
import classnames from 'classnames/bind';
import { useState } from 'react';

import { usePasswordsStore, type PasswordField } from '@store/passwords';
import { useUserStore } from '@store/user';

import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

export function Field(props: { field: PasswordField }) {
  const [value, setValue] = useState(props.field.valueDecrypted);
  const [isLoading, setIsLoading] = useState(false);
  const [updateFieldError, setUpdateFieldError] = useState<string>('');

  const { accessToken } = useUserStore();
  const { updateField } = usePasswordsStore();

  const handleUpdateField = async () => {
    if (isLoading) return;
    if (!value) {
      setUpdateFieldError('Please fill in all fields');
      return;
    }
    setIsLoading(true);
    try {
      const response = await axios.put<PasswordField>(
        `${import.meta.env.VITE_API_HOST}/api/v1/field/${props.field.id}`,
        { value },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );
      updateField(props.field.id, response.data);
      setValue(props.field.valueDecrypted);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center' }}>
      <TextField
        key={props.field.id}
        label={props.field.name}
        fullWidth
        variant="outlined"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        sx={{ textDecoration: props.field.isDeleted ? 'line-through' : 'none' }}
        disabled={props.field.isDeleted}
        color={value !== props.field.valueDecrypted ? 'secondary' : 'primary'}
        error={!!updateFieldError}
        helperText={updateFieldError}
        slotProps={{
          input: {
            endAdornment: (
              <ContentCopyIcon
                onClick={() => navigator.clipboard.writeText(props.field.valueDecrypted)}
                className={cx('copy-icon')}
              />
            ),
          },
        }}
      />
      {props.field.isDeleted ? null : (
        <Box sx={{ marginLeft: '1rem', width: '40px', height: '40px' }}>
          <Fab
            color="secondary"
            aria-label="edit"
            size="small"
            disabled={value === props.field.valueDecrypted}
            onClick={handleUpdateField}
          >
            <EditIcon />
          </Fab>
        </Box>
      )}
    </Box>
  );
}
