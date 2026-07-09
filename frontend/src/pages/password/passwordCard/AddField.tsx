import AddIcon from '@mui/icons-material/Add';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import { useState } from 'react';

import { FloatingButton } from '@components/floatingButton';
import { usePasswordsStore } from '@store/passwords';
import { useUserStore } from '@store/user';
import { useFieldAPIClient } from '@utils/apiClient/field';

export function AddField() {
  const [fieldName, setFieldName] = useState<string>('');
  const [fieldValue, setFieldValue] = useState<string>('');
  const [newFieldError, setNewFieldError] = useState<string>('');

  const { currentPassword, addField } = usePasswordsStore();
  const { isLoading } = useUserStore();
  const { postField } = useFieldAPIClient();

  const handleAddField = async () => {
    if (isLoading) return;
    if (!fieldName || !fieldValue) {
      setNewFieldError('Please fill in all fields');
      return;
    }
    postField({ passwordId: currentPassword!.id, name: fieldName, value: fieldValue })
      .then((response) => {
        addField(response);
        setFieldName('');
        setFieldValue('');
        setNewFieldError('');
      })
      .catch((error) => {
        console.error(error);
        setNewFieldError('Failed to add field');
      });
  };

  return (
    <Stack spacing={2} sx={{ marginTop: '2rem' }} direction="row" alignItems="center">
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
      <FloatingButton color="primary" onClick={handleAddField} disabled={isLoading}>
        <AddIcon />
      </FloatingButton>
    </Stack>
  );
}
