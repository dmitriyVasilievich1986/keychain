import CreateNewPassword from "./createNewPasswordWindow/CreateNewPassword";
import PasswordBlock from "./passwordBlock/PasswordBlock";
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
      <div
        style={{ display: "flex", justifyContent: "center", marginTop: "2rem" }}
      >
        <div style={{ width: "90%", maxWidth: "450px" }}>
          {passwords.map((p, i) => (
            <PasswordBlock
              onClick={() => setOpenBlock(i === openBlock ? null : i)}
              password={p}
              key={p.id}
              open={i === openBlock}
              setNewPasswordWindow={setNewPasswordWindow}
              setPasswordsToUpdate={setPasswordsToUpdate}
            />
          ))}
          <button onClick={() => setNewPasswordWindow(true)}>New</button>
        </div>
      </div>
    </div>
  );
}

export default App;
