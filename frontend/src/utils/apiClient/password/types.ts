/**
 * Request types for password calls to `/api/v1/password`.
 *
 * Fields are embedded in the password: they are sent as a whole list on create, full update and
 * (optionally) patch, and the list order defines each field's position.
 */

/**
 * A single value sent for a password field.
 *
 * @property {string} value - Plaintext value of the field.
 */
export type PasswordFieldValueRequest = {
  value: string;
};

/**
 * A field sent as part of a password create/update/patch request.
 *
 * @property {string} name - Label of the field (at least 1 character).
 * @property {PasswordFieldValueRequest[]} values - Values of the field, at least one; order is preserved.
 */
export type PasswordFieldRequest = {
  name: string;
  values: PasswordFieldValueRequest[];
};

/**
 * Payload for creating a password (`POST /api/v1/password`).
 *
 * @property {string} name - Display name of the password (at least 1 character).
 * @property {string | null} [imageUrl] - URL of the password image; omitted or `null` for none.
 * @property {PasswordFieldRequest[]} [fields] - Fields of the password; defaults to an empty list.
 */
export type PasswordPostRequest = {
  name: string;
  imageUrl?: string | null;
  fields?: PasswordFieldRequest[];
};

/**
 * Payload for fully replacing a password (`PUT /api/v1/password/{id}`). All properties are required.
 *
 * @property {string} name - Display name of the password.
 * @property {string | null} imageUrl - URL of the password image, or `null` for none.
 * @property {PasswordFieldRequest[]} fields - Full list of fields; replaces the existing ones.
 */
export type PasswordPutRequest = {
  name: string;
  imageUrl: string | null;
  fields: PasswordFieldRequest[];
};

/**
 * Payload for partially updating a password (`PATCH /api/v1/password/{id}`). Only the provided
 * properties are changed; `imageUrl: null` removes the image, and `fields`, when sent, replaces the
 * whole field list.
 */
export type PasswordPatchRequest = Partial<PasswordPutRequest>;

/** Columns the password list can be sorted by. */
export type PasswordSortBy = 'id' | 'name' | 'created_at';

/** Sort direction accepted by the password list. */
export type PasswordSortOrder = 'asc' | 'desc';
