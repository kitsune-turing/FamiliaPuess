import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { AdminLayout } from "../components/AdminLayout";

interface Reporte {
  id: number;
  nombre: string;
  rangoFechas: string;
  tipo: string;
  generadoPor: string;
  fechaHora: string;
  estado: string;
}

const CARDS = [
  { label: "Reportes generados", value: 45, iconClass: "admin-card__icon--pink" },
  { label: "Este mes", value: 12, iconClass: "admin-card__icon--gold" },
  { label: "Completados", value: 42, iconClass: "admin-card__icon--green" },
  { label: "Pendientes", value: 3, iconClass: "admin-card__icon--orange" },
];

const MOCK_DATA: Reporte[] = [
  { id: 1, nombre: "Asistencia mensual", rangoFechas: "01/07/2026 - 31/07/2026", tipo: "Asistencia", generadoPor: "Admin Principal", fechaHora: "01/08/2026 08:00", estado: "Completado" },
  { id: 2, nombre: "Novedades semanal", rangoFechas: "21/07/2026 - 27/07/2026", tipo: "Novedades", generadoPor: "Admin Principal", fechaHora: "28/07/2026 09:15", estado: "Completado" },
  { id: 3, nombre: "Tardanzas julio", rangoFechas: "01/07/2026 - 31/07/2026", tipo: "Tardanzas", generadoPor: "Supervisor", fechaHora: "31/07/2026 17:00", estado: "Completado" },
  { id: 4, nombre: "Empleados por sede", rangoFechas: "01/07/2026 - 31/07/2026", tipo: "Empleados", generadoPor: "Admin Principal", fechaHora: "30/07/2026 10:30", estado: "Completado" },
  { id: 5, nombre: "Asistencia diaria", rangoFechas: "01/08/2026", tipo: "Asistencia", generadoPor: "Admin Principal", fechaHora: "01/08/2026 18:00", estado: "Pendiente" },
];

export function ReportesPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [tipoFilter, setTipoFilter] = useState("");
  const [fechaDesde, setFechaDesde] = useState("");
  const [fechaHasta, setFechaHasta] = useState("");

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const filtered = MOCK_DATA.filter((r) => {
    if (tipoFilter && r.tipo !== tipoFilter) return false;
    return true;
  });

  return (
    <AdminLayout title="Reportes" subtitle="Generación y consulta de reportes">
      <section className="admin-cards">
        {CARDS.map((card) => (
          <div key={card.label} className="admin-card">
            <div className={`admin-card__icon ${card.iconClass}`} />
            <div className="admin-card__info">
              <span className="admin-card__label">{card.label}</span>
              <span className="admin-card__value">{card.value}</span>
            </div>
          </div>
        ))}
      </section>

      <div className="admin-filters">
        <input type="date" className="admin-filters__date" value={fechaDesde} onChange={(e) => setFechaDesde(e.target.value)} />
        <input type="date" className="admin-filters__date" value={fechaHasta} onChange={(e) => setFechaHasta(e.target.value)} />
        <select className="admin-filters__select" value={tipoFilter} onChange={(e) => setTipoFilter(e.target.value)}>
          <option value="">Todos los tipos</option>
          <option value="Asistencia">Asistencia</option>
          <option value="Novedades">Novedades</option>
          <option value="Tardanzas">Tardanzas</option>
          <option value="Empleados">Empleados</option>
        </select>
        <button type="button" className="admin-btn admin-btn--primary">Generar reporte</button>
      </div>

      <div className="admin-table-container">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Reporte</th>
              <th>Rango de fechas</th>
              <th>Tipo</th>
              <th>Generado por</th>
              <th>Fecha/Hora</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => (
              <tr key={r.id}>
                <td>{r.nombre}</td>
                <td>{r.rangoFechas}</td>
                <td>{r.tipo}</td>
                <td>{r.generadoPor}</td>
                <td>{r.fechaHora}</td>
                <td>
                  <span className={`admin-badge ${r.estado === "Completado" ? "admin-badge--green" : "admin-badge--gold"}`}>
                    {r.estado}
                  </span>
                </td>
                <td>
                  <div className="admin-table__actions">
                    <button type="button" className="admin-table__action-btn" title="Descargar">&#8595;</button>
                    <button type="button" className="admin-table__action-btn" title="Ver">&#128065;</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="admin-pagination">
          <span className="admin-pagination__info">Mostrando 1 a {filtered.length} de {filtered.length} registros</span>
          <div className="admin-pagination__controls">
            <button type="button" className="admin-pagination__btn">&laquo;</button>
            <button type="button" className="admin-pagination__btn admin-pagination__btn--active">1</button>
            <button type="button" className="admin-pagination__btn">&raquo;</button>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}
