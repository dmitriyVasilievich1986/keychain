import classNames from "classnames";
import React from "react";
import axios from "axios";

function AuthPage(props) {
  const [value, setValue] = React.useState("");

  const submitHandler = (e) => {
    e.preventDefault();

    axios
      .get("/check_password", { auth: { password: value } })
      .then((data) => {
        props.onChange(data.data.token);
      })
      .catch((e) => {});
  };

  return (
    <div className={classNames("authPage")}>
      <form onSubmit={submitHandler}>
        <input
          autoFocus
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value.toLowerCase())}
        />
      </form>
    </div>
  );
}

export default AuthPage;
