import Grid from '@mui/material/Grid';

import { PasswordCard } from './PasswordCard';
import PasswordsList from './PasswordsList';

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
