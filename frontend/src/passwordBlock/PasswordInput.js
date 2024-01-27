import copyIcon from "Images/copy.png";
import classNames from "classnames";
import React from "react";

function PasswordInput(props) {
  const inputRef = React.useRef();

  const clickHandler = () => {
    inputRef.current.select();
    document.execCommand("copy");
  };

  return (
    <div className={classNames("passwordValueWrapper")}>
      <input
        type={process.env.NODE_ENV === "development" ? "password" : "text"}
        className={classNames({ deleted: props.is_deleted })}
        onChange={(e) => e.preventDefault()}
        value={props.value}
        ref={inputRef}
      />
      <img src={copyIcon} onClick={clickHandler} />
    </div>
  );
}

export default PasswordInput;
