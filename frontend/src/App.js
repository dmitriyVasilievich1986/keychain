import CreateNewPassword from "./createNewPasswordWindow/CreateNewPassword";
import PasswordBlock from "./passwordBlock/PasswordBlock";
import addIcon from "./assets/add.png";
import Icon from "./components/Icon";
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

  if (secret !== process.env.SECRET) {
    return (
      <input
        type="text"
        value={secret}
        onChange={(e) => setSecret(e.target.value)}
      />
    );
  }
  return (
    <div style={{ padding: "0", margin: "0" }}>
      {newPasswordWindow && (
        <CreateNewPassword
          setOpen={setNewPasswordWindow}
          password={passwordsToUpdate}
          setPasswords={setPasswords}
        />
      )}
      <div style={{ display: "flex", flexWrap: "wrap" }}>
        <div
          style={{
            flex: "1 300px",
            padding: "1rem",
            flexDirection: "column",
            flexWrap: "nowrap",
          }}
        >
          <select
            style={{ marginBottom: "1rem" }}
            value={openBlock}
            onChange={(e) => setOpenBlock(e.target.value)}
          >
            {passwords.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
          <div>
            <Icon src={addIcon} onClick={() => setNewPasswordWindow(true)} />
          </div>
        </div>
        <div style={{ flex: "2 700px" }}>
          <div>
            {openBlock && (
              <PasswordBlock
                onClick={() => setOpenBlock(i === openBlock ? null : i)}
                password={passwords.find((p) => p.id == openBlock)}
                open={true}
                setNewPasswordWindow={setNewPasswordWindow}
                setPasswordsToUpdate={setPasswordsToUpdate}
              />
            )}
          </div>
        </div>
        <div style={{ flex: "1 300px" }}>right</div>
      </div>
    </div>
  );
}

export default App;
