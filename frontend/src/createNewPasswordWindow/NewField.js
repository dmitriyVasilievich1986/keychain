import React from "react";
import binIcon from "../assets/bin.png";
import Icon from "../components/Icon";

function NewField(props) {
  function updateField(name, value) {
    props.update((fields) =>
      fields.map((f, i) => (i === props.index ? { ...f, [name]: value } : f))
    );
  }

  function deleteField() {
    props.update((fields) => fields.filter((f, i) => i !== props.index));
  }

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-evenly",
        alignItems: "center",
        width: "100%",
        margin: "10px 0",
      }}
    >
      <input
        type="text"
        value={props.name}
        placeholder={`name #${props.index + 1}`}
        onChange={(e) => updateField("name", e.target.value)}
      />
      <textarea
        value={props.value}
        style={{ resize: "vertical" }}
        placeholder={`value #${props.index + 1}`}
        onChange={(e) => updateField("value", e.target.value)}
      />
      <div
        style={{
          width: "25px",
        }}
      >
        <Icon src={binIcon} onClick={deleteField} disabled={!props.index} />
      </div>
    </div>
  );
}

export default NewField;
