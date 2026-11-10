/**
 * This file contains the AddField component.
 * It is used to render a form for adding a new field to the password card's unsaved changes.
 */

import AddIcon from '@mui/icons-material/Add';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import { useState } from 'react';

import { FloatingButton } from '@components/floatingButton';

import { NAME_INPUT_SX, VALUE_INPUT_SX } from './fields';

/**
 * Form row for adding a new field to the currently selected password.
 *
 * Renders name/value inputs plus an add button and manages the local input and validation state.
 * The field is not saved here: it is handed to `onAdd` and saved together with the other changes
 * by the card's update button.
 *
 * @param props - Component props.
 * @param props.onAdd - Called with the new field's name and value.
 * @returns The add-field form.
 */
export function AddField(props: { onAdd: (name: string, value: string) => void }) {
  const [fieldName, setFieldName] = useState<string>('');
  const [fieldValue, setFieldValue] = useState<string>('');
  const [newFieldError, setNewFieldError] = useState<string>('');

  /**
   * Validates the inputs, hands the new field to `onAdd` and resets the form. Requires both a
   * name and a value.
   */
  const handleAddField = () => {
    if (!fieldName || !fieldValue) {
      setNewFieldError('Please fill in all fields');
      return;
    }
    props.onAdd(fieldName, fieldValue);
    setFieldName('');
    setFieldValue('');
    setNewFieldError('');
  };

  return (
    <Stack spacing={2} sx={{ marginTop: '2rem', alignItems: 'center' }} direction="row">
      <TextField
        label="New field name"
        variant="outlined"
        value={fieldName}
        sx={NAME_INPUT_SX}
        onChange={(e) => setFieldName(e.target.value)}
        error={!!newFieldError}
        helperText={newFieldError}
      />
      <TextField
        label="New field value"
        variant="outlined"
        value={fieldValue}
        sx={VALUE_INPUT_SX}
        onChange={(e) => setFieldValue(e.target.value)}
        error={!!newFieldError}
        helperText={newFieldError}
      />
      <FloatingButton color="primary" onClick={handleAddField}>
        <AddIcon />
      </FloatingButton>
    </Stack>
  );
}
