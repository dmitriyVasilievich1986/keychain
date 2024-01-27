import PasswordInput from "./PasswordInput";
import classNames from "classnames";
import React from "react";

function PasswordRow(props) {
  return (
    <div className={classNames("passwordRow")}>
      <div className={classNames("passwordNameWrapper")}>
        <div>{props.name}</div>
      </div>
      <PasswordInput is_deleted={props.is_deleted} value={props.value} />
    </div>
  );
}

export default PasswordRow;
