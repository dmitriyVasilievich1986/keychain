import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import Fab from '@mui/material/Fab';
import classnames from 'classnames/bind';

import { useUserStore } from '@store/user';

import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

export function FloatingButton(props: {
  color: 'primary' | 'secondary';
  children: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
}) {
  const { isLoading } = useUserStore();

  return (
    <Box className={cx('floating-button-container')}>
      {isLoading ? (
        <CircularProgress size={20} />
      ) : (
        <Fab
          color={props.color}
          aria-label="edit"
          size="small"
          onClick={props.onClick}
          disabled={props.disabled}
        >
          {props.children}
        </Fab>
      )}
    </Box>
  );
}
