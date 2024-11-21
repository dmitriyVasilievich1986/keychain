import { PostModal } from "../../postRequestModal";
import TextField from "@mui/material/TextField";
import AddIcon from "@mui/icons-material/Add";
import ListItem from "@mui/material/ListItem";
import Fab from "@mui/material/Fab";
import React from "react";
import _ from "lodash";

export function AddField(props) {
  const [open, setOpen] = React.useState(false);
  const [value, setValue] = React.useState("");
  const [name, setName] = React.useState("");

  const postHandler = () => {
    setOpen(false);
    props.postHandler(name, value);
    setValue("");
    setName("");
  };

  return (
    <>
      <ListItem
        sx={{ height: "70px" }}
        secondaryAction={
          <Fab
            onClick={() => setOpen(true)}
            aria-label="add"
            color="primary"
            size="small"
          >
            <AddIcon />
          </Fab>
        }
      />
      <PostModal
        closeHandler={() => setOpen(false)}
        header="Create new password item"
        clickHandler={postHandler}
        postButtonLabel="Create"
        open={open}
      >
        <ListItem>
          <TextField
            onChange={(e) => setName(e.target.value)}
            variant="outlined"
            fullWidth={true}
            value={name}
            label="name"
          />
        </ListItem>
        <ListItem>
          <TextField
            onChange={(e) => setValue(e.target.value)}
            variant="outlined"
            fullWidth={true}
            value={value}
            label="value"
          />
        </ListItem>
      </PostModal>
    </>
  );
}
