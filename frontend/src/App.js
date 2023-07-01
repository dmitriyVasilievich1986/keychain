import React from "react";
import axios from "axios";

function App() {
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
    <div>
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
    </div>
  );
}

export default App;
