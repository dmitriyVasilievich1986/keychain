import updateIcon from "../assets/pen.png";
import Icon from "../components/Icon";
import Field from "./Field";
import React from "react";

function PasswordBlock(props) {
  return (
    <div>
      <div
        style={{
          display: "flex",
        }}
        onClick={props.onClick}
      >
        <div style={{ flex: "1" }}></div>
        <div style={{ flex: "3" }}>{props.password.name}</div>
        <div style={{ flex: "1" }}>
          <Icon
            onClick={() => {
              props.setNewPasswordWindow(true);
              props.setPasswordsToUpdate({
                ...props.password,
                fields: props.password.fields.filter((pf) => !pf.is_deleted),
              });
            }}
            src={updateIcon}
          />
        </div>
      </div>
      <ul style={{ display: props.open ? "block" : "none" }}>
        <div style={{ margin: "10px 0" }}>
          passwords:
          {props.password.fields
            .filter((f) => !f.is_deleted)
            .map((f, i) => (
              <Field {...f} key={`${f.name}_${i}`} />
            ))}
        </div>
        <div style={{ margin: "10px 0" }}>
          history:
          {props.password.fields
            .filter((f) => f.is_deleted)
            .map((f, i) => (
              <Field {...f} key={`${f.name}_${i}`} />
            ))}
        </div>
      </ul>
    </div>
  );
}

export default PasswordBlock;
