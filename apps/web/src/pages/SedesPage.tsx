import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { AdminLayout } from "../components/AdminLayout";

interface Sede {
  id: number;
  nombre: string;
  direccion: string;
  ciudad: string;
  trabajadores: number;
  dispositivos: number;
  estado: string;
}

const CARDS = [
  { label: "Total sedes", value: 5, iconClass: "admin-card__icon--pink" },
  { label: "Sedes activas", value: 4, iconClass: "admin-card__icon--green" },
  { label: "Total trabajadores", value: 128, iconClass: "admin-card__icon--gold" },
  { label: "Total dispositivos", value: 12, iconClass: "admin-card__icon--orange" },
];

const MOCK_DATA: Sede[] = [
  { id: 1, nombre: "Sede Principal", direccion: "Calle 50 #30-20", ciudad: "Medellín", trabajadores: 45, dispositivos: 4, estado: "Activa" },
  { id: 2, nombre: "Sede Norte", direccion: "Carrera 65 #48-12", ciudad: "Medellín", trabajadores: 32, dispositivos: 3, estado: "Activa" },
  { id: 3, nombre: "Sede Sur", direccion: "Avenida 80 #15-40", ciudad: "Envigado", trabajadores: 28, dispositivos: 3, estado: "Activa" },
  { id: 4, nombre: "Sede Centro", direccion: "Calle 10 #43-15", ciudad: "Medellín", trabajadores: 23, dispositivos: 2, estado: "Activa" },
  { id: 5, nombre: "Sede Bodega", direccion: "Km 5 Vía Las Palmas", ciudad: "Rionegro", trabajadores: 0, dispositivos: 0, estado: "Inactiva" },
];

export function SedesPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [ciudadFilter, setCiudadFilter] = useState("");
  const [estadoFilter, setEstadoFilter] = useState("");

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const filtered = MOCK_DATA.filter((s) => {
    if (search && !s.nombre.toLowerCase().includes(search.toLowerCase())) return false;
    if (ciudadFilter && s.ciudad !== ciudadFilter) return false;
    if (estadoFilter && s.estado !== estadoFilter) return false;
    return true;
  });

  const clearFilters = () => {
    setSearch("");
    setCiudadFilter("");
    setEstadoFilter("");
  };

  return (
    <AdminLayout title="Sedes" subtitle="Gestión de sedes del sistema">
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
        <input
          type="text"
          className="admin-filters__search"
          placeholder="Buscar sede..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select className="admin-filters__select" value={ciudadFilter} onChange={(e) => setCiudadFilter(e.target.value)}>
          <option value="">Todas las ciudades</option>
          <option value="Medellín">Medellín</option>
          <option value="Envigado">Envigado</option>
          <option value="Rionegro">Rionegro</option>
        </select>
        <select className="admin-filters__select" value={estadoFilter} onChange={(e) => setEstadoFilter(e.target.value)}>
          <option value="">Todos los estados</option>
          <option value="Activa">Activa</option>
          <option value="Inactiva">Inactiva</option>
        </select>
        <button type="button" className="admin-filters__clear" onClick={clearFilters}>Limpiar filtros</button>
        <button type="button" className="admin-btn admin-btn--primary">Nueva sede</button>
      </div>

      <div className="admin-table-container">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Sede</th>
              <th>Dirección</th>
              <th>Ciudad</th>
              <th>Trabajadores</th>
              <th>Dispositivos</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((s) => (
              <tr key={s.id}>
                <td>{s.nombre}</td>
                <td>{s.direccion}</td>
                <td>{s.ciudad}</td>
                <td>{s.trabajadores}</td>
                <td>{s.dispositivos}</td>
                <td>
                  <span className={`admin-badge ${s.estado === "Activa" ? "admin-badge--green" : "admin-badge--red"}`}>
                    {s.estado}
                  </span>
                </td>
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
