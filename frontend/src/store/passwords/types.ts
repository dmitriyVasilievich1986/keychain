export type PasswordSimple = {
  id: number;
  name: string;
  imageUrl: string;
};

export type PasswordField = {
  id: number;
  name: string;
  isDeleted: boolean;
  valueDecrypted: string;
  createdAt: string;
};

export type Password = {
  id: number;
  name: string;
  createdAt: string;
  imageUrl: string;
  fields: PasswordField[];
};

export type PasswordStore = {
  passwords: PasswordSimple[];
  currentPassword: Password | null;
  setPasswords: (passwords: PasswordSimple[]) => void;
  setCurrentPassword: (password: Password | null) => void;
  removePassword: (id: number) => void;
  addPassword: (password: PasswordSimple) => void;
  addField: (field: PasswordField) => void;
  updateField: (id: number, field: PasswordField) => void;
};
