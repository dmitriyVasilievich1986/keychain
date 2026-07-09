/**
 * This file contains the Password component.
 * It is used to render the top-level password page layout.
 */

import Grid from '@mui/material/Grid';

import { PasswordCard } from './passwordCard';
import PasswordsList from './PasswordsList';

/**
 * Top-level password page layout.
 *
 * Arranges the passwords list and the selected password's card in a responsive
 * two-column grid that collapses to a single column on small screens.
 *
 * @returns The password page.
 */
export function Password() {
  return (
    <Grid container spacing={2}>
      <Grid size={{ xs: 12, md: 4 }}>
        <PasswordsList />
      </Grid>
      <Grid size={{ xs: 12, md: 8 }}>
        <PasswordCard />
      </Grid>
    </Grid>
  );
}
