/**
 * @fileoverview Application entry point.
 *
 * Mounts the React tree onto the `#root` DOM node, wrapping {@link App} in
 * {@link BrowserRouter} for client-side routing and {@link StrictMode} to
 * surface potential problems during development.
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router';

import './index.css';
import App from './App.tsx';

/**
 * Application entry point.
 *
 * Mounts the React tree onto the `#root` DOM node, wrapping {@link App} in
 * {@link BrowserRouter} for client-side routing and {@link StrictMode} to
 * surface potential problems during development.
 */
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>
);
