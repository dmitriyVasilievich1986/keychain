/**
 * Request body types for user profile updates to `/api/v1/user`.
 */

/**
 * Payload for replacing editable profile fields (`PUT /api/v1/user`).
 *
 * @property {string} name - User's name.
 */
export type UserPutRequest = {
  name: string;
};
