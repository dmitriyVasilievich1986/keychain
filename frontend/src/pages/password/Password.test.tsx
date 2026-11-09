/**
 * Tests for the Password page layout.
 */

import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vite-plus/test';

import { Password } from './Password';

vi.mock('./PasswordsList', () => ({ default: () => <div>passwords list</div> }));
vi.mock('./passwordCard', () => ({ PasswordCard: () => <div>password card</div> }));

describe('Password', () => {
  afterEach(() => {
    cleanup();
  });

  it('renders the passwords list next to the password card', () => {
    render(<Password />);

    expect(screen.getByText('passwords list')).toBeInTheDocument();
    expect(screen.getByText('password card')).toBeInTheDocument();
  });
});
