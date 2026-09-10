import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { RegistroPage } from "./pages/RegistroPage";
import "./styles/registro.css";
import "./styles/global.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/*" element={<RegistroPage />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
);
