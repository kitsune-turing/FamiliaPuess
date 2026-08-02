import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { fetchDashboard } from "../services/api";
import type { DashboardIndicadores } from "../types/dashboard";
import { AdminLayout } from "../components/AdminLayout";

const INDICATOR_CARDS = [
  {
    key: "empleados_activos" as const,
    label: "Trabajadores activos",
    iconClass: "admin-card__icon--pink",
  },
  {
    key: "asistencias_hoy" as const,
    label: "Entradas hoy",
    iconClass: "admin-card__icon--gold",
  },
  {
    key: "novedades_hoy" as const,
    label: "Novedades hoy",
    iconClass: "admin-card__icon--pink",
  },
  {
    key: "tardanzas_hoy" as const,
    label: "Entradas tarde",
    iconClass: "admin-card__icon--pink",
  },
];

export function DashboardPage() {
  const { token, isAuthenticated } = useAuth();
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

  return (
    <AdminLayout title="Dashboard" subtitle="Resumen general del sistema">
      {loading && <div className="admin-loading">Cargando indicadores...</div>}

      {error && (
        <div className="admin-error">
          <p>{error}</p>
          <button type="button" className="admin-btn admin-btn--primary" onClick={loadDashboard}>
            Reintentar
          </button>
        </div>
      )}

      {data && !loading && (
        <section className="admin-cards">
          {INDICATOR_CARDS.map((card) => (
            <div key={card.key} className="admin-card">
              <div className={`admin-card__icon ${card.iconClass}`} />
              <div className="admin-card__info">
                <span className="admin-card__label">{card.label}</span>
                <span className="admin-card__value">{data[card.key]}</span>
              </div>
            </div>
          ))}
        </section>
      )}
    </AdminLayout>
  );
}
