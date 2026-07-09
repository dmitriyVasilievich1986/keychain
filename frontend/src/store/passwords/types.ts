/** Lightweight password entry used in list views. */
export type PasswordSimple = {
  /** Unique identifier of the password entry. */
  id: number;
  /** Display name of the password entry. */
  name: string;
  /** URL of the icon/logo associated with the entry. */
  imageUrl: string;
};

/** A single field belonging to a password entry (e.g. username, secret). */
export type PasswordField = {
  /** Unique identifier of the field. */
  id: number;
  /** Label of the field. */
  name: string;
  /** Whether the field has been marked as deleted. */
  isDeleted: boolean;
  /** Decrypted plaintext value of the field. */
  valueDecrypted: string;
  /** ISO timestamp of when the field was created. */
  createdAt: string;
};

/** A full password entry including all of its fields. */
export type Password = {
  /** Unique identifier of the password entry. */
  id: number;
  /** Display name of the password entry. */
  name: string;
  /** ISO timestamp of when the entry was created. */
  createdAt: string;
  /** URL of the icon/logo associated with the entry. */
  imageUrl: string;
  /** The fields (credentials/secrets) contained in this entry. */
  fields: PasswordField[];
};

/** Shape of the passwords store: entry state and its mutating actions. */
export type PasswordStore = {
  /** The list of passwords shown in the overview. */
  passwords: PasswordSimple[];
  /** The full password currently being viewed or edited, if any. */
  currentPassword: Password | null;
  /** Replaces the entire list of passwords. */
  setPasswords: (passwords: PasswordSimple[]) => void;
  /** Sets the currently selected password, or clears it when passed `null`. */
  setCurrentPassword: (password: Password | null) => void;
  /** Removes the password with the given id from the list. */
  removePassword: (id: number) => void;
  /** Appends a new password to the list. */
  addPassword: (password: PasswordSimple) => void;
  /** Adds a field to the current password. */
  addField: (field: PasswordField) => void;
  /** Updates the field identified by `id` on the current password. */
  updateField: (id: number, field: PasswordField) => void;
  /** Resets the store to its empty state. */
  clearStore: () => void;
};
