import { Navigate, Route, Routes } from "react-router-dom";
import { AccesoDenegadoPage } from "./pages/AccesoDenegadoPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import { RegistroPage } from "./pages/RegistroPage";

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/registro" element={<RegistroPage />} />
      <Route path="/acceso-denegado" element={<AccesoDenegadoPage />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
