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
      <input
        disabled={false}
        type="text"
        value={props.value}
        style={{
          marginLeft: "10px",
          border: "1px solid black",
          padding: "0 10px",
          cursor: "pointer",
        }}
        onChange={(e) => e.preventDefault()}
        onClick={(e) => {
          e.target.select();
          document.execCommand("copy");
        }}
      />
    </li>
  );
}

export default Field;
