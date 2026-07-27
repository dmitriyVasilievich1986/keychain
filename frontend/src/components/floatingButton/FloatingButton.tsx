/**
 * This file contains the FloatingButton component.
 * It is used to render a floating action button with a built-in loading state.
 */

import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import Fab from '@mui/material/Fab';
import classnames from 'classnames/bind';

import { useUserStore } from '@store/user';

import * as defaultStyle from './style.scss';

import type { FloatingButtonProps } from './types';

const cx = classnames.bind(defaultStyle);

/**
 * A floating action button (FAB) with a built-in loading state.
 *
 * While the user store reports a loading state, it renders a circular progress
 * spinner in place of the button; otherwise it renders a small MUI `Fab`.
 *
 * @param props.color - The FAB color theme, either `primary` or `secondary`.
 * @param props.children - The content rendered inside the FAB (typically an icon).
 * @param props.onClick - Handler invoked when the FAB is clicked.
 * @param props.disabled - When true, disables the FAB.
 */
export function FloatingButton(props: FloatingButtonProps) {
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
