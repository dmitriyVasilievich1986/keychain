import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import classnames from 'classnames/bind';
import { useEffect } from 'react';
import { useParams } from 'react-router';

import { usePasswordsStore } from '@store/passwords';
import { useUserStore } from '@store/user';

import { AddField } from './AddField';
import { Field } from './Field';
import { usePasswordAPIClient } from '@utils/apiClient/password';
import * as defaultStyle from './style.scss';
import Skeleton from '@mui/material/Skeleton';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { Image } from '@components/image';

import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';

const cx = classnames.bind(defaultStyle);

export function PasswordCard() {
  const { passwordId } = useParams();
  const { currentPassword, setCurrentPassword } = usePasswordsStore();
  const { isLoading } = useUserStore();
  const { getPassword } = usePasswordAPIClient();

  useEffect(() => {
    if (!passwordId) {
      setCurrentPassword(null);
      return;
    }
    if (currentPassword !== null) return;
    getPassword(parseInt(passwordId))
      .then((response) => {
        setCurrentPassword(response);
      })
      .catch((error) => {
        console.error(error);
      });
  }, [passwordId, currentPassword]);

  if (!currentPassword) return null;
  if (isLoading) {
    return (
      <Box sx={{ padding: '1rem' }}>
        <Skeleton variant="rectangular" width="100%" height={400} />
      </Box>
    );
  }

  return (
    <Box sx={{ padding: '1rem' }}>
      <Paper elevation={10} sx={{ padding: '1rem' }}>
        <Box className={cx('password-card-header')}>
          <Image
            src={`${import.meta.env.VITE_IMAGES_HOST}/${currentPassword.imageUrl}`}
            alt={currentPassword.name}
            width={25}
            height={25}
          />
          <Typography variant="h6">{currentPassword.name}</Typography>
        </Box>
        <Stack spacing={2} sx={{ marginTop: '2rem' }}>
          {currentPassword.fields
            .filter((f) => !f.isDeleted)
            .map((f) => (
              <Field key={f.id} field={f} />
            ))}
        </Stack>
        <AddField />
        <Accordion sx={{ '&::before': { display: 'none' }, marginTop: '2rem' }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>Deleted Fields</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Stack spacing={2} sx={{ marginTop: '2rem' }}>
              {currentPassword.fields
                .filter((f) => f.isDeleted)
                .map((f) => (
                  <Field key={f.id} field={f} />
                ))}
            </Stack>
          </AccordionDetails>
        </Accordion>
      </Paper>
    </Box>
  );
}
