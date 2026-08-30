import { Navigate, Outlet, Route, Routes } from "react-router-dom";
import { AdminLayout } from "./components/layout/AdminLayout";
import { useAuth } from "./contexts/AuthContext";
import { AccesoDenegadoPage } from "./pages/AccesoDenegadoPage";
import { AuditoriaPage } from "./pages/AuditoriaPage";
import { CatalogosPage } from "./pages/CatalogosPage";
import { ConfiguracionPage } from "./pages/ConfiguracionPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DispositivosPage } from "./pages/DispositivosPage";
import { HorariosPage } from "./pages/HorariosPage";
import { LoginPage } from "./pages/LoginPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { ParametrosPage } from "./pages/ParametrosPage";
import { RegistroPage } from "./pages/RegistroPage";
import { RegistroTrabajadoresPage } from "./pages/RegistroTrabajadoresPage";
import { RegistrosPage } from "./pages/RegistrosEntradaPage";
import { ReportesPage } from "./pages/ReportesPage";
import { SedesPage } from "./pages/SedesPage";
import { SeguridadPage } from "./pages/SeguridadPage";
import { TrabajadoresPage } from "./pages/TrabajadoresPage";
import { UsuariosPage } from "./pages/UsuariosPage";

/** Restringe las rutas de administración al súper administrador. */
function RutaSuperAdmin() {
  const { user } = useAuth();
  if (user?.rol_codigo !== "SUPER_ADMIN") return <Navigate to="/panel" replace />;
  return <Outlet />;
}

export function App() {
  return (
    <Routes>
      {/* ---- Rutas públicas ---- */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/registro" element={<RegistroPage />} />
      <Route path="/acceso-denegado" element={<AccesoDenegadoPage />} />

      {/* ---- Panel administrativo (exige sesión) ---- */}
      <Route path="/panel" element={<AdminLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="registros" element={<RegistrosPage />} />
        <Route path="trabajadores" element={<RegistroTrabajadoresPage />} />
        <Route path="trabajadores/listado" element={<TrabajadoresPage />} />
        <Route path="dispositivos" element={<DispositivosPage />} />
        <Route path="sedes" element={<SedesPage />} />
        <Route path="horarios" element={<HorariosPage />} />
        <Route path="reportes" element={<ReportesPage />} />
        <Route path="usuarios" element={<UsuariosPage />} />
        <Route path="configuracion" element={<ConfiguracionPage />} />
        <Route path="seguridad" element={<SeguridadPage />} />
        <Route path="auditoria" element={<AuditoriaPage />} />

        {/* Solo súper administrador */}
        <Route element={<RutaSuperAdmin />}>
          <Route path="catalogos" element={<CatalogosPage />} />
          <Route path="parametros" element={<ParametrosPage />} />
        </Route>
      </Route>

      {/* ---- Compatibilidad con las rutas antiguas ---- */}
      <Route path="/dashboard" element={<Navigate to="/panel" replace />} />
      <Route path="/trabajadores" element={<Navigate to="/panel/trabajadores" replace />} />
      <Route path="/sedes" element={<Navigate to="/panel/sedes" replace />} />
      <Route path="/dispositivos" element={<Navigate to="/panel/dispositivos" replace />} />
      <Route path="/horarios" element={<Navigate to="/panel/horarios" replace />} />
      <Route path="/reportes" element={<Navigate to="/panel/reportes" replace />} />
      <Route path="/usuarios" element={<Navigate to="/panel/usuarios" replace />} />
      <Route path="/auditoria" element={<Navigate to="/panel/auditoria" replace />} />
      <Route path="/configuracion" element={<Navigate to="/panel/configuracion" replace />} />

      <Route path="/" element={<Navigate to="/panel" replace />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
