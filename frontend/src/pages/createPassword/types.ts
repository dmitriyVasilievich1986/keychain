/**
 * This file contains the types for the create password page.
 */

/**
 * State returned by the create-password form action.
 *
 * @property {string} error - Error message to show on the form; empty when clear.
 */
export type CreatePasswordFormState = {
  error: string;
};
