/**
 * Tests for FloatingButton: click handling, disabled state, and the global loading spinner.
 */

import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { useUserStore } from '@store/user';

import { FloatingButton } from './FloatingButton';

describe('FloatingButton', () => {
  beforeEach(() => {
    useUserStore.setState({ isLoading: false });
  });

  afterEach(() => {
    cleanup();
  });

  it('renders its children and calls onClick', async () => {
    const onClick = vi.fn();
    render(
      <FloatingButton color="primary" onClick={onClick}>
        <span>add</span>
      </FloatingButton>
    );

    await userEvent.click(screen.getByRole('button', { name: 'edit' }));

    expect(screen.getByText('add')).toBeInTheDocument();
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when disabled', () => {
    const onClick = vi.fn();
    render(
      <FloatingButton color="secondary" onClick={onClick} disabled>
        <span>add</span>
      </FloatingButton>
    );

    const button = screen.getByRole('button', { name: 'edit' });
    expect(button).toBeDisabled();
    // userEvent refuses to click `pointer-events: none` elements, so dispatch directly.
    fireEvent.click(button);

    expect(onClick).not.toHaveBeenCalled();
  });

  it('shows a spinner instead of the button while loading', () => {
    useUserStore.setState({ isLoading: true });
    render(
      <FloatingButton color="primary" onClick={vi.fn()}>
        <span>add</span>
      </FloatingButton>
    );

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });
});
