import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { AdminLayout } from "./components/layout/AdminLayout";
import { LoginPage } from "./pages/LoginPage";

const RegistroPage = lazy(() => import("./pages/RegistroPage").then((m) => ({ default: m.RegistroPage })));
const AccesoDenegadoPage = lazy(() => import("./pages/AccesoDenegadoPage").then((m) => ({ default: m.AccesoDenegadoPage })));
const DashboardPage = lazy(() => import("./pages/admin/DashboardPage").then((m) => ({ default: m.DashboardPage })));
const RegistrosPage = lazy(() => import("./pages/admin/RegistrosPage").then((m) => ({ default: m.RegistrosPage })));
const TrabajadoresPage = lazy(() => import("./pages/admin/TrabajadoresPage").then((m) => ({ default: m.TrabajadoresPage })));
const RegistroTrabajadoresPage = lazy(() => import("./pages/admin/RegistroTrabajadoresPage").then((m) => ({ default: m.RegistroTrabajadoresPage })));
const CatalogosPage = lazy(() => import("./pages/admin/CatalogosPage").then((m) => ({ default: m.CatalogosPage })));
const DispositivosPage = lazy(() => import("./pages/admin/DispositivosPage").then((m) => ({ default: m.DispositivosPage })));
const SedesPage = lazy(() => import("./pages/admin/SedesPage").then((m) => ({ default: m.SedesPage })));
const ReportesPage = lazy(() => import("./pages/admin/ReportesPage").then((m) => ({ default: m.ReportesPage })));
const UsuariosPage = lazy(() => import("./pages/admin/UsuariosPage").then((m) => ({ default: m.UsuariosPage })));
const RolesPage = lazy(() => import("./pages/admin/RolesPage").then((m) => ({ default: m.RolesPage })));
const PerfilPage = lazy(() => import("./pages/admin/PerfilPage").then((m) => ({ default: m.PerfilPage })));
const HorariosPage = lazy(() => import("./pages/admin/HorariosPage").then((m) => ({ default: m.HorariosPage })));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage").then((m) => ({ default: m.NotFoundPage })));
const ConfiguracionPage = lazy(() => import("./pages/admin/ConfiguracionPage").then((m) => ({ default: m.ConfiguracionPage })));
const AuditoriaPage = lazy(() => import("./pages/admin/AuditoriaPage").then((m) => ({ default: m.AuditoriaPage })));

function PageLoader() {
  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: 200 }}>
      <span className="spinner" />
    </div>
  );
}

export function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        {/* Registro de asistencia por QR (acceso público con token) */}
        <Route path="/registro" element={<RegistroPage />} />
        <Route path="/acceso-denegado" element={<AccesoDenegadoPage />} />

        {/* Panel administrativo */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/panel" element={<AdminLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="registros" element={<RegistrosPage />} />
          <Route path="trabajadores" element={<RegistroTrabajadoresPage />} />
          <Route path="trabajadores/listado" element={<TrabajadoresPage />} />
          <Route path="dispositivos" element={<DispositivosPage />} />
          <Route path="sedes" element={<SedesPage />} />
          <Route path="reportes" element={<ReportesPage />} />
          <Route path="usuarios" element={<UsuariosPage />} />
          <Route path="roles" element={<RolesPage />} />
          <Route path="perfil" element={<PerfilPage />} />
          <Route path="horarios" element={<HorariosPage />} />
          <Route path="configuracion" element={<ConfiguracionPage />} />
          <Route path="auditoria" element={<AuditoriaPage />} />
          <Route path="catalogos" element={<CatalogosPage />} />
        </Route>

        <Route path="/" element={<Navigate to="/panel" replace />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Suspense>
  );
}
