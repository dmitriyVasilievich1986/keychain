import { FloatingChip, Navbar, PasswordPage } from "./components";
import { Routes, Route } from "react-router-dom";
import React from "react";

function App() {
  return (
    <>
      <FloatingChip />
      <Navbar />
      <Routes>
        <Route path="/">
          {["", "password/", "password/:pk/"].map((path) => (
            <Route path={path} key={path} element={<PasswordPage />} />
          ))}
        </Route>
      </Routes>
    </>
  );
}

export default App;
