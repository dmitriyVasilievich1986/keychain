/**
 * Tests for Navbar: brand rendering and the user menu slot.
 */

import { cleanup, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { afterEach, describe, expect, it, vi } from 'vite-plus/test';

import { Navbar } from './Navbar';

vi.mock('./components', () => ({
  LogoutMenu: () => <div>user menu</div>,
}));

describe('Navbar', () => {
  afterEach(() => {
    cleanup();
  });

  it('renders the brand logo, a link to the passwords page, and the user menu', () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );

    expect(screen.getByAltText('padlock')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Keychain' })).toHaveAttribute('href', '/password');
    expect(screen.getByText('user menu')).toBeInTheDocument();
  });
});
