import { PostModal } from "../../postRequestModal";
import IconButton from "@mui/material/IconButton";
import EditIcon from "@mui/icons-material/Edit";
import TextField from "@mui/material/TextField";
import ListItem from "@mui/material/ListItem";
import Grid from "@mui/material/Grid2";
import React from "react";
import _ from "lodash";

export function ModifyField(props) {
  if (props?.putHandler === undefined) return null;

  const [open, setOpen] = React.useState(false);
  const [value, setValue] = React.useState(props.field.get_value);

  const putHandler = () => {
    setOpen(false);
    props.putHandler(props.field.id, value);
    setValue("");
  };

  return (
    <>
      <Grid size={6}>
        <IconButton onClick={() => setOpen(true)} aria-label="edit" edge="end">
          <EditIcon />
        </IconButton>
      </Grid>
      <PostModal
        closeHandler={() => setOpen(false)}
        header="Modify password item"
        clickHandler={putHandler}
        postButtonLabel="Update"
        open={open}
      >
        <ListItem>
          <TextField
            onChange={(e) => setValue(e.target.value)}
            label={props.field.name}
            variant="outlined"
            fullWidth={true}
            value={value}
          />
        </ListItem>
      </PostModal>
    </>
  );
}
