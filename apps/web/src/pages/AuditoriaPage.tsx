import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { AdminLayout } from "../components/AdminLayout";

interface AuditoriaItem {
  id: number;
  fechaHora: string;
  usuario: string;
  modulo: string;
  accion: string;
  sede: string;
  ip: string;
  dispositivo: string;
}

const CARDS = [
  { label: "Total actividades", value: 1248, iconClass: "admin-card__icon--pink" },
  { label: "Hoy", value: 34, iconClass: "admin-card__icon--gold" },
  { label: "Usuarios activos", value: 8, iconClass: "admin-card__icon--green" },
  { label: "Alertas", value: 2, iconClass: "admin-card__icon--orange" },
];

const MOCK_DATA: AuditoriaItem[] = [
  { id: 1, fechaHora: "01/08/2026 08:15:23", usuario: "Admin Principal", modulo: "Trabajadores", accion: "Crear", sede: "Sede Principal", ip: "192.168.1.10", dispositivo: "Chrome / Windows" },
  { id: 2, fechaHora: "01/08/2026 08:10:05", usuario: "Carlos Supervisor", modulo: "Seguridad", accion: "Actualizar", sede: "Sede Norte", ip: "192.168.1.25", dispositivo: "Chrome / macOS" },
  { id: 3, fechaHora: "01/08/2026 07:55:42", usuario: "Admin Principal", modulo: "Sedes", accion: "Crear", sede: "Sede Principal", ip: "192.168.1.10", dispositivo: "Chrome / Windows" },
  { id: 4, fechaHora: "01/08/2026 07:45:18", usuario: "María Admin", modulo: "Dispositivos", accion: "Actualizar", sede: "Sede Sur", ip: "192.168.1.30", dispositivo: "Firefox / Linux" },
  { id: 5, fechaHora: "31/07/2026 17:30:00", usuario: "Admin Principal", modulo: "Usuarios", accion: "Crear", sede: "Sede Principal", ip: "192.168.1.10", dispositivo: "Chrome / Windows" },
  { id: 6, fechaHora: "31/07/2026 16:20:15", usuario: "Carlos Supervisor", modulo: "Horarios", accion: "Actualizar", sede: "Sede Norte", ip: "192.168.1.25", dispositivo: "Chrome / macOS" },
];

function moduloBadgeClass(modulo: string): string {
  if (modulo === "Trabajadores") return "admin-badge--pink";
  if (modulo === "Seguridad") return "admin-badge--orange";
  if (modulo === "Sedes") return "admin-badge--gold";
  if (modulo === "Dispositivos") return "admin-badge--blue";
  if (modulo === "Usuarios") return "admin-badge--pink";
  return "admin-badge--green";
}

function accionBadgeClass(accion: string): string {
  if (accion === "Crear") return "admin-badge--green";
  if (accion === "Actualizar") return "admin-badge--blue";
  if (accion === "Eliminar") return "admin-badge--red";
  return "admin-badge--gold";
}

export function AuditoriaPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [fechaDesde, setFechaDesde] = useState("");
  const [fechaHasta, setFechaHasta] = useState("");
  const [usuarioFilter, setUsuarioFilter] = useState("");
  const [moduloFilter, setModuloFilter] = useState("");
  const [accionFilter, setAccionFilter] = useState("");

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const filtered = MOCK_DATA.filter((a) => {
    if (usuarioFilter && a.usuario !== usuarioFilter) return false;
    if (moduloFilter && a.modulo !== moduloFilter) return false;
    if (accionFilter && a.accion !== accionFilter) return false;
    return true;
  });

  const clearFilters = () => {
    setFechaDesde("");
    setFechaHasta("");
    setUsuarioFilter("");
    setModuloFilter("");
    setAccionFilter("");
  };

  return (
    <AdminLayout title="Auditoría" subtitle="Registro de actividades del sistema">
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
        <select className="admin-filters__select" value={usuarioFilter} onChange={(e) => setUsuarioFilter(e.target.value)}>
          <option value="">Todos los usuarios</option>
          <option value="Admin Principal">Admin Principal</option>
          <option value="Carlos Supervisor">Carlos Supervisor</option>
          <option value="María Admin">María Admin</option>
        </select>
        <select className="admin-filters__select" value={moduloFilter} onChange={(e) => setModuloFilter(e.target.value)}>
          <option value="">Todos los módulos</option>
          <option value="Trabajadores">Trabajadores</option>
          <option value="Seguridad">Seguridad</option>
          <option value="Sedes">Sedes</option>
          <option value="Dispositivos">Dispositivos</option>
          <option value="Usuarios">Usuarios</option>
          <option value="Horarios">Horarios</option>
        </select>
        <select className="admin-filters__select" value={accionFilter} onChange={(e) => setAccionFilter(e.target.value)}>
          <option value="">Todas las acciones</option>
          <option value="Crear">Crear</option>
          <option value="Actualizar">Actualizar</option>
          <option value="Eliminar">Eliminar</option>
        </select>
        <button type="button" className="admin-filters__clear" onClick={clearFilters}>Limpiar filtros</button>
      </div>

      <div className="admin-table-container">
        <h2 className="admin-table-container__title">Historial de actividades</h2>
        <table className="admin-table">
          <thead>
            <tr>
              <th>Fecha/Hora</th>
              <th>Usuario</th>
              <th>Módulo</th>
              <th>Acción</th>
              <th>Sede</th>
              <th>IP</th>
              <th>Dispositivo</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((a) => (
              <tr key={a.id}>
                <td>{a.fechaHora}</td>
                <td>{a.usuario}</td>
                <td><span className={`admin-badge ${moduloBadgeClass(a.modulo)}`}>{a.modulo}</span></td>
                <td><span className={`admin-badge ${accionBadgeClass(a.accion)}`}>{a.accion}</span></td>
                <td>{a.sede}</td>
                <td>{a.ip}</td>
                <td>{a.dispositivo}</td>
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
