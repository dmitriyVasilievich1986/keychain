import classNames from "classnames";
import React from "react";
import Item from "./Item";

function PasswordSelect(props) {
  return (
    <div className={classNames("passwordSelectBlock")}>
      <div>
        <Item
          {...props.passwords.find((p) => p.id === props.value)}
          selectedPassword={true}
        />
        <div className={classNames("list")}>
          {props.passwords
            .filter((p) => p.id !== props.value)
            .map((p) => (
              <Item onClick={props.onChange} key={p.id} {...p} />
            ))}
        </div>
      </div>
    </div>
  );
}

export default PasswordSelect;
