import { BrowserRouter } from "react-router-dom";
import ReactDOM from "react-dom/client";
import "Styles/style.scss";
import React from "react";
import App from "./App";

ReactDOM.createRoot(document.getElementById("app")).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
);
