# Keychain Frontend

A modern password management web application built with React and TypeScript.

## Description

Keychain Frontend is a secure password manager interface that allows users to store, manage, and organize their passwords. The application features user authentication, encrypted password storage, and an intuitive user interface built with Material-UI components.

## Tech Stack

- **React 19** - UI library
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and development server
- **Material-UI (MUI)** - Component library
- **Zustand** - Lightweight state management
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Sass** - CSS preprocessor
- **ESLint & Prettier** - Code quality and formatting

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── navbar/          # Navigation bar component
│   │   ├── protectedRoute/  # Route protection wrapper
│   │   └── floatingButton/  # Floating action button
│   ├── pages/               # Page components
│   │   ├── login/           # Login page
│   │   ├── password/        # Password list and detail pages
│   │   │   └── passwordCard/ # Password card components
│   │   └── createPassword/  # Create password page
│   ├── store/               # Zustand state stores
│   │   ├── user/            # User authentication store
│   │   └── passwords/       # Passwords data store
│   ├── utils/               # Utility functions
│   │   └── apiClient/       # API client configuration
│   ├── App.tsx              # Main application component
│   └── main.tsx             # Application entry point
├── index.html               # HTML template
├── vite.config.ts           # Vite configuration
├── tsconfig.json            # TypeScript configuration
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

- Node.js (v18 or higher)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Available Scripts

### Development
```bash
npm run dev
```
Starts the Vite development server with hot module replacement.

### Build
```bash
npm run build
```
Compiles TypeScript and builds the application for production. Output is generated in the `../static` directory.

### Preview
```bash
npm run preview
```
Previews the production build locally.

### Linting
```bash
npm run lint:check    # Check for linting errors
npm run lint:fix      # Fix linting errors automatically
```

### Formatting
```bash
npm run format:check  # Check code formatting
npm run format:fix    # Format code automatically
```

## Usage Examples

### Authentication

```typescript
import { useUserStore } from '@store/user';

function LoginComponent() {
  const { login, isAuthenticated } = useUserStore();

  const handleLogin = async (username: string, password: string) => {
    await login(username, password);
  };

  return (
    // Login form implementation
  );
}
```

### Managing Passwords

```typescript
import { usePasswordsStore } from '@store/passwords';

function PasswordsList() {
  const { passwords, fetchPasswords, deletePassword } = usePasswordsStore();

  useEffect(() => {
    fetchPasswords();
  }, []);

  return (
    <div>
      {passwords.map(password => (
        <PasswordCard
          key={password.id}
          password={password}
          onDelete={deletePassword}
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

```typescript
import { apiClient } from '@utils/apiClient';

// GET request
const passwords = await apiClient.get('/api/passwords');

// POST request
const newPassword = await apiClient.post('/api/passwords', {
  title: 'My Password',
  username: 'user@example.com',
  password: 'securepass123'
});

// DELETE request
await apiClient.delete(`/api/passwords/${passwordId}`);
```

## Features

- User authentication and authorization
- Secure password storage and management
- Create, read, update, and delete passwords
- Protected routes for authenticated users
- Responsive Material-UI design
- Type-safe development with TypeScript
- State management with Zustand
- Clean and maintainable code structure

## Development Guidelines

1. Use TypeScript for all new files
2. Follow the established folder structure
3. Use path aliases for imports
4. Run linting and formatting before committing
5. Create reusable components in the `components/` directory
6. Keep business logic in Zustand stores
7. Use Material-UI components for consistency

## Build Configuration

The build outputs to `../static` directory with the following structure:
- `assets/` - Contains all compiled JS, CSS, and asset files with hash-based filenames for cache busting

## License

This project is private and proprietary.
