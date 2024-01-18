import React from "react";

function PasswordSelect(props) {
  const clickHandler = (newID) => {
    props?.onChange && props.onChange(newID);
  };

  return (
    <div>
      <ul>
        {props.passwords.map((p) => (
          <li
            style={{
              backgroundColor: p.id === props.value ? "red" : "inherit",
              alignItems: "center",
              cursor: "pointer",
              display: "flex",
            }}
            onClick={() => clickHandler(p.id)}
            key={p.id}
          >
            <img
              src={p.image_url}
              style={{ height: "25px", width: "25px", marginRight: "5px" }}
            />
            {p.name}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default PasswordSelect;
