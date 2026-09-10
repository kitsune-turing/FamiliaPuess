import { useEffect, useState } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthProvider";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

/** Título y subtítulo mostrados en la barra superior para cada ruta. */
const CABECERAS: Record<string, { titulo: string; subtitulo: string }> = {
  "/panel": { titulo: "Dashboard", subtitulo: "Resumen general del sistema" },
  "/panel/registros": {
    titulo: "Registros de entrada",
    subtitulo: "Consulta los registros de asistencia de cada jornada",
  },
  "/panel/trabajadores": {
    titulo: "Registro de trabajadores",
    subtitulo: "Gestiona la información de los trabajadores del sistema",
  },
  "/panel/trabajadores/listado": {
    titulo: "Trabajadores",
    subtitulo: "Consulta y gestiona los registros de entrada de los trabajadores",
  },
  "/panel/dispositivos": {
    titulo: "Dispositivos",
    subtitulo: "Gestiona los dispositivos de asistencia del sistema",
  },
  "/panel/sedes": {
    titulo: "Sedes",
    subtitulo: "Gestiona las sedes de la organización y su información",
  },
  "/panel/reportes": {
    titulo: "Reportes",
    subtitulo: "Genera y descarga reportes de asistencia según tus necesidades",
  },
  "/panel/usuarios": {
    titulo: "Usuarios",
    subtitulo: "Gestiona los usuarios del sistema y sus permisos de acceso",
  },
  "/panel/horarios": {
    titulo: "Horarios",
    subtitulo: "Gestiona los horarios laborales de los trabajadores",
  },
  "/panel/roles": {
    titulo: "Roles y permisos",
    subtitulo: "Gestiona roles y permisos del sistema",
  },
  "/panel/perfil": {
    titulo: "Mi perfil",
    subtitulo: "Consulta y actualiza los datos de tu cuenta",
  },
  "/panel/configuracion": {
    titulo: "Configuración",
    subtitulo: "Ajusta los parámetros generales del sistema de asistencia",
  },
  "/panel/auditoria": {
    titulo: "Auditoría",
    subtitulo: "Consulta y analiza todas las actividades realizadas en el sistema",
  },
  "/panel/catalogos": {
    titulo: "Catálogos",
    subtitulo: "Administra las listas de valores que alimentan los formularios",
  },
  "/panel/parametros": {
    titulo: "Parámetros",
    subtitulo: "Ajusta los valores de configuración del sistema sin recompilar",
  },
};

export function AdminLayout() {
  const { usuario, cargando } = useAuth();
  const ubicacion = useLocation();
  const [menuAbierto, setMenuAbierto] = useState(false);

  // Cierra el menú lateral y sube el scroll al cambiar de sección.
  useEffect(() => {
    setMenuAbierto(false);
    window.scrollTo({ top: 0 });
  }, [ubicacion.pathname]);

  if (cargando) {
    return (
      <div style={{ display: "grid", placeItems: "center", minHeight: "100vh" }}>
        <span className="spinner spinner--dark" />
      </div>
    );
  }

  if (!usuario) {
    return <Navigate to="/login" replace state={{ desde: ubicacion.pathname }} />;
  }

  const cabecera = CABECERAS[ubicacion.pathname] ?? {
    titulo: "Panel",
    subtitulo: "Sistema de control de asistencia",
  };

  return (
    <div className="admin-shell">
      <Sidebar
        abierto={menuAbierto}
        alCerrar={() => setMenuAbierto(false)}
        mostrarAdministracion={usuario.rolCodigo === "SUPER_ADMIN"}
      />
      <div className="admin-main">
        <Topbar
          titulo={cabecera.titulo}
          subtitulo={cabecera.subtitulo}
          alAbrirMenu={() => setMenuAbierto(true)}
        />
        <main className="admin-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
