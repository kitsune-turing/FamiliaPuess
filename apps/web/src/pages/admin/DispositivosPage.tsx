import { useEffect, useMemo, useState, type ReactNode } from "react";
import { useSearchParams } from "react-router-dom";
import {
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
  BoxIcon,
  EditIcon,
  MonitorIcon,
  MonitorOffIcon,
  PlusIcon,
  RefreshIcon,
  TrashIcon,
  WifiOffIcon,
} from "../../components/ui/Icons";
import { useDatos } from "../../context/DataProvider";
import { useToast } from "../../context/ToastProvider";
import { usePaginacion } from "../../hooks";
import { coincide } from "../../lib/format";
import type { Dispositivo } from "../../types/admin";

const POR_PAGINA = 5;

const VACIO: Dispositivo = {
  id: "",
  nombre: "",
  codigo: "",
  sede: "",
  ultimaConexion: "Sin conexión previa",
  estado: "fuera_de_linea",
  version: "v2.4.1",
  activo: true,
};

export function DispositivosPage() {
  const { dispositivos, sedes, guardarDispositivo, eliminarDispositivo } = useDatos();
  const { mostrar } = useToast();
  const [parametros, setParametros] = useSearchParams();

  const [busqueda, setBusqueda] = useState("");
  const [filtroSede, setFiltroSede] = useState("todas");
  const [filtroEstado, setFiltroEstado] = useState("todos");
  const [editando, setEditando] = useState<Dispositivo | null>(null);
  const [aEliminar, setAEliminar] = useState<Dispositivo | null>(null);

  useEffect(() => {
    if (parametros.get("nuevo")) {
      setEditando({ ...VACIO, sede: sedes[0]?.nombre ?? "" });
      parametros.delete("nuevo");
      setParametros(parametros, { replace: true });
    }
  }, [parametros, setParametros, sedes]);

  const metricas = useMemo(
    () => ({
      total: dispositivos.length,
      activos: dispositivos.filter((d) => d.activo).length,
      inactivos: dispositivos.filter((d) => !d.activo).length,
      sinConexion: dispositivos.filter((d) => d.estado === "fuera_de_linea").length,
    }),
    [dispositivos],
  );

  const filtrados = useMemo(
    () =>
      dispositivos.filter((dispositivo) => {
        const porTexto =
          coincide(dispositivo.nombre, busqueda) ||
          coincide(dispositivo.codigo, busqueda) ||
          coincide(dispositivo.sede, busqueda);
        const porSede = filtroSede === "todas" || dispositivo.sede === filtroSede;
        const porEstado =
          filtroEstado === "todos" ||
          (filtroEstado === "activo" ? dispositivo.activo : !dispositivo.activo);
        return porTexto && porSede && porEstado;
      }),
    [dispositivos, busqueda, filtroSede, filtroEstado],
  );

  const paginacion = usePaginacion(filtrados, POR_PAGINA);

  const guardar = async () => {
    if (!editando) return;
    if (!editando.nombre.trim() || !editando.codigo.trim()) {
      mostrar("El nombre y el código del dispositivo son obligatorios.", "error");
      return;
    }
    const esNuevo = !editando.id;
    try {
      await guardarDispositivo({ ...editando, id: editando.id || `disp-${Date.now()}` });
      setEditando(null);
      mostrar(esNuevo ? "Dispositivo agregado." : "Dispositivo actualizado.");
    } catch (e) {
      mostrar(e instanceof Error ? e.message : "Error al guardar el dispositivo.", "error");
    }
  };

  return (
    <>
      {/* ------------------------------------------------------ Métricas - */}
      <div className="stat-grid">
        <StatBox icono={<MonitorIcon size={26} />} color="pink" etiqueta="Total dispositivos" valor={metricas.total} />
        <StatBox icono={<BoxIcon size={26} />} color="pink" etiqueta="Dispositivos activos" valor={metricas.activos} />
        <StatBox
          icono={<MonitorOffIcon size={26} />}
          color="yellow"
          etiqueta="Dispositivos inactivos"
          valor={metricas.inactivos}
        />
        <StatBox icono={<WifiOffIcon size={26} />} color="yellow" etiqueta="Sin conexión" valor={metricas.sinConexion} />
      </div>

      {/* ---------------------------------------- Filtros y acciones -- */}
      <Card>
        <div className="filters">
          <SearchInput
            valor={busqueda}
            alCambiar={setBusqueda}
            placeholder="Buscar dispositivo"
            etiquetaAccesible="Buscar dispositivo por nombre, código o sede"
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
          <SelectField
            etiqueta="Estado"
            valor={filtroEstado}
            alCambiar={setFiltroEstado}
            opciones={[
              { valor: "todos", etiqueta: "Todos los estados" },
              { valor: "activo", etiqueta: "Activos" },
              { valor: "inactivo", etiqueta: "Inactivos" },
            ]}
          />
          <button
            type="button"
            className="btn btn--primary"
            onClick={() => setEditando({ ...VACIO, sede: sedes[0]?.nombre ?? "" })}
          >
            <PlusIcon size={20} /> Agregar dispositivo
          </button>
        </div>
      </Card>

      {/* -------------------------------------------------------- Tabla -- */}
      <Card>
      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>Dispositivo</th>
              <th>Código</th>
              <th>Sede</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {paginacion.visibles.length === 0 ? (
              <EmptyRow columnas={5} mensaje={
                  dispositivos.length === 0
                  ? "Aún no hay dispositivos registrados."
                  : "No hay dispositivos que coincidan con los filtros."
                } />
            ) : (
              paginacion.visibles.map((dispositivo) => (
                <tr key={dispositivo.id}>
                  <td>{dispositivo.nombre}</td>
                  <td>{dispositivo.codigo}</td>
                  <td>{dispositivo.sede}</td>
                  <td>
                    <BadgeOutline tono={dispositivo.activo ? "green" : "pink"}>
                      {dispositivo.activo ? "Activo" : "Inactivo"}
                    </BadgeOutline>
                  </td>
                  <td>
                    <div className="table__actions">
                      <button
                        type="button"
                        className="btn btn--icon"
                        aria-label={`Sincronizar ${dispositivo.nombre}`}
                        onClick={() => mostrar(`${dispositivo.nombre} sincronizado.`)}
                      >
                        <RefreshIcon size={18} />
                      </button>
                      <button
                        type="button"
                        className="btn btn--icon"
                        aria-label={`Editar ${dispositivo.nombre}`}
                        onClick={() => setEditando(dispositivo)}
                      >
                        <EditIcon size={19} />
                      </button>
                      <button
                        type="button"
                        className="btn btn--icon"
                        aria-label={`Eliminar ${dispositivo.nombre}`}
                        onClick={() => setAEliminar(dispositivo)}
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
        info={`Mostrando ${paginacion.desde} a ${paginacion.hasta} de ${paginacion.total} dispositivos`}
        irA={paginacion.irA}
      />
      </Card>

      {/* ------------------------------------------------------- Modales - */}
      <Modal
        abierto={editando !== null}
        titulo={editando?.id ? "Editar dispositivo" : "Agregar dispositivo"}
        subtitulo="Cada dispositivo genera los códigos QR de una sede."
        ancho="ancho"
        alCerrar={() => setEditando(null)}
        pie={
          <>
            <button type="button" className="btn btn--neutral" onClick={() => setEditando(null)}>
              Cancelar
            </button>
            <button type="button" className="btn btn--primary" onClick={guardar}>
              Guardar dispositivo
            </button>
          </>
        }
      >
        {editando ? (
          <>
            <div className="modal__grid">
              <TextField
                etiqueta="Nombre"
                requerido
                placeholder="PV-01"
                valor={editando.nombre}
                alCambiar={(v) => setEditando({ ...editando, nombre: v })}
              />
              <TextField
                etiqueta="Código"
                requerido
                placeholder="DHI-001J"
                valor={editando.codigo}
                alCambiar={(v) => setEditando({ ...editando, codigo: v.toUpperCase() })}
              />
              <SelectField
                etiqueta="Sede"
                valor={editando.sede}
                opciones={sedes.map((s) => ({ valor: s.nombre, etiqueta: s.nombre }))}
                alCambiar={(v) => setEditando({ ...editando, sede: v })}
              />
            </div>
            <div className="setting-row">
              <div>
                <p className="setting-row__label">Dispositivo activo</p>
                <p className="setting-row__hint">
                  Un dispositivo inactivo deja de emitir códigos QR válidos de inmediato.
                </p>
              </div>
              <Switch
                marcado={editando.activo}
                etiqueta="Dispositivo activo"
                alCambiar={(v) => setEditando({ ...editando, activo: v })}
              />
            </div>
          </>
        ) : null}
      </Modal>

      <ConfirmDialog
        abierto={aEliminar !== null}
        titulo="Eliminar dispositivo"
        mensaje={`Se eliminará ${aEliminar?.nombre ?? ""} (${aEliminar?.codigo ?? ""}). Los registros hechos desde este dispositivo se conservan.`}
        alCerrar={() => setAEliminar(null)}
        alConfirmar={async () => {
          if (aEliminar) {
            try {
              await eliminarDispositivo(aEliminar.id);
              mostrar("Dispositivo eliminado.");
            } catch (e) {
              mostrar(e instanceof Error ? e.message : "Error al eliminar el dispositivo.", "error");
            }
          }
          setAEliminar(null);
        }}
      />
    </>
  );
}

/** Variante de métrica con borde, usada dentro de la tarjeta de dispositivos. */
function StatBox({
  icono,
  color,
  etiqueta,
  valor,
}: {
  icono: ReactNode;
  color: "pink" | "yellow";
  etiqueta: string;
  valor: number;
}) {
  return (
    <article
      className="stat-card"
    >
      <div className={`stat-card__icon stat-card__icon--${color}`}>{icono}</div>
      <div className="stat-card__body">
        <p className="stat-card__label">{etiqueta}</p>
        <p className="stat-card__value">{valor}</p>
        <p className="stat-card__hint">En total</p>
      </div>
    </article>
  );
}
