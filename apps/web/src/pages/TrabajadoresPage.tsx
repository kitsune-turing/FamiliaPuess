import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { AdminLayout } from "../components/AdminLayout";

interface Trabajador {
  id: number;
  nombre: string;
  documento: string;
  sede: string;
  entrada: string;
  estado: string;
  dispositivo: string;
}

const MOCK_DATA: Trabajador[] = [
  { id: 1, nombre: "Carlos Rodríguez", documento: "1234567890", sede: "Sede Principal", entrada: "07:58 AM", estado: "Activo", dispositivo: "Desktop-01" },
  { id: 2, nombre: "María López", documento: "0987654321", sede: "Sede Norte", entrada: "08:02 AM", estado: "Activo", dispositivo: "Desktop-02" },
  { id: 3, nombre: "Juan Pérez", documento: "1122334455", sede: "Sede Principal", entrada: "08:15 AM", estado: "Activo", dispositivo: "Desktop-01" },
  { id: 4, nombre: "Ana García", documento: "5566778899", sede: "Sede Sur", entrada: "07:45 AM", estado: "Inactivo", dispositivo: "Desktop-03" },
  { id: 5, nombre: "Pedro Martínez", documento: "6677889900", sede: "Sede Principal", entrada: "08:30 AM", estado: "Activo", dispositivo: "Desktop-01" },
];

export function TrabajadoresPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const filtered = MOCK_DATA.filter(
    (t) =>
      t.nombre.toLowerCase().includes(search.toLowerCase()) ||
      t.documento.includes(search),
  );

  return (
    <AdminLayout title="Trabajadores" subtitle="Gestión de trabajadores del sistema">
      <div className="admin-filters">
        <input
          type="text"
          className="admin-filters__search"
          placeholder="Buscar trabajador..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="admin-actions" style={{ marginBottom: 0 }}>
          <button type="button" className="admin-btn admin-btn--secondary">Importar</button>
          <button type="button" className="admin-btn admin-btn--primary">Nuevo trabajador</button>
        </div>
      </div>

      <div className="admin-table-container">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Trabajador</th>
              <th>Documento</th>
              <th>Sede</th>
              <th>Entrada</th>
              <th>Estado</th>
              <th>Dispositivo</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((t) => (
              <tr key={t.id}>
                <td>{t.nombre}</td>
                <td>{t.documento}</td>
                <td>{t.sede}</td>
                <td>{t.entrada}</td>
                <td>
                  <span className={`admin-badge ${t.estado === "Activo" ? "admin-badge--green" : "admin-badge--red"}`}>
                    {t.estado}
                  </span>
                </td>
                <td>{t.dispositivo}</td>
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
