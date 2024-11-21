import classnames from "classnames/bind";
import * as style from "./style.scss";
import { LeftSide } from "./leftSide";
import { Center } from "./center";
import React from "react";

const cx = classnames.bind(style);

export function PasswordPage() {
  return (
    <div className={cx("main-container")}>
      <div className={cx("left")}>
        <LeftSide />
      </div>
      <div className={cx("center")}>
        <Center />
      </div>
      <div className={cx("right")}></div>
    </div>
  );
}
