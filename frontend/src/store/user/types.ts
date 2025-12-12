export type User = {
  id: string;
  name: string;
  createdAt: string;
};

export type UserStore = {
  user: User | null;
  accessToken: string | null;
  setAccessToken: (accessToken: string) => void;
  setUser: (user: User) => void;
};
