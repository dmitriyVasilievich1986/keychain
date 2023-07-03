import CreateNewPassword from "./createNewPasswordWindow/CreateNewPassword";
import React from "react";
import axios from "axios";

function App() {
  const [newPasswordWindow, setNewPasswordWindow] = React.useState(false);
  const [passwordsToUpdate, setPasswordsToUpdate] = React.useState(null);
  const [passwords, setPasswords] = React.useState([]);

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

  return (
    <div style={{ padding: "0", margin: "0" }}>
      {newPasswordWindow && (
        <CreateNewPassword
          setOpen={setNewPasswordWindow}
          password={passwordsToUpdate}
          setPasswords={setPasswords}
        />
      )}
      <ul>
        {passwords.map((p) => (
          <li key={p.id}>
            <div style={{ display: "flex" }}>
              {p.name}
              <button
                onClick={() => {
                  setNewPasswordWindow(true);
                  setPasswordsToUpdate({
                    ...p,
                    fields: p.fields.filter((pf) => !pf.is_deleted),
                  });
                }}
              >
                update
              </button>
            </div>
            <ul>
              {p.fields.map((f) => (
                <li
                  key={`${f.name}_${f.created_at}`}
                  style={{ textDecoration: f.is_deleted ? "line-through" : "" }}
                >
                  {f.name}: {f.value} - {f.created_at}
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
      <button onClick={() => setNewPasswordWindow(true)}>New</button>
    </div>
  );
}

export default App;
