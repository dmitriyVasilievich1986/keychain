import { useLocation, useParams } from "react-router-dom";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import Container from "@mui/material/Container";
import { AddPassword } from "./AddPassword";
import classnames from "classnames/bind";
import * as style from "./style.scss";
import React from "react";
import axios from "axios";
import _ from "lodash";

const cx = classnames.bind(style);

export function LeftSide() {
  const [passwords, setPasswords] = React.useState([]);
  const [value, setValue] = React.useState(null);
  const location = useLocation();
  const params = useParams();

  React.useEffect(() => {
    axios
      .get("/api/v1/password/")
      .then((data) => {
        setPasswords(data.data.result.map((d) => ({ ...d, label: d.name })));
      })
      .catch((e) => {
        console.log(e);
      });
  }, []);

  React.useEffect(() => {
    if (params.pk) {
      setValue(
        passwords.find((password) => password.id === parseInt(params.pk))
      );
    }
  }, [location.pathname, passwords]);

  const postPasswordHandler = (name, image_url) => {
    axios
      .post("/api/v1/password/", { name, image_url: image_url || null })
      .then((data) => {
        setPasswords((prev) => [
          ...prev,
          { ...data.data.result, id: data.data.id, label: name },
        ]);
      })
      .catch((e) => {
        console.log(e);
      });
  };

  return (
    <Container maxWidth="md" sx={{ mt: "1rem" }}>
      <Autocomplete
        value={value || null}
        options={passwords}
        clearIcon={null}
        renderInput={(params) => <TextField {...params} label="Passwords" />}
        renderOption={(props, option) => {
          return (
            <a
              href={`/password/${option.id}/`}
              {...props}
              className={cx("autocomplete-option")}
            >
              <img src={option.image_url} />
              {option.label}
            </a>
          );
        }}
      />
      <AddPassword postHandler={postPasswordHandler} />
    </Container>
  );
}
