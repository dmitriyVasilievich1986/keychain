import CreateNewPassword from "./createNewPasswordWindow/CreateNewPassword";
import PasswordSelect from "./passwordSelect";
import PasswordBlock from "./passwordBlock";
import { Message } from "./components";
import classNames from "classnames";
import React from "react";
import axios from "axios";

const emptyPassword = {
  image_url: "static/i/icon/no-image.png",
  fields: [],
  name: "",
};

function App() {
  const [createPassword, setCreatePassword] = React.useState(null);
  const [openBlock, setOpenBlock] = React.useState(null);
  const [passwords, setPasswords] = React.useState([]);
  const [message, setMessage] = React.useState({});
  const [secret, setSecret] = React.useState("");

  React.useEffect(() => {
    axios
      .get("/api")
      .then((data) => {
        setPasswords(data.data);
        setOpenBlock(data.data[0].id);
        setMessage({ message: "Data was loaded", type: "success" });
      })
      .catch((e) => {
        console.log(e);
        setMessage({ message: "Data was not loaded", type: "error" });
      });
  }, []);

  const createHandler = (data) => {
    if (!passwords.find((p) => p.id === data.id)) {
      setPasswords([...passwords, data]);
      setOpenBlock(data.id);
    } else {
      setPasswords(passwords.map((p) => (p.id === data.id ? data : p)));
    }
    setCreatePassword(null);
  };

  if (secret !== process.env.SECRET && process.env.NODE_ENV !== "development") {
    return (
      <input
        type="text"
        value={secret}
        onChange={(e) => setSecret(e.target.value)}
      />
    );
  }
  return (
    <div>
      {process.env.NODE_ENV === "development" && (
        <div className={classNames("nodeEnvLabel")}>{process.env.NODE_ENV}</div>
      )}
      <CreateNewPassword
        closeHandler={() => setCreatePassword(null)}
        password={createPassword}
        createHandler={createHandler}
      />
      <Message {...message} />
      <div className={classNames("main")}>
        <div className={classNames("left")}>
          <PasswordSelect
            onChange={setOpenBlock}
            passwords={passwords}
            value={openBlock}
            createHandler={() => setCreatePassword(emptyPassword)}
            updateHandler={() =>
              setCreatePassword(passwords.find((p) => p.id == openBlock))
            }
          />
        </div>
        <div className={classNames("center")}>
          <PasswordBlock password={passwords.find((p) => p.id == openBlock)} />
        </div>
        <div className={classNames("right")} />
      </div>
    </div>
  );
}

export default App;
