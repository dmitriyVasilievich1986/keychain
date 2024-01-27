import { ModalWindow, InputRow } from "../components";
import removeIcon from "Images/bin.png";
import addIcon from "Images/add.png";
import classNames from "classnames";
import React from "react";
import axios from "axios";

const emptyField = { name: "", value: "" };

function CreateNewPassword(props) {
  if (!props?.password) return null;

  const filteredFields = props.password.fields.filter((f) => !f.is_deleted);
  const [fields, setFields] = React.useState(
    filteredFields.length === 0 ? [emptyField] : filteredFields
  );

  const [imageSrc, setImageSrc] = React.useState(props.password.image_url);
  const [name, setName] = React.useState(props.password.name);

  const closeHandler = () => {
    props?.closeHandler && props.closeHandler();
  };

  const sendHandler = (e) => {
    e.preventDefault();
    const data = {
      url: props.password?.id ? `/api/${props.password.id}` : "/api",
      method: props.password?.id ? "put" : "post",
      data: {
        fields: Object.fromEntries(fields.map((f) => [f.name, f.value])),
        image_url: imageSrc,
        name,
      },
    };

    axios(data)
      .then((data) => {
        props.createHandler(data.data);
      })
      .catch((e) => {
        console.log(e);
      });
  };

  const fieldChangeHandler = (index, newValue) => {
    setFields(fields.map((f, i) => (i === index ? { ...f, ...newValue } : f)));
  };

  return (
    <ModalWindow closeHandler={closeHandler}>
      <form onSubmit={sendHandler}>
        <h4>Main attributes:</h4>
        <InputRow
          name="Name"
          value={name}
          placeholder="Enter the name"
          onChange={(e) => setName(e.target.value)}
        />
        <InputRow
          value={imageSrc}
          name="Image URL"
          placeholder="Enter url address for a icon"
          onChange={(e) => setImageSrc(e.target.value)}
        />
        <h4 style={{ marginTop: "2rem" }}>Secrets:</h4>
        <div className={classNames("fieldsList")}>
          {fields.map((f, i) => (
            <div key={i}>
              <div className={classNames("item")}>
                <InputRow
                  name="Name"
                  value={f.name}
                  placeholder="enter name for a secret"
                  onChange={(e) =>
                    fieldChangeHandler(i, { name: e.target.value })
                  }
                />
                <InputRow
                  name="Value"
                  value={f.value}
                  placeholder="enter value for a secret"
                  onChange={(e) =>
                    fieldChangeHandler(i, { value: e.target.value })
                  }
                />
              </div>
              <img
                src={removeIcon}
                onClick={() =>
                  setFields(
                    fields.length === 1
                      ? [emptyField]
                      : fields.filter((x, ind) => ind !== i)
                  )
                }
              />
            </div>
          ))}
        </div>
        <div className={classNames("addItem")}>
          <img
            src={addIcon}
            onClick={() => setFields([...fields, emptyField])}
          />
        </div>
        <div className={classNames("sendButtonWrapper")}>
          <button>{!props.password?.id ? "Create" : "Update"}</button>
        </div>
      </form>
    </ModalWindow>
  );
}

export default CreateNewPassword;
