import { useMemo, useState } from "react";
import {
  Badge,
  Card,
  ConfirmDialog,
  EmptyRow,
  Modal,
  Pagination,
  SearchInput,
  SelectField,
  Switch,
  TextField,
} from "../components/ui";
import {
  BuildingCheckIcon,
  BuildingIcon,
  BuildingOffIcon,
  BuildingXIcon,
  EditIcon,
  PlusIcon,
  RefreshIcon,
  TrashIcon,
} from "../components/ui/Icons";
import { StatCard } from "../components/ui";
import { useDatos } from "../context/DataProvider";
import { useToast } from "../context/ToastProvider";
import { usePaginacion } from "../hooks";
import { coincide, porcentaje } from "../lib/format";
import type { Sede } from "../types/admin";

const POR_PAGINA = 5;

const VACIA: Sede = {
  id: "",
  nombre: "",
  direccion: "",
  ciudad: "",
  trabajadores: 0,
  dispositivos: 0,
  activa: true,
  telefono: "",
  responsable: "",
};

export function SedesPage() {
  const { sedes, guardarSede, eliminarSede } = useDatos();
  const { mostrar } = useToast();

  const [busqueda, setBusqueda] = useState("");
  const [filtroCiudad, setFiltroCiudad] = useState("todas");
  const [filtroEstado, setFiltroEstado] = useState("todos");
  const [filtroSede, setFiltroSede] = useState("todas");
  const [editando, setEditando] = useState<Sede | null>(null);
  const [aEliminar, setAEliminar] = useState<Sede | null>(null);

  // Las ciudades del filtro salen de las sedes ya registradas.
  const ciudades = useMemo(
    () => Array.from(new Set(sedes.map((s) => s.ciudad).filter(Boolean))).sort(),
    [sedes],
  );

  const metricas = useMemo(() => {
    const total = sedes.length;
    const activas = sedes.filter((s) => s.activa).length;
    return {
      total,
      activas,
      inactivas: total - activas,
      sinDispositivos: sedes.filter((s) => s.dispositivos === 0).length,
    };
  }, [sedes]);

  const filtradas = useMemo(
    () =>
      sedes.filter((sede) => {
        const porTexto =
          coincide(sede.nombre, busqueda) ||
          coincide(sede.direccion, busqueda) ||
          coincide(sede.ciudad, busqueda);
        const porCiudad = filtroCiudad === "todas" || sede.ciudad === filtroCiudad;
        const porEstado =
          filtroEstado === "todos" || (filtroEstado === "activa" ? sede.activa : !sede.activa);
        const porSede = filtroSede === "todas" || sede.nombre === filtroSede;
        return porTexto && porCiudad && porEstado && porSede;
      }),
    [sedes, busqueda, filtroCiudad, filtroEstado, filtroSede],
  );

  const paginacion = usePaginacion(filtradas, POR_PAGINA);

  const limpiarFiltros = () => {
    setBusqueda("");
    setFiltroCiudad("todas");
    setFiltroEstado("todos");
    setFiltroSede("todas");
    mostrar("Filtros restablecidos.", "info");
  };

  const guardar = () => {
    if (!editando) return;
    if (!editando.nombre.trim() || !editando.direccion.trim()) {
      mostrar("El nombre y la dirección de la sede son obligatorios.", "error");
      return;
    }
    const esNueva = !editando.id;
    guardarSede({ ...editando, id: editando.id || `sede-${Date.now()}` });
    setEditando(null);
    mostrar(esNueva ? "Sede creada." : "Sede actualizada.");
  };

  return (
    <>
      <div className="page-actions">
        <button type="button" className="btn btn--primary" onClick={() => setEditando({ ...VACIA })}>
          <PlusIcon size={20} /> Nueva sede
        </button>
      </div>

      {/* ------------------------------------------------------ Métricas - */}
      <div className="stat-grid">
        <StatCard
          icono={<BuildingIcon size={26} />}
          color="yellow"
          etiqueta="Total sedes"
          valor={metricas.total}
          pista="En total"
        />
        <StatCard
          icono={<BuildingCheckIcon size={26} />}
          color="yellow"
          etiqueta="Sedes activas"
          valor={metricas.activas}
          pista={`${porcentaje(metricas.activas, metricas.total)} del total`}
        />
        <StatCard
          icono={<BuildingXIcon size={26} />}
          color="pink"
          etiqueta="Sedes inactivas"
          valor={metricas.inactivas}
          pista={`${porcentaje(metricas.inactivas, metricas.total)} del total`}
        />
        <StatCard
          icono={<BuildingOffIcon size={26} />}
          color="pink"
          etiqueta="Sedes sin dispositivos"
          valor={metricas.sinDispositivos}
          pista={`${porcentaje(metricas.sinDispositivos, metricas.total)} del total`}
        />
      </div>

      {/* ------------------------------------------------------- Filtros - */}
      <Card>
        <div className="filters">
          <SearchInput valor={busqueda} alCambiar={setBusqueda} placeholder="Buscar sede" />
          <SelectField
            etiqueta="Ciudad"
            valor={filtroCiudad}
            alCambiar={setFiltroCiudad}
            opciones={[
              { valor: "todas", etiqueta: "Todas las ciudades" },
              ...ciudades.map((c) => ({ valor: c, etiqueta: c })),
            ]}
          />
          <SelectField
            etiqueta="Estado"
            valor={filtroEstado}
            alCambiar={setFiltroEstado}
            opciones={[
              { valor: "todos", etiqueta: "Todos los estados" },
              { valor: "activa", etiqueta: "Activas" },
              { valor: "inactiva", etiqueta: "Inactivas" },
            ]}
          />
          <SelectField
            etiqueta="Sede"
            valor={filtroSede}
            alCambiar={setFiltroSede}
            opciones={[
              { valor: "todas", etiqueta: "Todas las sedes" },
              ...sedes.map((s) => ({ valor: s.nombre, etiqueta: s.nombre })),
            ]}
          />
          <button type="button" className="btn btn--ghost" onClick={limpiarFiltros}>
            <RefreshIcon size={20} /> Limpiar filtros
          </button>
        </div>
      </Card>

      {/* --------------------------------------------------------- Tabla - */}
      <Card>
        <div className="table-wrap">
          <table className="table">
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
              {paginacion.visibles.length === 0 ? (
                <EmptyRow columnas={7} mensaje={
                  sedes.length === 0
                    ? "Aún no hay sedes registradas."
                    : "No hay sedes que coincidan con los filtros."
                } />
              ) : (
                paginacion.visibles.map((sede) => (
                  <tr key={sede.id}>
                    <td>{sede.nombre}</td>
                    <td>{sede.direccion}</td>
                    <td>{sede.ciudad}</td>
                    <td>{sede.trabajadores}</td>
                    <td>{sede.dispositivos}</td>
                    <td>
                      <Badge tono={sede.activa ? "green" : "grey"}>
                        {sede.activa ? "Activa" : "Inactiva"}
                      </Badge>
                    </td>
                    <td>
                      <div className="table__actions">
                        <button
                          type="button"
                          className="btn btn--icon"
                          aria-label={`Editar ${sede.nombre}`}
                          onClick={() => setEditando(sede)}
                        >
                          <EditIcon size={19} />
                        </button>
                        <button
                          type="button"
                          className="btn btn--icon"
                          aria-label={`Eliminar ${sede.nombre}`}
                          onClick={() => setAEliminar(sede)}
                        >
                          <TrashIcon size={19} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <Pagination
          pagina={paginacion.pagina}
          totalPaginas={paginacion.totalPaginas}
          info={`Mostrando ${paginacion.desde} a ${paginacion.hasta} de ${paginacion.total} sedes`}
          irA={paginacion.irA}
        />
      </Card>

      {/* ------------------------------------------------------- Modales - */}
      <Modal
        abierto={editando !== null}
        titulo={editando?.id ? "Editar sede" : "Nueva sede"}
        subtitulo="La sede agrupa trabajadores, dispositivos y reportes de asistencia."
        ancho="ancho"
        alCerrar={() => setEditando(null)}
        pie={
          <>
            <button type="button" className="btn btn--neutral" onClick={() => setEditando(null)}>
              Cancelar
            </button>
            <button type="button" className="btn btn--primary" onClick={guardar}>
              Guardar sede
            </button>
          </>
        }
      >
        {editando ? (
          <>
            <div className="modal__grid">
              <TextField
                etiqueta="Nombre de la sede"
                requerido
                valor={editando.nombre}
                alCambiar={(v) => setEditando({ ...editando, nombre: v })}
              />
              <TextField
                etiqueta="Dirección"
                requerido
                placeholder="Cra 43 # 10-15"
                valor={editando.direccion}
                alCambiar={(v) => setEditando({ ...editando, direccion: v })}
              />
              <TextField
                etiqueta="Ciudad"
                requerido
                placeholder="Medellín"
                valor={editando.ciudad}
                alCambiar={(v) => setEditando({ ...editando, ciudad: v })}
              />
              <TextField
                etiqueta="Teléfono"
                valor={editando.telefono}
                alCambiar={(v) => setEditando({ ...editando, telefono: v })}
              />
              <TextField
                etiqueta="Responsable"
                valor={editando.responsable}
                alCambiar={(v) => setEditando({ ...editando, responsable: v })}
              />
            </div>
            <div className="setting-row">
              <div>
                <p className="setting-row__label">Sede activa</p>
                <p className="setting-row__hint">
                  Las sedes inactivas no aceptan registros de asistencia nuevos.
                </p>
              </div>
              <Switch
                marcado={editando.activa}
                etiqueta="Sede activa"
                alCambiar={(v) => setEditando({ ...editando, activa: v })}
              />
            </div>
          </>
        ) : null}
      </Modal>

      <ConfirmDialog
        abierto={aEliminar !== null}
        titulo="Eliminar sede"
        mensaje={`Se eliminará ${aEliminar?.nombre ?? ""}. Los trabajadores y dispositivos asociados quedarán sin sede asignada.`}
        alCerrar={() => setAEliminar(null)}
        alConfirmar={() => {
          if (aEliminar) {
            eliminarSede(aEliminar.id);
            mostrar("Sede eliminada.");
          }
          setAEliminar(null);
        }}
      />
    </>
  );
}
