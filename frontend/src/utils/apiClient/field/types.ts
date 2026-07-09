/**
 * Request body types for field create and update calls to `/api/v1/field`.
 */

/**
 * Payload for creating a field (`POST /api/v1/field`).
 *
 * @property {string} value - The new value of the field.
 * @property {number} passwordId - The ID of the password that the field belongs to.
 * @property {string} name - The name of the field.
 */
export type FieldPostRequest = {
  passwordId: number;
  name: string;
  value: string;
};

export type FieldPutRequest = {
  value: string;
};
