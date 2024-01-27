import CreateNewPassword from "./createNewPasswordWindow/CreateNewPassword";
import PasswordSelect from "./passwordSelect";
import PasswordBlock from "./passwordBlock";
import { Message } from "./components";
import classNames from "classnames";
import AuthPage from "./AuthPage";
import React from "react";
import axios from "axios";

const emptyPassword = {
  image_url: "static/i/no-photo.png",
  fields: [],
  name: "",
};

const basicPasswords = [
  {
    image_url: "static/i/no-photo.png",
    name: "password1",
    id: 1,
    fields: [
      { name: "login", value: "login" },
      { name: "password", value: "password" },
    ],
  },
  {
    image_url: "static/i/no-photo.png",
    name: "password2",
    id: 2,
    fields: [
      { name: "login", value: "login" },
      { name: "password", value: "password" },
    ],
  },
];

function App() {
  const [createPassword, setCreatePassword] = React.useState(null);
  const [passwords, setPasswords] = React.useState(basicPasswords);
  const [openBlock, setOpenBlock] = React.useState(1);
  const [message, setMessage] = React.useState({});
  const [secret, setSecret] = React.useState(null);

  React.useEffect(() => {
    axios
      .get("/api", { auth: { password: secret } })
      .then((data) => {
        setPasswords(data.data);
        setOpenBlock(data.data[0].id);
        setMessage({ message: "Data was loaded", type: "success" });
      })
      .catch((e) => {
        console.log(e);
        setMessage({ message: "Data was not loaded", type: "error" });
      });
  }, [secret]);

  const createHandler = (data) => {
    if (!passwords.find((p) => p.id === data.id)) {
      setPasswords([...passwords, data]);
      setOpenBlock(data.id);
    } else {
      setPasswords(passwords.map((p) => (p.id === data.id ? data : p)));
    }
    setCreatePassword(null);
  };

  if (process.env.NODE_ENV !== "development" && secret === null) {
    return <AuthPage onChange={setSecret} />;
  }
  return (
    <div>
      {process.env.NODE_ENV === "development" && (
        <div className={classNames("nodeEnvLabel")}>{process.env.NODE_ENV}</div>
      )}
      <CreateNewPassword
        closeHandler={() => setCreatePassword(null)}
        createHandler={createHandler}
        password={createPassword}
        setMessage={setMessage}
        secret={secret}
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
