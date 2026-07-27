# Keychain Frontend

A modern password management web application built with React and TypeScript.

## Description

Keychain Frontend is a secure password manager interface that allows users to store, manage, and organize their passwords. The application features user authentication, encrypted password storage, and an intuitive user interface built with Material-UI components.

## Tech Stack

- **React 19** - UI library
- **TypeScript** - Type-safe development
- **Vite+** - Unified toolchain (`vp`) for Vite, Oxlint, and Oxfmt
- **Material-UI (MUI)** - Component library
- **Zustand** - Lightweight state management
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Sass** - CSS preprocessor
- **Oxlint & Oxfmt** - Linting and formatting (via `vp lint` / `vp fmt`)

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── navbar/          # Navigation bar component
│   │   ├── protectedRoute/  # Route protection wrapper
│   │   ├── floatingButton/  # Floating action button
│   │   └── image/           # Image wrapper component
│   ├── pages/               # Page components
│   │   ├── login/           # Login page
│   │   ├── password/        # Password list and detail pages
│   │   │   └── passwordCard/ # Password card components
│   │   └── createPassword/  # Create password page
│   ├── store/               # Zustand state stores
│   │   ├── user/            # User authentication store
│   │   └── passwords/       # Passwords data store
│   ├── utils/               # Utility functions
│   │   └── apiClient/       # API client hooks (auth, user, password, field)
│   ├── App.tsx              # Main application component
│   └── main.tsx             # Application entry point
├── index.html               # HTML template
├── vite.config.ts           # Vite+, lint, fmt, and path aliases
├── tsconfig.json            # TypeScript project references
├── types/vite/client.d.ts   # Ambient asset / env typings
└── package.json             # Dependencies and scripts
```

## Path Aliases

The project uses path aliases for cleaner imports:

- `@components` → `./src/components`
- `@store` → `./src/store`
- `@pages` → `./src/pages`
- `@assets` → `./src/assets`
- `@utils` → `./src/utils`

## Getting Started

### Prerequisites

- Node.js 24
- npm 12.0.1 (see `package.json` `devEngines`; install with `npm install -g npm@12.0.1` if needed)

See also [AGENTS.md](./AGENTS.md) for Vite+ agent guidance.

### Installation

1. Install dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm run dev   # vp dev
```

The application will be available at `http://localhost:5173`

## Available Scripts

### Development

```bash
npm run dev
```

Starts the Vite+ development server (`vp dev`) with hot module replacement.

### Build

```bash
npm run build
```

Runs `tsc -b` then `vp build`. Output is written to `../static`.

### Preview

```bash
npm run preview
```

Previews the production build locally (`vp preview`).

### Lint & format

```bash
npm run lint:check     # vp lint .
npm run lint:fix       # vp lint . --fix
npm run format:check   # vp fmt --check .
npm run format:fix     # vp fmt .
npm run typecheck      # tsc --noEmit
npm run lint:all       # fmt + lint --fix + typecheck
```

## Usage Examples

### Authentication

Login is performed via the `useAuthAPIClient` hook, and the returned token is persisted with the user store (which syncs it to the `accessToken` cookie):

```typescript
import { useAuthAPIClient } from '@utils/apiClient';
import { useUserStore } from '@store/user';

function LoginComponent() {
  const { login } = useAuthAPIClient();
  const { setAccessToken } = useUserStore();

  const handleLogin = async (username: string, password: string) => {
    const { access_token } = await login(username, password);
    setAccessToken(access_token);
  };

  // Login form implementation
}
```

### Managing Passwords

Data is fetched through the `usePasswordAPIClient` hook, which populates the `usePasswordsStore` state:

```typescript
import { usePasswordAPIClient } from '@utils/apiClient';
import { usePasswordsStore } from '@store/passwords';

function PasswordsList() {
  const { getPasswords } = usePasswordAPIClient();
  const { passwords, setPasswords, removePassword } = usePasswordsStore();

  useEffect(() => {
    getPasswords(20, 0).then(({ data }) => setPasswords(data));
  }, []);

  return (
    <div>
      {passwords.map((password) => (
        <PasswordCard
          key={password.id}
          password={password}
          onDelete={() => removePassword(password.id)}
        />
      ))}
    </div>
  );
}
```

### Protected Routes

```typescript
import { ProtectedRoute } from '@components/protectedRoute';

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/password"
        element={
          <ProtectedRoute>
            <Password />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
```

### API Client

The API layer is exposed as hooks (not a bare client). Each hook returns typed methods that call the backend and, where relevant, sync the corresponding store. See `src/utils/apiClient/Readme.md` for details.

```typescript
import { usePasswordAPIClient } from '@utils/apiClient';

function Example() {
  const { getPassword, getPasswords, postPassword } = usePasswordAPIClient();

  // Fetch a single password by id
  const password = await getPassword(1);

  // Fetch a paginated, sorted list
  const { data, metadata } = await getPasswords(20, 0, 'name', 'asc');

  // Create a new password
  const created = await postPassword({
    name: 'My Password',
    imageUrl: 'https://example.com/icon.png',
  });
}
```

## Features

- User authentication and authorization
- Secure password storage and management
- Create and view passwords, with support for custom fields
- Protected routes for authenticated users
- Responsive Material-UI design
- Type-safe development with TypeScript
- State management with Zustand
- Clean and maintainable code structure

## Development Guidelines

1. Use TypeScript for all new files
2. Follow the established folder structure
3. Use path aliases for imports
4. Run `npm run lint:all` (or rely on repo pre-commit `vp fmt` / `vp lint`) before committing
5. Create reusable components in the `components/` directory
6. Keep business logic in Zustand stores
7. Use Material-UI components for consistency

## Build Configuration

The build outputs to `../static` directory with the following structure:

- `assets/` - Contains all compiled JS, CSS, and asset files with hash-based filenames for cache busting

## License

This project is private and proprietary.
