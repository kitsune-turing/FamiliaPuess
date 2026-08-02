import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { fetchDashboard } from "../services/api";
import type { DashboardIndicadores } from "../types/dashboard";
import marcaImg from "../assets/images/marca.png";
import "../styles/dashboard.css";

const INDICATOR_CARDS = [
  {
    key: "empleados_activos" as const,
    label: "Trabajadores activos",
    iconClass: "dashboard-card__icon--pink",
  },
  {
    key: "asistencias_hoy" as const,
    label: "Entradas hoy",
    iconClass: "dashboard-card__icon--gold",
  },
  {
    key: "novedades_hoy" as const,
    label: "Novedades hoy",
    iconClass: "dashboard-card__icon--pink",
  },
  {
    key: "tardanzas_hoy" as const,
    label: "Entradas tarde",
    iconClass: "dashboard-card__icon--pink",
  },
];

const NAV_ITEMS = [
  { label: "Dashboard", path: "/dashboard", active: true },
  { label: "Trabajadores", path: "/trabajadores", active: false },
  { label: "Sedes", path: "/sedes", active: false },
  { label: "Dispositivos", path: "/dispositivos", active: false },
  { label: "Horarios", path: "/horarios", active: false },
  { label: "Reportes", path: "/reportes", active: false },
  { label: "Usuarios", path: "/usuarios", active: false },
  { label: "Configuración", path: "/configuracion", active: false },
];

export function DashboardPage() {
  const { token, user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [data, setData] = useState<DashboardIndicadores | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const result = await fetchDashboard(token);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar el dashboard");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login", { replace: true });
      return;
    }
    loadDashboard();
  }, [isAuthenticated, navigate, loadDashboard]);

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="dashboard-page">
      <aside className="dashboard-sidebar">
        <img src={marcaImg} alt="FamiliaPues" className="dashboard-sidebar__marca" />
        <span className="dashboard-sidebar__subtitle">CONTROL DE ASISTENCIA</span>

        <span className="dashboard-sidebar__section-title">MENÚ</span>
        <nav className="dashboard-sidebar__nav">
          {NAV_ITEMS.map((item) => (
            <a
              key={item.path}
              href={item.path}
              className={`dashboard-sidebar__item${item.active ? " dashboard-sidebar__item--active" : ""}`}
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

      <main className="dashboard-main">
        <header className="dashboard-header">
          <div className="dashboard-header__left">
            <h1>Dashboard</h1>
            <p>Resumen general del sistema</p>
          </div>
          <div className="dashboard-header__right">
            <div className="dashboard-header__user">
              <div className="dashboard-header__avatar" />
              <span>{user?.nombre ?? "Usuario"}</span>
            </div>
            <button
              type="button"
              className="dashboard-error__retry"
              onClick={handleLogout}
            >
              Salir
            </button>
          </div>
        </header>

        {loading && (
          <div className="dashboard-loading">Cargando indicadores...</div>
        )}

        {error && (
          <div className="dashboard-error">
            <p>{error}</p>
            <button type="button" className="dashboard-error__retry" onClick={loadDashboard}>
              Reintentar
            </button>
          </div>
        )}

        {data && !loading && (
          <section className="dashboard-cards">
            {INDICATOR_CARDS.map((card) => (
              <div key={card.key} className="dashboard-card">
                <div className={`dashboard-card__icon ${card.iconClass}`} />
                <div className="dashboard-card__info">
                  <span className="dashboard-card__label">{card.label}</span>
                  <span className="dashboard-card__value">{data[card.key]}</span>
                </div>
              </div>
            ))}
          </section>
        )}
      </main>
    </div>
  );
}
