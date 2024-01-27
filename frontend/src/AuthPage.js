import classNames from "classnames";
import React from "react";
import axios from "axios";

function AuthPage(props) {
  const [value, setValue] = React.useState("");

  const check = (e) => {
    setValue(e.target.value);
    axios
      .get("/check_password", { auth: { password: e.target.value } })
      .then((data) => {
        props.onChange(data.data.password);
      })
      .catch((e) => {});
  };

  return (
    <div className={classNames("authPage")}>
      <input type="text" value={value} onChange={check} />
    </div>
  );
}

export default AuthPage;
