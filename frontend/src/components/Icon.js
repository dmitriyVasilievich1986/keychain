import React from "react";

function Icon(props) {
  if (props.disabled) {
    return <div style={{ width: "15px", height: "15px" }} />;
  }
  return (
    <img
      src={props.src}
      onClick={props.onClick}
      style={{ width: "15px", height: "15px", cursor: "pointer" }}
    />
  );
}

export default Icon;
