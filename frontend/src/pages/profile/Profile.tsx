/**
 * This file contains the Profile page.
 */

import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';

import { useUserStore } from '@store/user';

/**
 * Profile page displaying the current user's details.
 *
 * Reads the authenticated user from the user store and renders their name in a
 * centered card. Expects a user to be present (typically guaranteed by the
 * route guard), so it accesses the user non-null.
 *
 * @returns The profile page content.
 */
export function Profile() {
  const { user } = useUserStore();

  return (
    <Container maxWidth="md">
      <Paper sx={{ my: 4, p: 2 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          {user!.name}
        </Typography>
      </Paper>
    </Container>
  );
}
