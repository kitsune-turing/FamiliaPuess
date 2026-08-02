import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { AdminLayout } from "../components/AdminLayout";

interface Usuario {
  id: number;
  nombre: string;
  correo: string;
  rol: string;
  sede: string;
  estado: string;
  ultimoAcceso: string;
}

const CARDS = [
  { label: "Total usuarios", value: 15, iconClass: "admin-card__icon--pink" },
  { label: "Usuarios activos", value: 12, iconClass: "admin-card__icon--green" },
  { label: "Súper admins", value: 2, iconClass: "admin-card__icon--gold" },
  { label: "Administradores", value: 10, iconClass: "admin-card__icon--orange" },
];

const MOCK_DATA: Usuario[] = [
  { id: 1, nombre: "Admin Principal", correo: "admin@familiapuess.com", rol: "Súper admin", sede: "Sede Principal", estado: "Activo", ultimoAcceso: "Hoy, 08:00 AM" },
  { id: 2, nombre: "Carlos Supervisor", correo: "carlos@familiapuess.com", rol: "Administrador", sede: "Sede Norte", estado: "Activo", ultimoAcceso: "Hoy, 07:45 AM" },
  { id: 3, nombre: "María Admin", correo: "maria@familiapuess.com", rol: "Administrador", sede: "Sede Sur", estado: "Activo", ultimoAcceso: "Ayer, 17:30 PM" },
  { id: 4, nombre: "Pedro Gestor", correo: "pedro@familiapuess.com", rol: "Administrador", sede: "Sede Principal", estado: "Inactivo", ultimoAcceso: "15/07/2026" },
  { id: 5, nombre: "Ana Super", correo: "ana@familiapuess.com", rol: "Súper admin", sede: "Sede Principal", estado: "Activo", ultimoAcceso: "Hoy, 09:15 AM" },
];

function rolBadgeClass(rol: string): string {
  if (rol === "Súper admin") return "admin-badge--pink";
  return "admin-badge--orange";
}

export function UsuariosPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [rolFilter, setRolFilter] = useState("");
  const [estadoFilter, setEstadoFilter] = useState("");

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const filtered = MOCK_DATA.filter((u) => {
    if (search && !u.nombre.toLowerCase().includes(search.toLowerCase()) && !u.correo.toLowerCase().includes(search.toLowerCase())) return false;
    if (rolFilter && u.rol !== rolFilter) return false;
    if (estadoFilter && u.estado !== estadoFilter) return false;
    return true;
  });

  const clearFilters = () => {
    setSearch("");
    setRolFilter("");
    setEstadoFilter("");
  };

  return (
    <AdminLayout title="Usuarios" subtitle="Gestión de usuarios del sistema">
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
          placeholder="Buscar usuario..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select className="admin-filters__select" value={rolFilter} onChange={(e) => setRolFilter(e.target.value)}>
          <option value="">Todos los roles</option>
          <option value="Súper admin">Súper admin</option>
          <option value="Administrador">Administrador</option>
        </select>
        <select className="admin-filters__select" value={estadoFilter} onChange={(e) => setEstadoFilter(e.target.value)}>
          <option value="">Todos los estados</option>
          <option value="Activo">Activo</option>
          <option value="Inactivo">Inactivo</option>
        </select>
        <button type="button" className="admin-filters__clear" onClick={clearFilters}>Limpiar filtros</button>
        <button type="button" className="admin-btn admin-btn--primary">Nuevo usuario</button>
      </div>

      <div className="admin-table-container">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Usuario</th>
              <th>Correo electrónico</th>
              <th>Rol</th>
              <th>Sede</th>
              <th>Estado</th>
              <th>Último acceso</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((u) => (
              <tr key={u.id}>
                <td>{u.nombre}</td>
                <td>{u.correo}</td>
                <td><span className={`admin-badge ${rolBadgeClass(u.rol)}`}>{u.rol}</span></td>
                <td>{u.sede}</td>
                <td>
                  <span className={`admin-badge ${u.estado === "Activo" ? "admin-badge--green" : "admin-badge--red"}`}>
                    {u.estado}
                  </span>
                </td>
                <td>{u.ultimoAcceso}</td>
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
