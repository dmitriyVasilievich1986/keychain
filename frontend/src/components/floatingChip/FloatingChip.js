import classnames from "classnames/bind";
import Chip from "@mui/material/Chip";
import * as style from "./style.scss";
import React from "react";

const cx = classnames.bind(style);

export function FloatingChip() {
  if (process.env.NODE_ENV !== "development") return null;
  return (
    <div className={cx("floating-chip")}>
      <Chip label="development" color="error" size="small" />
    </div>
  );
}
