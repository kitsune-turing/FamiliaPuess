import { useMemo, useState } from "react";
import {
  Badge,
  BadgeOutline,
  Card,
  ConfirmDialog,
  EmptyRow,
  Modal,
  Pagination,
  SearchInput,
  SelectField,
  Switch,
  TextField,
} from "../../components/ui";
import {
  BuildingCheckIcon,
  BuildingIcon,
  BuildingOffIcon,
  BuildingXIcon,
  EditIcon,
  MonitorIcon,
  PlusIcon,
  RefreshIcon,
  TrashIcon,
} from "../../components/ui/Icons";
import { StatCard } from "../../components/ui";
import { useDatos } from "../../context/DataProvider";
import { useToast } from "../../context/ToastProvider";
import { usePaginacion } from "../../hooks";
import { coincide, porcentaje } from "../../lib/format";
import type { Dispositivo, Sede } from "../../types/admin";

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
  const { sedes, dispositivos, guardarSede, eliminarSede, guardarDispositivo } = useDatos();
  const { mostrar } = useToast();

  const [busqueda, setBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("todos");
  const [editando, setEditando] = useState<Sede | null>(null);
  const [aEliminar, setAEliminar] = useState<Sede | null>(null);

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
          coincide(sede.direccion, busqueda);
        const porEstado =
          filtroEstado === "todos" || (filtroEstado === "activa" ? sede.activa : !sede.activa);
        return porTexto && porEstado;
      }),
    [sedes, busqueda, filtroEstado],
  );

  const paginacion = usePaginacion(filtradas, POR_PAGINA);

  const limpiarFiltros = () => {
    setBusqueda("");
    setFiltroEstado("todos");
    mostrar("Filtros restablecidos.", "info");
  };

  const guardar = async () => {
    if (!editando) return;
    if (!editando.nombre.trim() || !editando.direccion.trim()) {
      mostrar("El nombre y la dirección de la sede son obligatorios.", "error");
      return;
    }
    const esNueva = !editando.id;
    try {
      await guardarSede({ ...editando, id: editando.id || `sede-${Date.now()}` });
      setEditando(null);
      mostrar(esNueva ? "Sede creada." : "Sede actualizada.");
    } catch (e) {
      mostrar(e instanceof Error ? e.message : "Error al guardar la sede.", "error");
    }
  };

  // Dispositivos de la sede que se está editando y dispositivos sin asignar
  const dispositivosDeSede = useMemo(
    () => editando?.id
      ? dispositivos.filter((d) => {
          const sedeNombre = editando.nombre;
          return d.sede === sedeNombre;
        })
      : [],
    [dispositivos, editando],
  );

  const dispositivosSinAsignar = useMemo(
    () => dispositivos.filter((d) => !d.sede || d.sede === ""),
    [dispositivos],
  );

  const asignarDispositivo = async (dispositivo: Dispositivo) => {
    if (!editando) return;
    try {
      await guardarDispositivo({ ...dispositivo, sede: editando.nombre });
      mostrar(`${dispositivo.nombre || dispositivo.codigo} asignado a ${editando.nombre}.`);
    } catch (e) {
      mostrar(e instanceof Error ? e.message : "Error al asignar dispositivo.", "error");
    }
  };

  const desasignarDispositivo = async (dispositivo: Dispositivo) => {
    try {
      await guardarDispositivo({ ...dispositivo, sede: "" });
      mostrar(`${dispositivo.nombre || dispositivo.codigo} desasignado.`);
    } catch (e) {
      mostrar(e instanceof Error ? e.message : "Error al desasignar dispositivo.", "error");
    }
  };

  const toggleActivoDispositivo = async (dispositivo: Dispositivo) => {
    try {
      await guardarDispositivo({ ...dispositivo, activo: !dispositivo.activo });
      mostrar(`${dispositivo.nombre || dispositivo.codigo} ${dispositivo.activo ? "desactivado" : "activado"}.`);
    } catch (e) {
      mostrar(e instanceof Error ? e.message : "Error al cambiar estado.", "error");
    }
  };

  return (
    <>
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

      {/* ----------------------------------------- Filtros y acciones -- */}
      <Card>
        <div className="filters">
          <SearchInput valor={busqueda} alCambiar={setBusqueda} placeholder="Buscar sede" />
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
          <button type="button" className="btn btn--ghost" onClick={limpiarFiltros}>
            <RefreshIcon size={20} /> Limpiar filtros
          </button>
          <button type="button" className="btn btn--primary" onClick={() => setEditando({ ...VACIA })}>
            <PlusIcon size={20} /> Nueva sede
          </button>
        </div>
      </Card>

      {/* -------------------------------------------------------- Tabla -- */}
      <Card>
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Sede</th>
                <th>Dirección</th>
                <th>Trabajadores</th>
                <th>Dispositivos</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {paginacion.visibles.length === 0 ? (
                <EmptyRow columnas={6} mensaje={
                  sedes.length === 0
                    ? "Aún no hay sedes registradas."
                    : "No hay sedes que coincidan con los filtros."
                } />
              ) : (
                paginacion.visibles.map((sede) => (
                  <tr key={sede.id}>
                    <td>{sede.nombre}</td>
                    <td>{sede.direccion}</td>
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

            {/* ─── Dispositivos asociados ─── */}
            {editando.id ? (
              <div style={{ marginTop: 20 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                  <MonitorIcon size={20} />
                  <h3 style={{ margin: 0, fontSize: 15, fontWeight: 600, color: "var(--fp-text)" }}>
                    Dispositivos asociados
                  </h3>
                </div>

                {dispositivosDeSede.length === 0 ? (
                  <p style={{ color: "var(--fp-text-muted)", fontSize: 14, marginBottom: 12 }}>
                    No hay dispositivos asociados a esta sede.
                  </p>
                ) : (
                  <div className="table-wrap" style={{ marginBottom: 12 }}>
                    <table className="table">
                      <thead>
                        <tr>
                          <th>Identificador</th>
                          <th>Descripción</th>
                          <th>Estado</th>
                          <th>Acciones</th>
                        </tr>
                      </thead>
                      <tbody>
                        {dispositivosDeSede.map((d) => (
                          <tr key={d.id}>
                            <td style={{ fontFamily: "ui-monospace, monospace", fontSize: 13 }}>
                              {d.codigo}
                            </td>
                            <td>{d.nombre}</td>
                            <td>
                              <BadgeOutline tono={d.activo ? "green" : "pink"}>
                                {d.activo ? "Activo" : "Inactivo"}
                              </BadgeOutline>
                            </td>
                            <td>
                              <div className="table__actions">
                                <button
                                  type="button"
                                  className="btn btn--ghost"
                                  style={{ fontSize: 13, padding: "4px 10px" }}
                                  onClick={() => toggleActivoDispositivo(d)}
                                >
                                  {d.activo ? "Desactivar" : "Activar"}
                                </button>
                                <button
                                  type="button"
                                  className="btn btn--ghost"
                                  style={{ fontSize: 13, padding: "4px 10px", color: "var(--fp-pink)" }}
                                  onClick={() => desasignarDispositivo(d)}
                                >
                                  Desasignar
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Dispositivos disponibles para asignar */}
                {dispositivosSinAsignar.length > 0 && (
                  <>
                    <p style={{ fontSize: 13, fontWeight: 600, color: "var(--fp-text-muted)", marginBottom: 8 }}>
                      Dispositivos disponibles para asignar:
                    </p>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                      {dispositivosSinAsignar.map((d) => (
                        <button
                          key={d.id}
                          type="button"
                          className="btn btn--ghost"
                          style={{
                            fontSize: 13,
                            padding: "6px 14px",
                            border: "1px dashed var(--fp-border)",
                            borderRadius: 8,
                          }}
                          onClick={() => asignarDispositivo(d)}
                        >
                          <PlusIcon size={14} />
                          {d.nombre || d.codigo}
                        </button>
                      ))}
                    </div>
                  </>
                )}
              </div>
            ) : null}
          </>
        ) : null}
      </Modal>

      <ConfirmDialog
        abierto={aEliminar !== null}
        titulo="Eliminar sede"
        mensaje={`Se eliminará ${aEliminar?.nombre ?? ""}. Los trabajadores y dispositivos asociados quedarán sin sede asignada.`}
        alCerrar={() => setAEliminar(null)}
        alConfirmar={async () => {
          if (aEliminar) {
            try {
              await eliminarSede(aEliminar.id);
              mostrar("Sede eliminada.");
            } catch (e) {
              mostrar(e instanceof Error ? e.message : "Error al eliminar la sede.", "error");
            }
          }
          setAEliminar(null);
        }}
      />
    </>
  );
}
