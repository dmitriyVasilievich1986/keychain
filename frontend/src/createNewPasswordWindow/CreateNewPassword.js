import NewField from "./NewField";
import React from "react";
import axios from "axios";

const emptyField = { name: "", value: "" };

function CreateNewPassword(props) {
  const modealWindowRef = React.useRef();
  const [newName, setNewName] = React.useState(props.password?.name || "");
  const [newFieldsList, setNewFieldsList] = React.useState(
    props.password?.fields || [emptyField]
  );

  React.useEffect(() => {
    function handleClickOutside(event) {
      if (
        modealWindowRef.current &&
        !modealWindowRef.current.contains(event.target)
      ) {
        props.setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [modealWindowRef]);

  function sendRequest(e) {
    if (
      newName === "" ||
      newFieldsList.map((f) => f.name === "" || f.value === "").includes(true)
    ) {
      console.log("empty");
      return;
    }
    const fields = {};
    newFieldsList.map((f) => {
      fields[f.name] = f.value;
    });
    const newPassword = {
      name: newName,
      fields,
    };

    if (props.password?.id) {
      sendPut(newPassword);
    } else {
      sendPost(newPassword);
    }
  }

  function sendPut(newPassword) {
    const ID = props.password.id;
    axios
      .put(`/api/${ID}`, newPassword)
      .then((data) => {
        console.log(data.data);
        props.setPasswords((passwords) =>
          passwords.map((p) => (p.id === ID ? data.data : p))
        );
        props.setOpen(false);
      })
      .catch((e) => {
        console.log(e);
      });
  }

  function sendPost(newPassword) {
    axios
      .post("/api", newPassword)
      .then((data) => {
        props.setPasswords((passwords) => [...passwords, data.data]);
        props.setOpen(false);
      })
      .catch((e) => {
        console.log(e);
      });
  }

  function addField() {
    setNewFieldsList([...newFieldsList, emptyField]);
  }

  return (
    <div
      style={{
        position: "absolute",
        top: "0",
        left: "0",
        width: "100vw",
        height: "100vh",
        justifyContent: "center",
        display: "flex",
      }}
    >
      <div
        ref={modealWindowRef}
        style={{
          width: "100%",
          maxWidth: "450px",
          margin: "3rem 1rem 0 1rem",
          height: "500px",
          maxHeight: "90%",
          backgroundColor: "white",
          border: "1px solid black",
          overflowY: "auto",
        }}
      >
        <div
          style={{ margin: "1rem", justifyContent: "center", display: "flex" }}
        >
          <input
            type="text"
            value={newName}
            placeholder="name for a new key"
            onChange={(e) => setNewName(e.target.value)}
          />
        </div>
        {newFieldsList.map((f, i) => (
          <NewField update={setNewFieldsList} index={i} key={i} {...f} />
        ))}
        <div
          style={{
            display: "flex",
            justifyContent: "end",
            margin: "10px 2rem",
          }}
        >
          <button
            style={{
              borderRadius: "50%",
              height: "25px",
              width: "25px",
              border: "none",
              backgroundColor: "#ccc",
              fontWeight: "bolder",
              cursor: "pointer",
              fontSize: "20px",
            }}
            onClick={addField}
          >
            +
          </button>
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            margin: "10px 0",
          }}
        >
          <button onClick={sendRequest}>
            {props.password?.id ? "update" : "send"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default CreateNewPassword;
