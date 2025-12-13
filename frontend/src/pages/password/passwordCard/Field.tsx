import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import TextField from '@mui/material/TextField';
import classnames from 'classnames/bind';

import type { PasswordField } from '@store/passwords';

import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

export function Field(props: { field: PasswordField }) {
  return (
    <TextField
      key={props.field.id}
      label={props.field.name}
      variant="outlined"
      value={props.field.valueDecrypted}
      sx={{ textDecoration: props.field.isDeleted ? 'line-through' : 'none' }}
      disabled={props.field.isDeleted}
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
  );
}
