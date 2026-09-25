/**
 * This file contains the types for the login page.
 * It is used to define the types for the login page.
 */

/**
 * State returned by the login form action.
 *
 * @property {string} error - Server or fallback error message to show on the form; empty when clear.
 */
export type LoginFormState = {
  error: string;
};
