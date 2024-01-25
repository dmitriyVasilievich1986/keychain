import CreateNewPassword from "./createNewPasswordWindow/CreateNewPassword";
import PasswordBlock from "./passwordBlock/PasswordBlock";
import { PasswordSelect } from "./passwordSelect";
import addIcon from "./assets/add.png";
import Icon from "./components/Icon";
import classNames from "classnames";
import React from "react";
import axios from "axios";

function App() {
  const [newPasswordWindow, setNewPasswordWindow] = React.useState(false);
  const [passwordsToUpdate, setPasswordsToUpdate] = React.useState(null);
  const [openBlock, setOpenBlock] = React.useState(null);
  const [passwords, setPasswords] = React.useState([]);
  const [secret, setSecret] = React.useState("");

  React.useEffect(() => {
    axios
      .get("/api")
      .then((data) => {
        setPasswords(data.data);
        setOpenBlock(data.data[0].id);
      })
      .catch((e) => {
        console.log(e);
      });
  }, []);

  React.useEffect(() => {
    if (!newPasswordWindow) setPasswordsToUpdate(null);
  }, [newPasswordWindow]);

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
        newPasswordWindow={newPasswordWindow}
        setOpen={setNewPasswordWindow}
        password={passwordsToUpdate}
        setPasswords={setPasswords}
      />
      <div className={classNames("main")}>
        <div className={classNames("left")}>
          <PasswordSelect
            onChange={setOpenBlock}
            passwords={passwords}
            value={openBlock}
          />
          <div>
            <Icon src={addIcon} onClick={() => setNewPasswordWindow(true)} />
          </div>
        </div>
        <div className={classNames("center")}>
          <div>
            {openBlock && (
              <PasswordBlock
                onClick={() => setOpenBlock(i === openBlock ? null : i)}
                password={passwords.find((p) => p.id == openBlock)}
                setNewPasswordWindow={setNewPasswordWindow}
                setPasswordsToUpdate={setPasswordsToUpdate}
                open={true}
              />
            )}
          </div>
        </div>
        <div className={classNames("right")} />
      </div>
    </div>
  );
}

export default App;
