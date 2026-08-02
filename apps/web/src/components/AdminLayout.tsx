import type { ReactNode } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import marcaImg from "../assets/images/marca.png";
import "../styles/admin-layout.css";

const NAV_ITEMS = [
  { label: "Dashboard", path: "/dashboard" },
  { label: "Trabajadores", path: "/trabajadores" },
  { label: "Sedes", path: "/sedes" },
  { label: "Dispositivos", path: "/dispositivos" },
  { label: "Horarios", path: "/horarios" },
  { label: "Reportes", path: "/reportes" },
  { label: "Usuarios", path: "/usuarios" },
  { label: "Auditoría", path: "/auditoria" },
  { label: "Configuración", path: "/configuracion" },
];

interface AdminLayoutProps {
  title: string;
  subtitle: string;
  children: ReactNode;
}

export function AdminLayout({ title, subtitle, children }: AdminLayoutProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="admin-page">
      <aside className="admin-sidebar">
        <img src={marcaImg} alt="FamiliaPues" className="admin-sidebar__marca" />
        <span className="admin-sidebar__subtitle">CONTROL DE ASISTENCIA</span>

        <span className="admin-sidebar__section-title">MENÚ</span>
        <nav className="admin-sidebar__nav">
          {NAV_ITEMS.map((item) => (
            <a
              key={item.path}
              href={item.path}
              className={`admin-sidebar__item${location.pathname === item.path ? " admin-sidebar__item--active" : ""}`}
              onClick={(e) => {
                e.preventDefault();
                navigate(item.path);
              }}
            >
              {item.label}
            </a>
          ))}
        </nav>
      </aside>

      <main className="admin-main">
        <header className="admin-header">
          <div className="admin-header__left">
            <h1>{title}</h1>
            <p>{subtitle}</p>
          </div>
          <div className="admin-header__right">
            <div className="admin-header__user">
              <div className="admin-header__avatar" />
              <span>{user?.nombre ?? "Usuario"}</span>
            </div>
            <button type="button" className="admin-header__logout" onClick={handleLogout}>
              Salir
            </button>
          </div>
        </header>

        {children}
      </main>
    </div>
  );
}
