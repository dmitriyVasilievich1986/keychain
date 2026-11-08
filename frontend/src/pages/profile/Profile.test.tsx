/**
 * Tests for the Profile page.
 */

import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it } from 'vite-plus/test';

import { useUserStore } from '@store/user';

import { Profile } from './Profile';

describe('Profile', () => {
  afterEach(() => {
    cleanup();
  });

  it("shows the current user's name as the page heading", () => {
    useUserStore.setState({
      user: { id: 'u-1', name: 'Alice', createdAt: '2026-01-01T00:00:00Z' },
    });

    render(<Profile />);

    expect(screen.getByRole('heading', { level: 1, name: 'Alice' })).toBeInTheDocument();
  });
});
