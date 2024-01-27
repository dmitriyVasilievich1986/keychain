import ClickOutsideRef from "./ClickOutsideRef";
import crossIcon from "Images/cross.png";
import classNames from "classnames";
import React from "react";

function ModalWindow(props) {
  return (
    <div className={classNames("modalWindow")}>
      <div className={classNames("createPasswordWrapper")}>
        <div className={classNames("cross")}>
          <div>
            <img src={crossIcon} onClick={props.closeHandler} />
          </div>
        </div>
        <ClickOutsideRef
          className={classNames("formWrapper")}
          clickHandler={props.closeHandler}
        >
          {props.children}
        </ClickOutsideRef>
      </div>
    </div>
  );
}

export default ModalWindow;
