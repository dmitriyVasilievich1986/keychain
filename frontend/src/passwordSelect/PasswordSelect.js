import classNames from "classnames";
import React from "react";

function Item(props) {
  return (
    <div className={classNames("passwordSelectField")}>
      <img src={props.image_url} style={{ marginRight: "5px" }} />
      <div className={classNames({ show: props.id === props.value })}>
        {props.name}
      </div>
    </div>
  );
}

function PasswordSelect(props) {
  const clickHandler = (newID) => {
    props?.onChange && props.onChange(newID);
  };

  return (
    <div className={classNames("passwordSelectBlock")}>
      <div>
        <ul>
          {props.passwords.map((p) => (
            <li onClick={() => clickHandler(p.id)} key={p.id}>
              <Item {...p} value={props.value} />
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default PasswordSelect;
