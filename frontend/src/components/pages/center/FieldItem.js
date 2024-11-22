import ListItemAvatar from "@mui/material/ListItemAvatar";
import ListItemText from "@mui/material/ListItemText";
import DeleteIcon from "@mui/icons-material/Delete";
import IconButton from "@mui/material/IconButton";
import TextField from "@mui/material/TextField";
import ListItem from "@mui/material/ListItem";
import { ModifyField } from "./ModifyField";
import classnames from "classnames/bind";
import Grid from "@mui/material/Grid2";
import * as style from "./style.scss";
import Chip from "@mui/material/Chip";
import React from "react";
import _ from "lodash";

const cx = classnames.bind(style);

export function FieldItem(props) {
  const DeleteButton = () => {
    if (props?.deleteHandler === undefined) return null;
    return (
      <Grid size={6}>
        <IconButton
          onClick={props.deleteHandler}
          aria-label="delete"
          edge="end"
        >
          <DeleteIcon />
        </IconButton>
      </Grid>
    );
  };

  return (
    <ListItem key={props.field.id}>
      <ListItemAvatar>
        <Chip
          sx={{ marginRight: "10px" }}
          label={
            <div className={cx("field-avatar")}>
              <div>{props.field.name}</div>
              <div>{props.field.created_at}</div>
            </div>
          }
        />
      </ListItemAvatar>
      <ListItemText
        primary={
          <div className={cx("field-row")}>
            <TextField
              fullWidth={true}
              error={props.field.is_deleted}
              value={props.field.get_value}
              id="outlined-basic"
              variant="outlined"
              onFocus={(e) => {
                e.target.select();
                document.execCommand("copy");
                props.setMessage({
                  message: "Copied",
                  severity: "info",
                  timeout: 1000,
                });
              }}
            />
            <Grid container spacing={2}>
              <ModifyField {...props} />
              <DeleteButton />
            </Grid>
          </div>
        }
      />
    </ListItem>
  );
}
