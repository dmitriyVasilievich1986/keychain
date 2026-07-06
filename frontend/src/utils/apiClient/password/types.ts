/**
 * Request body types for password create and update calls to `/api/v1/password`.
 */

/**
 * Payload for creating a password (`POST /api/v1/password`).
 *
 * @property {string} name - Display name of the password.
 * @property {string} imageUrl - URL of the password image.
 */
export type PasswordPostRequest = {
  name: string;
  imageUrl: string;
};
