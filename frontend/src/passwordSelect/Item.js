import classNames from "classnames";
import React from "react";

function Item(props) {
  const clickHandler = (e) => {
    props?.onClick && props?.onClick(props.id);
  };

  return (
    <div className={classNames("passwordSelectField")} onClick={clickHandler}>
      <img src={props.image_url} style={{ marginRight: "5px" }} />
      <div className={classNames({ selectedPassword: props.selectedPassword })}>
        {props.name}
      </div>
    </div>
  );
}

export default Item;
