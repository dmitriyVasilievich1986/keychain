import { PostModal } from "../../postRequestModal";
import TextField from "@mui/material/TextField";
import AddIcon from "@mui/icons-material/Add";
import ListItem from "@mui/material/ListItem";
import classnames from "classnames/bind";
import * as style from "./style.scss";
import Fab from "@mui/material/Fab";
import React from "react";
import _ from "lodash";

const cx = classnames.bind(style);

export function AddPassword(props) {
  const [open, setOpen] = React.useState(false);
  const [image_url, setImageUrl] = React.useState("");
  const [name, setName] = React.useState("");

  const postHandler = () => {
    setOpen(false);
    props.postHandler(name, image_url);
    setImageUrl("");
    setName("");
  };

  return (
    <div className={cx("add-password-container")}>
      <Fab
        onClick={() => setOpen(true)}
        aria-label="add"
        color="primary"
        size="small"
      >
        <AddIcon />
      </Fab>
      <PostModal
        closeHandler={() => setOpen(false)}
        header="Create new password"
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
            onChange={(e) => setImageUrl(e.target.value)}
            variant="outlined"
            label="image url"
            value={image_url}
            fullWidth={true}
          />
        </ListItem>
      </PostModal>
    </div>
  );
}
