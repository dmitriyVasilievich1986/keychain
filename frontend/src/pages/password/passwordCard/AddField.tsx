import AddIcon from '@mui/icons-material/Add';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import Fab from '@mui/material/Fab';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import axios from 'axios';
import { useState } from 'react';

import { usePasswordsStore, type PasswordField } from '@store/passwords';
import { useUserStore } from '@store/user';

export function AddField() {
  const [fieldName, setFieldName] = useState<string>('');
  const [fieldValue, setFieldValue] = useState<string>('');
  const [newFieldError, setNewFieldError] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const { currentPassword, addField } = usePasswordsStore();
  const { accessToken } = useUserStore();

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
          passwordId: currentPassword!.id,
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
  );
}
