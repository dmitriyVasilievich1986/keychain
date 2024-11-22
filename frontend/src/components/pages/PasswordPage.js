import classnames from "classnames/bind";
import * as style from "./style.scss";
import { LeftSide } from "./leftSide";
import { Center } from "./center";
import React from "react";

import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";

const cx = classnames.bind(style);

export function PasswordPage() {
  const [message, setMessage] = React.useState(null);

  return (
    <>
      {message !== null && (
        <Snackbar
          open={true}
          onClose={() => setMessage(null)}
          autoHideDuration={message?.timeout || 3000}
          ClickAwayListenerProps={{ onClickAway: () => null }}
          anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
        >
          <Alert
            severity={message.severity}
            sx={{ width: "100%" }}
            variant="filled"
          >
            {message.message}
          </Alert>
        </Snackbar>
      )}
      <div className={cx("main-container")}>
        <div className={cx("left")}>
          <LeftSide setMessage={setMessage} />
        </div>
        <div className={cx("center")}>
          <Center setMessage={setMessage} />
        </div>
        <div className={cx("right")}></div>
      </div>
    </>
  );
}
