/**
 * Response types for auth API calls to `/api/v1/user/login`.
 */

/**
 * Successful payload from `POST /api/v1/user/login`.
 *
 * @property {string} accessToken - JWT access token issued for the authenticated user.
 * @property {string} expiresAt - ISO 8601 timestamp at which the access token expires.
 */
export type LoginResponse = {
  accessToken: string;
  expiresAt: string;
};
