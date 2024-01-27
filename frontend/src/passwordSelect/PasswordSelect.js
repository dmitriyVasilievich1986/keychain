import { ClickOutsideRef } from "../components";
import createIcon from "Images/add.png";
import update from "Images/pen.png";
import classNames from "classnames";
import React from "react";
import Item from "./Item";

function PasswordSelect(props) {
  const [hide, setHide] = React.useState(true);

  const clickHandler = (newID) => {
    setHide(true);
    props?.onChange && props.onChange(newID);
  };

  const updateHandler = () => {
    setHide(true);
    props?.updateHandler && props.updateHandler();
  };
  const createHandler = () => {
    setHide(true);
    props?.createHandler && props.createHandler();
  };

  return (
    <div className={classNames("passwordSelectBlock")}>
      <ClickOutsideRef
        className={classNames("selectWrapper")}
        clickHandler={() => setHide(true)}
      >
        <div className={classNames("selectHead")}>
          <Item
            {...props.passwords.find((p) => p.id === props.value)}
            onClick={() => setHide((h) => !h)}
            selectedPassword={true}
          />
          <div className={classNames("selectButtons")}>
            <img src={update} onClick={updateHandler} />
            <img src={createIcon} onClick={createHandler} />
          </div>
        </div>
        <div className={classNames("list", { hide })}>
          {props.passwords
            .filter((p) => p.id !== props.value)
            .map((p) => (
              <Item onClick={clickHandler} key={p.id} {...p} />
            ))}
        </div>
      </ClickOutsideRef>
    </div>
  );
}

export default PasswordSelect;
