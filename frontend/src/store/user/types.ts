export type User = {
  id: string;
  name: string;
  createdAt: string;
};

export type UserStore = {
  user: User | null;
  accessToken: string | null;
  isLoading: boolean;
  setIsLoading: (isLoading: boolean) => void;
  setAccessToken: (accessToken: string) => void;
  setUser: (user: User | null) => void;
  clearStore: () => void;
};
