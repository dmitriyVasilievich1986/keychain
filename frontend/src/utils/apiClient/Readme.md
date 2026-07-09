# apiClient

A small, hook-based wrapper around [Axios](https://axios-http.com/) that centralizes how the frontend talks to the backend REST API. It handles authentication, global loading state, and error logging in one place, so feature code only deals with typed request/response payloads.

## Base client (`base.ts`)

The foundation everything else builds on.

- **`apiClientInstance`** — a pre-configured Axios instance pointed at `VITE_API_HOST` with JSON defaults. It has two interceptors:
  - **Request interceptor** — reads the `accessToken` cookie. If it is missing, the user is redirected to `/login?redirectTo=<current path>` and the request is aborted; otherwise it attaches an `Authorization: Bearer <token>` header.
  - **Response interceptor** — on an HTTP `401` it performs the same login redirect (skipped when already on `/login` to avoid loops), then rejects so callers still see the error.
- **`useApiClientWrapper()`** — a hook returning a `wrapper(func)` helper. It toggles the global loading flag (`useUserStore`) on for the duration of the wrapped promise, logs errors, and always resets loading afterward.

## Service clients (children)

Each child folder exposes a hook returning typed methods for one API resource. They call `apiClientInstance` and, where relevant, sync results into the corresponding store.

| Hook                   | Folder      | Methods                                       | Notes                                                                                                                            |
| ---------------------- | ----------- | --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `useAuthAPIClient`     | `auth/`     | `login`                                       | Uses a raw `axios.post` (not `apiClientInstance`) so the unauthenticated login call isn't redirected by the request interceptor. |
| `useUserAPIClient`     | `user/`     | `getUser`, `putUser`                          | `putUser` writes the updated user into the user store.                                                                           |
| `usePasswordAPIClient` | `password/` | `getPassword`, `getPasswords`, `postPassword` | `getPasswords` supports pagination, sorting, and filters; `postPassword` appends to the password store.                          |
| `useFieldAPIClient`    | `field/`    | `postField`, `putField`                       | Create/update fields belonging to a password.                                                                                    |

Shared types live in `types.ts` (`PaginationMetadata`, `FilterType`), and each service folder has its own `types.ts` for request/response shapes.

## Usage examples

Fetch the current user:

```tsx
import { useUserAPIClient } from '@utils/apiClient';

function Profile() {
  const { getUser } = useUserAPIClient();

  useEffect(() => {
    getUser().then((user) => console.log(user));
  }, []);
}
```

Log in:

```tsx
import { useAuthAPIClient } from '@utils/apiClient';

const { login } = useAuthAPIClient();
const { access_token } = await login('john', 's3cret');
```

List passwords with pagination and create a new one:

```tsx
import { usePasswordAPIClient } from '@utils/apiClient';

const { getPasswords, postPassword } = usePasswordAPIClient();

const { data, metadata } = await getPasswords(20, 0, 'name', 'asc');

await postPassword({ name: 'GitHub', imageUrl: 'https://github.com/icon.png' });
```
