/**
 * Response types for auth API calls to `/api/login`.
 */

/**
 * Successful payload from `POST /api/login`.
 *
 * @property {string} accessToken - JWT access token issued for the authenticated user.
 */
export type LoginResponse = {
  accessToken: string;
};
