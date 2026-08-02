import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { AdminLayout } from "../components/AdminLayout";

interface Dispositivo {
  id: number;
  nombre: string;
  codigo: string;
  sede: string;
  ultimaConexion: string;
  estado: string;
  version: string;
}

const CARDS = [
  { label: "Total dispositivos", value: 12, iconClass: "admin-card__icon--pink" },
  { label: "En línea", value: 8, iconClass: "admin-card__icon--green" },
  { label: "Con problemas", value: 2, iconClass: "admin-card__icon--orange" },
  { label: "Fuera de línea", value: 2, iconClass: "admin-card__icon--gold" },
];

const MOCK_DATA: Dispositivo[] = [
  { id: 1, nombre: "Desktop Principal", codigo: "DSK-001", sede: "Sede Principal", ultimaConexion: "Hace 2 min", estado: "En línea", version: "2.1.0" },
  { id: 2, nombre: "Desktop Recepción", codigo: "DSK-002", sede: "Sede Norte", ultimaConexion: "Hace 5 min", estado: "En línea", version: "2.1.0" },
  { id: 3, nombre: "Desktop Almacén", codigo: "DSK-003", sede: "Sede Sur", ultimaConexion: "Hace 1 hora", estado: "Problemas", version: "2.0.8" },
  { id: 4, nombre: "Desktop Entrada", codigo: "DSK-004", sede: "Sede Principal", ultimaConexion: "Hace 3 días", estado: "Fuera de línea", version: "2.0.5" },
  { id: 5, nombre: "Desktop Cafetería", codigo: "DSK-005", sede: "Sede Norte", ultimaConexion: "Hace 1 min", estado: "En línea", version: "2.1.0" },
];

function badgeClass(estado: string): string {
  if (estado === "En línea") return "admin-badge--green";
  if (estado === "Problemas") return "admin-badge--pink";
  return "admin-badge--gold";
}

export function DispositivosPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [sedeFilter, setSedeFilter] = useState("");
  const [estadoFilter, setEstadoFilter] = useState("");

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const filtered = MOCK_DATA.filter((d) => {
    if (sedeFilter && d.sede !== sedeFilter) return false;
    if (estadoFilter && d.estado !== estadoFilter) return false;
    return true;
  });

  return (
    <AdminLayout title="Dispositivos" subtitle="Gestión de dispositivos del sistema">
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
        <select className="admin-filters__select" value={sedeFilter} onChange={(e) => setSedeFilter(e.target.value)}>
          <option value="">Todas las sedes</option>
          <option value="Sede Principal">Sede Principal</option>
          <option value="Sede Norte">Sede Norte</option>
          <option value="Sede Sur">Sede Sur</option>
        </select>
        <select className="admin-filters__select" value={estadoFilter} onChange={(e) => setEstadoFilter(e.target.value)}>
          <option value="">Todos los estados</option>
          <option value="En línea">En línea</option>
          <option value="Problemas">Problemas</option>
          <option value="Fuera de línea">Fuera de línea</option>
        </select>
        <button type="button" className="admin-btn admin-btn--primary">Agregar dispositivo</button>
      </div>

      <div className="admin-table-container">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Dispositivo</th>
              <th>Código</th>
              <th>Sede</th>
              <th>Última conexión</th>
              <th>Estado</th>
              <th>Versión</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((d) => (
              <tr key={d.id}>
                <td>{d.nombre}</td>
                <td>{d.codigo}</td>
                <td>{d.sede}</td>
                <td>{d.ultimaConexion}</td>
                <td><span className={`admin-badge ${badgeClass(d.estado)}`}>{d.estado}</span></td>
                <td>{d.version}</td>
                <td>
                  <div className="admin-table__actions">
                    <button type="button" className="admin-table__action-btn" title="Ver">&#128065;</button>
                    <button type="button" className="admin-table__action-btn" title="Editar">&#9998;</button>
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
