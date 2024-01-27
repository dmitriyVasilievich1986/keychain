import createIcon from "Images/add.png";
import updateIcon from "Images/pen.png";
import removeIcon from "Images/bin.png";
import copyIcon from "Images/copy.png";
import classNames from "classnames";
import React from "react";

function InputRow(props) {
  const inputRef = React.useRef();

  const clickHandler = () => {
    inputRef.current.select();
    document.execCommand("copy");
  };

  const onChangeHandler = (e) => {
    e.preventDefault();
    props?.onChange && props.onChange(e);
  };

  return (
    <div className={classNames("inputRow")}>
      <div className={classNames("inputName")}>
        <span>{props.name}</span>
      </div>
      <div className={classNames("inputField")}>
        <input
          className={classNames({ deleted: props.is_deleted })}
          type={props?.secret ? "password" : "text"}
          placeholder={props?.placeholder || ""}
          disabled={props?.disabled || false}
          onChange={onChangeHandler}
          value={props.value}
          ref={inputRef}
        />

        {props?.copy && <img src={copyIcon} onClick={clickHandler} />}
        {props?.updateHandler && (
          <img src={updateIcon} onClick={props.updateHandler} />
        )}
        {props?.createHandler && (
          <img src={createIcon} onClick={props.createHandler} />
        )}
        {props?.removeHandler && (
          <img src={removeIcon} onClick={props.removeHandler} />
        )}
      </div>
    </div>
  );
}

export default InputRow;
