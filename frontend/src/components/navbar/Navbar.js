import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import Toolbar from "@mui/material/Toolbar";
import SvgIcon from "@mui/material/SvgIcon";
import AppBar from "@mui/material/AppBar";
import classnames from "classnames/bind";
import padlockIcon from "./padlock.svg";
import * as style from "./style.scss";
import React from "react";

const cx = classnames.bind(style);

export function Navbar() {
  return (
    <AppBar position="sticky">
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <div className={cx("navbar-inner")}>
            <div className={cx("navbar-brand")}>
              <SvgIcon
                component={padlockIcon}
                fontSize="large"
                color="primary"
                inheritViewBox
              />
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                <a href="/password/" className={cx("navbar-link")}>
                  Password
                </a>
              </Typography>
            </div>
            <div>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                <a href="/logout" className={cx("navbar-link")}>
                  Logout
                </a>
              </Typography>
            </div>
          </div>
        </Toolbar>
      </Container>
    </AppBar>
  );
}
