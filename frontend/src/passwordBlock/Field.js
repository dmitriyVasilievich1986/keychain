import React from "react";

function Field(props) {
  return (
    <li
      style={{
        textDecoration: props.is_deleted ? "line-through" : "",
        display: "flex",
      }}
    >
      [{props.created_at}] {props.name}:
      <div
        style={{
          marginLeft: "10px",
          border: "1px solid black",
          padding: "0 10px",
        }}
      >
        {props.value}
      </div>
    </li>
  );
}

export default Field;
