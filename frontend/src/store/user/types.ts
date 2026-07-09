/** A registered application user. */
export type User = {
  /** Unique identifier of the user. */
  id: string;
  /** Display name of the user. */
  name: string;
  /** ISO timestamp of when the user account was created. */
  createdAt: string;
};

/** Shape of the user store: authentication state and its mutating actions. */
export type UserStore = {
  /** The currently authenticated user, or `null` when signed out. */
  user: User | null;
  /** The active access token, or `null` when not authenticated. */
  accessToken: string | null;
  /** Whether an auth-related request is in progress. */
  isLoading: boolean;
  /** Sets the global loading flag. */
  setIsLoading: (isLoading: boolean) => void;
  /** Persists the access token and updates the store. */
  setAccessToken: (accessToken: string) => void;
  /** Sets the current user, or clears it when passed `null`. */
  setUser: (user: User | null) => void;
  /** Resets the store to its signed-out state. */
  clearStore: () => void;
};
