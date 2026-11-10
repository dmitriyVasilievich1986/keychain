/**
 * This file contains the Field component.
 * It is used to render a single editable password field with its value history.
 */

import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import Accordion from '@mui/material/Accordion';
import AccordionDetails from '@mui/material/AccordionDetails';
import AccordionSummary from '@mui/material/AccordionSummary';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import dayjs from 'dayjs';
import { useState } from 'react';

import { type PasswordFieldValue } from '@store/passwords';

import {
  getCurrentValue,
  getHistoryValues,
  NAME_INPUT_SX,
  VALUE_INPUT_SX,
  type FieldDraft,
} from './fields';

import type { SxProps, Theme } from '@mui/material/styles';

/**
 * Masked text input with show/hide and copy-to-clipboard actions.
 *
 * @param props - Component props.
 * @param props.label - Input label.
 * @param props.value - Value shown in the input.
 * @param props.copyValue - Value copied to the clipboard.
 * @param props.onChange - Change handler; when omitted the input is read-only.
 * @param props.color - Input color, used to highlight unsaved edits.
 * @param props.error - Whether to show the input in an error state.
 * @param props.sx - Extra styles for the input root (e.g. its share of a row).
 * @returns The masked input.
 */
function SecretInput(props: {
  label: string;
  value: string;
  copyValue: string;
  onChange?: (value: string) => void;
  color?: 'primary' | 'secondary';
  error?: boolean;
  sx?: SxProps<Theme>;
}) {
  const [show, setShow] = useState<boolean>(false);

  return (
    <TextField
      label={props.label}
      type={show ? 'text' : 'password'}
      fullWidth
      variant="outlined"
      value={props.value}
      onChange={(e) => props.onChange?.(e.target.value)}
      color={props.color}
      error={props.error}
      sx={props.sx}
      slotProps={{
        input: {
          readOnly: !props.onChange,
          endAdornment: (
            <Stack direction="row" spacing={1}>
              <IconButton size="small" onClick={() => setShow(!show)}>
                {show ? <VisibilityIcon /> : <VisibilityOffIcon />}
              </IconButton>
              <IconButton onClick={() => navigator.clipboard.writeText(props.copyValue)}>
                <ContentCopyIcon />
              </IconButton>
            </Stack>
          ),
        },
      }}
    />
  );
}

/** Muted look for history rows, so they read as secondary to the editable current value. */
const HISTORY_INPUT_SX = {
  '& .MuiInputBase-input': { color: 'text.secondary' },
  '& .MuiInputLabel-root': { color: 'text.disabled' },
  '& .MuiOutlinedInput-notchedOutline': { borderColor: 'divider' },
  '& .MuiIconButton-root': { color: 'text.disabled' },
} as const;

/**
 * Read-only, muted row for a previous value of a field.
 *
 * @param props - Component props.
 * @param props.value - The historical value to display.
 * @returns The history row.
 */
function HistoryValue(props: { value: PasswordFieldValue }) {
  return (
    <SecretInput
      label={dayjs(props.value.createdAt).format('YYYY-MM-DD HH:mm')}
      value={props.value.value}
      copyValue={props.value.value}
      sx={HISTORY_INPUT_SX}
    />
  );
}

/**
 * Accordion for a single password field, controlled by the password card.
 *
 * The header holds the field's name and current value as editable inputs, laid out like the
 * add-field form. Edits are reported through `onChange` and saved by the card's single update
 * button; changed inputs use the secondary color. The accordion body lists the previous values,
 * newest first.
 *
 * @param props - Component props.
 * @param props.draft - The field's editable state.
 * @param props.onChange - Called with the updated draft on every edit.
 * @param props.showErrors - Whether to highlight empty inputs (after a failed save attempt).
 * @returns The field accordion.
 */
export function Field(props: {
  draft: FieldDraft;
  onChange: (draft: FieldDraft) => void;
  showErrors?: boolean;
}) {
  const { draft } = props;
  const savedName = draft.field?.name;
  const savedValue = draft.field ? getCurrentValue(draft.field) : undefined;
  const history = draft.field ? getHistoryValues(draft.field) : [];
  const isNew = !draft.field;

  return (
    <Accordion disableGutters sx={{ '&::before': { display: 'none' } }}>
      <AccordionSummary
        expandIcon={<ExpandMoreIcon />}
        aria-label={`${draft.name || 'New field'} history`}
        sx={{ '& .MuiAccordionSummary-content': { margin: '0.75rem 0' } }}
      >
        {/* Keep clicks on the inputs and buttons from toggling the accordion. */}
        <Stack
          spacing={2}
          direction="row"
          sx={{ alignItems: 'center', width: '100%', marginRight: '1rem' }}
          onClick={(e) => e.stopPropagation()}
          onFocus={(e) => e.stopPropagation()}
        >
          <TextField
            label="Field name"
            variant="outlined"
            value={draft.name}
            sx={NAME_INPUT_SX}
            onChange={(e) => props.onChange({ ...draft, name: e.target.value })}
            color={isNew || draft.name !== savedName ? 'secondary' : 'primary'}
            error={props.showErrors && !draft.name}
          />
          <SecretInput
            label="Field value"
            value={draft.value}
            copyValue={draft.value}
            onChange={(value) => props.onChange({ ...draft, value })}
            color={isNew || draft.value !== savedValue ? 'secondary' : 'primary'}
            error={props.showErrors && !draft.value}
            sx={VALUE_INPUT_SX}
          />
        </Stack>
      </AccordionSummary>
      <AccordionDetails>
        <Divider textAlign="left" sx={{ marginBottom: 2, color: 'text.disabled' }}>
          <Typography variant="caption">History</Typography>
        </Divider>
        {history.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            {isNew ? 'New field, not saved yet' : 'No previous values'}
          </Typography>
        ) : (
          <Stack spacing={2}>
            {history.map((item, index) => (
              <HistoryValue key={`${item.createdAt}-${index}`} value={item} />
            ))}
          </Stack>
        )}
      </AccordionDetails>
    </Accordion>
  );
}
