import CreateNewPassword from "./createNewPasswordWindow/CreateNewPassword";
import React from "react";
import axios from "axios";

function App() {
  const [newPasswordWindow, setNewPasswordWindow] = React.useState(false);
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

  return (
    <div style={{ padding: "0", margin: "0" }}>
      {newPasswordWindow && (
        <CreateNewPassword
          setOpen={setNewPasswordWindow}
          setPasswords={setPasswords}
        />
      )}
      <ul>
        {passwords.map((p) => (
          <li key={p.id}>
            {p.name}
            <ul>
              {p.fields.map((f) => (
                <li key={f.name}>
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
