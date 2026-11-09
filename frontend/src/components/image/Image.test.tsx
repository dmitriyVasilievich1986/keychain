/**
 * Tests for Image: lazy <img> rendering and the storefront icon fallback.
 */

import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it } from 'vite-plus/test';

import { Image } from './Image';

describe('Image', () => {
  afterEach(() => {
    cleanup();
  });

  it('renders a lazy image with the given size and alt text', () => {
    render(<Image src="https://example.com/logo.png" alt="logo" width={25} height={30} />);

    const img = screen.getByAltText('logo');
    expect(img).toHaveAttribute('src', 'https://example.com/logo.png');
    expect(img).toHaveAttribute('loading', 'lazy');
    expect(img).toHaveStyle({ width: '25px', height: '30px' });
  });

  it('uses a default alt text', () => {
    render(<Image src="https://example.com/logo.png" />);

    expect(screen.getByAltText('Image')).toBeInTheDocument();
  });

  it('shows the fallback icon when there is no src', () => {
    render(<Image src={null} alt="logo" />);

    expect(screen.queryByRole('img')).not.toBeInTheDocument();
    expect(screen.getByTestId('StorefrontIcon')).toHaveAttribute('aria-label', 'logo');
  });

  it('uses a default label for the fallback icon', () => {
    render(<Image />);

    expect(screen.getByTestId('StorefrontIcon')).toHaveAttribute('aria-label', 'Storefront icon');
  });

  it('switches to the fallback icon when the image fails to load', () => {
    render(<Image src="https://example.com/broken.png" alt="logo" />);

    fireEvent.error(screen.getByAltText('logo'));

    expect(screen.queryByAltText('logo')).not.toBeInTheDocument();
    expect(screen.getByTestId('StorefrontIcon')).toBeInTheDocument();
  });
});
