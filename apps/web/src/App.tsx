import { Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AccesoDenegadoPage } from "./pages/AccesoDenegadoPage";
import { AuditoriaPage } from "./pages/AuditoriaPage";
import { ConfiguracionPage } from "./pages/ConfiguracionPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DispositivosPage } from "./pages/DispositivosPage";
import { HorariosPage } from "./pages/HorariosPage";
import { LoginPage } from "./pages/LoginPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { RegistroPage } from "./pages/RegistroPage";
import { ReportesPage } from "./pages/ReportesPage";
import { SedesPage } from "./pages/SedesPage";
import { TrabajadoresPage } from "./pages/TrabajadoresPage";
import { UsuariosPage } from "./pages/UsuariosPage";

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/registro" element={<RegistroPage />} />
      <Route path="/acceso-denegado" element={<AccesoDenegadoPage />} />
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/trabajadores" element={<ProtectedRoute><TrabajadoresPage /></ProtectedRoute>} />
      <Route path="/sedes" element={<ProtectedRoute><SedesPage /></ProtectedRoute>} />
      <Route path="/dispositivos" element={<ProtectedRoute><DispositivosPage /></ProtectedRoute>} />
      <Route path="/horarios" element={<ProtectedRoute><HorariosPage /></ProtectedRoute>} />
      <Route path="/reportes" element={<ProtectedRoute><ReportesPage /></ProtectedRoute>} />
      <Route path="/usuarios" element={<ProtectedRoute><UsuariosPage /></ProtectedRoute>} />
      <Route path="/auditoria" element={<ProtectedRoute><AuditoriaPage /></ProtectedRoute>} />
      <Route path="/configuracion" element={<ProtectedRoute><ConfiguracionPage /></ProtectedRoute>} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
