import AddIcon from '@mui/icons-material/Add';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import Divider from '@mui/material/Divider';
import Fab from '@mui/material/Fab';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import axios from 'axios';
import classnames from 'classnames/bind';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router';

import { usePasswordsStore, type Password, type PasswordField } from '@store/passwords';
import { useUserStore } from '@store/user';

import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

export function PasswordCard() {
  const [fieldName, setFieldName] = useState<string>('');
  const [fieldValue, setFieldValue] = useState<string>('');
  const [newFieldError, setNewFieldError] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const { passwordId } = useParams();
  const { currentPassword, setCurrentPassword, addField } = usePasswordsStore();
  const { accessToken } = useUserStore();

  useEffect(() => {
    if (!passwordId) {
      setCurrentPassword(null);
      return;
    }
    axios
      .get<Password>(`${import.meta.env.VITE_API_HOST}/api/v1/password/${passwordId}`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      })
      .then((response) => {
        setCurrentPassword(response.data);
      });
  }, [passwordId]);

  if (!currentPassword) return null;

  const handleAddField = async () => {
    if (isLoading) return;
    if (!fieldName || !fieldValue) {
      setNewFieldError('Please fill in all fields');
      return;
    }
    setIsLoading(true);
    try {
      const response = await axios.post<PasswordField>(
        `${import.meta.env.VITE_API_HOST}/api/v1/field`,
        {
          name: fieldName,
          value: fieldValue,
          passwordId: currentPassword.id,
        },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );
      addField({
        id: response.data.id,
        name: response.data.name,
        valueDecrypted: response.data.valueDecrypted,
        createdAt: response.data.createdAt,
        isDeleted: false,
      });
      setFieldName('');
      setFieldValue('');
      setNewFieldError('');
    } catch (error) {
      console.error(error);
      setNewFieldError('Failed to add field');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box sx={{ padding: '1rem' }}>
      <Paper elevation={10} sx={{ padding: '1rem' }}>
        <Box className={cx('password-card-header')}>
          <img
            src={`${import.meta.env.VITE_IMAGES_HOST}/${currentPassword.imageUrl}`}
            alt={currentPassword.name}
          />
          <Typography variant="h6">{currentPassword.name}</Typography>
        </Box>
        <Stack spacing={2} sx={{ marginTop: '2rem' }}>
          {currentPassword.fields
            .filter((f) => !f.isDeleted)
            .map((f) => (
              <TextField
                key={f.id}
                label={f.name}
                variant="outlined"
                value={f.valueDecrypted}
                slotProps={{
                  input: {
                    endAdornment: (
                      <ContentCopyIcon
                        onClick={() => navigator.clipboard.writeText(f.valueDecrypted)}
                        className={cx('copy-icon')}
                      />
                    ),
                  },
                }}
              />
            ))}
        </Stack>
        <Stack spacing={2} sx={{ marginTop: '2rem' }} direction="row">
          <TextField
            label="New field name"
            variant="outlined"
            value={fieldName}
            fullWidth
            onChange={(e) => setFieldName(e.target.value)}
            error={!!newFieldError}
            helperText={newFieldError}
          />
          <TextField
            label="New field value"
            variant="outlined"
            value={fieldValue}
            fullWidth
            onChange={(e) => setFieldValue(e.target.value)}
            error={!!newFieldError}
            helperText={newFieldError}
          />
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {isLoading ? (
              <CircularProgress size={20} />
            ) : (
              <Fab
                color="primary"
                aria-label="add"
                onClick={handleAddField}
                size="small"
                disabled={isLoading}
              >
                <AddIcon />
              </Fab>
            )}
          </Box>
        </Stack>
        <Divider sx={{ marginTop: '2rem' }}>Deleted Fields</Divider>
        <Stack spacing={2} sx={{ marginTop: '2rem' }}>
          {currentPassword.fields
            .filter((f) => f.isDeleted)
            .map((f) => (
              <TextField
                key={f.id}
                label={f.name}
                variant="outlined"
                fullWidth
                value={f.valueDecrypted}
                sx={{ textDecoration: 'line-through' }}
                disabled
                slotProps={{
                  input: {
                    endAdornment: (
                      <ContentCopyIcon
                        onClick={() => navigator.clipboard.writeText(f.valueDecrypted)}
                        className={cx('copy-icon')}
                      />
                    ),
                  },
                }}
              />
            ))}
        </Stack>
      </Paper>
    </Box>
  );
}
