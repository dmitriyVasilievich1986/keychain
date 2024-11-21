import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import DialogTitle from "@mui/material/DialogTitle";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import Container from "@mui/material/Container";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import List from "@mui/material/List";
import React from "react";
import _ from "lodash";

export function PostModal(props) {
  return (
    <Dialog
      aria-labelledby="customized-dialog-title"
      onClose={props.closeHandler}
      open={props.open}
    >
      <DialogTitle sx={{ m: 0, p: 2 }} id="customized-dialog-title">
        {props.header}
      </DialogTitle>
      <IconButton
        aria-label="close"
        onClick={props.closeHandler}
        sx={{
          position: "absolute",
          color: "gray",
          right: 8,
          top: 8,
        }}
      >
        <CloseIcon />
      </IconButton>
      <DialogContent sx={{ minWidth: "500px" }}>
        <Container maxWidth="md">
          <List>{props.children}</List>
        </Container>
        <DialogActions>
          <Button onClick={props.clickHandler}>
            {props?.postButtonLabel || Send}
          </Button>
        </DialogActions>
      </DialogContent>
    </Dialog>
  );
}
