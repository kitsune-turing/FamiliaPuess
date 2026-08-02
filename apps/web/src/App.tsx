import { Navigate, Route, Routes } from "react-router-dom";
import { AccesoDenegadoPage } from "./pages/AccesoDenegadoPage";
import { AuditoriaPage } from "./pages/AuditoriaPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DispositivosPage } from "./pages/DispositivosPage";
import { LoginPage } from "./pages/LoginPage";
import { RegistroPage } from "./pages/RegistroPage";
import { ReportesPage } from "./pages/ReportesPage";
import { SedesPage } from "./pages/SedesPage";
import { TrabajadoresPage } from "./pages/TrabajadoresPage";
import { UsuariosPage } from "./pages/UsuariosPage";

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/trabajadores" element={<TrabajadoresPage />} />
      <Route path="/sedes" element={<SedesPage />} />
      <Route path="/dispositivos" element={<DispositivosPage />} />
      <Route path="/reportes" element={<ReportesPage />} />
      <Route path="/usuarios" element={<UsuariosPage />} />
      <Route path="/auditoria" element={<AuditoriaPage />} />
      <Route path="/registro" element={<RegistroPage />} />
      <Route path="/acceso-denegado" element={<AccesoDenegadoPage />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
