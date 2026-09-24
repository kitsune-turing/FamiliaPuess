import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Card,
  ConfirmDialog,
  EmptyRow,
  Modal,
  Pagination,
  SearchInput,
  SelectField,
  TextField,
} from "../../components/ui";
import {
  ClockIcon,
  EditIcon,
  PlusIcon,
  RefreshIcon,
  TrashIcon,
} from "../../components/ui/Icons";
import { StatCard } from "../../components/ui";
import { useDatos } from "../../context/DataProvider";
import { useToast } from "../../context/ToastProvider";
import { usePaginacion } from "../../hooks";
import { coincide } from "../../lib/format";
import {
  listarHorarios,
  crearHorario,
  actualizarHorario,
  eliminarHorarioApi,
  type HorarioApi,
} from "../../services/adminApi";

const POR_PAGINA = 5;

interface HorarioLocal {
  id: string;
  nombre: string;
  sede: string;
  idSede: number;
  horaEntrada: string;
  horaSalida: string;
  vigenteDesde: string;
  vigenteHasta: string;
}

const VACIO: HorarioLocal = {
  id: "",
  nombre: "",
  sede: "",
  idSede: 0,
  horaEntrada: "07:00",
  horaSalida: "",
  vigenteDesde: new Date().toISOString().slice(0, 10),
  vigenteHasta: "",
};

function mapHorario(h: HorarioApi): HorarioLocal {
  return {
    id: String(h.id),
    nombre: h.nombre ?? `Horario #${h.id}`,
    sede: h.sede_nombre,
    idSede: h.id_sede,
    horaEntrada: h.hora_entrada?.slice(0, 5) ?? "07:00",
    horaSalida: h.hora_salida?.slice(0, 5) ?? "",
    vigenteDesde: h.vigente_desde,
    vigenteHasta: h.vigente_hasta ?? "",
  };
}

export function HorariosPage() {
  const { sedes } = useDatos();
  const { mostrar } = useToast();
  const sedesActivas = useMemo(() => sedes.filter((s) => s.activa), [sedes]);

  const [horarios, setHorarios] = useState<HorarioLocal[]>([]);
  const [cargando, setCargando] = useState(true);
  const [busqueda, setBusqueda] = useState("");
  const [filtroSede, setFiltroSede] = useState("todas");
  const [editando, setEditando] = useState<HorarioLocal | null>(null);
  const [aEliminar, setAEliminar] = useState<HorarioLocal | null>(null);

  const cargar = useCallback(async () => {
    setCargando(true);
    try {
      const res = await listarHorarios();
      setHorarios(res.items.map(mapHorario));
    } catch {
      mostrar("Error al cargar horarios.", "error");
    } finally {
      setCargando(false);
    }
  }, [mostrar]);

  useEffect(() => {
    cargar();
  }, [cargar]);

  const sedesNombres = useMemo(
    () => Array.from(new Set(horarios.map((h) => h.sede).filter(Boolean))).sort(),
    [horarios],
  );

  const filtrados = useMemo(
    () =>
      horarios.filter((h) => {
        const porTexto =
          coincide(h.nombre, busqueda) ||
          coincide(h.sede, busqueda) ||
          coincide(h.horaEntrada, busqueda);
        const porSede = filtroSede === "todas" || h.sede === filtroSede;
        return porTexto && porSede;
      }),
    [horarios, busqueda, filtroSede],
  );

  const { visibles, pagina, totalPaginas, irA } = usePaginacion(filtrados, POR_PAGINA);

  const metricas = useMemo(() => {
    const total = horarios.length;
    const sedesConHorario = new Set(horarios.map((h) => h.sede)).size;
    const vigentes = horarios.filter(
      (h) => !h.vigenteHasta || new Date(h.vigenteHasta) >= new Date(),
    ).length;
    return { total, sedesConHorario, vigentes };
  }, [horarios]);

  const guardar = async () => {
    if (!editando) return;
    if (!editando.horaEntrada) {
      mostrar("La hora de entrada es obligatoria.", "error");
      return;
    }

    const sedeObj = sedesActivas.find((s) => s.nombre === editando.sede);
    const idSede = sedeObj ? Number(sedeObj.id) : editando.idSede || 1;
    const numId = Number(editando.id);

    try {
      if (!editando.id || isNaN(numId)) {
        const nuevo = await crearHorario({
          id_sede: idSede,
          nombre: editando.nombre || undefined,
          hora_entrada: editando.horaEntrada,
          hora_salida: editando.horaSalida || undefined,
          vigente_desde: editando.vigenteDesde,
          vigente_hasta: editando.vigenteHasta || undefined,
        });
        setHorarios((prev) => [mapHorario(nuevo), ...prev]);
        mostrar("Horario creado.");
      } else {
        const actualizado = await actualizarHorario(numId, {
          id_sede: idSede,
          nombre: editando.nombre || undefined,
          hora_entrada: editando.horaEntrada,
          hora_salida: editando.horaSalida || undefined,
          vigente_desde: editando.vigenteDesde,
          vigente_hasta: editando.vigenteHasta || undefined,
        });
        setHorarios((prev) =>
          prev.map((h) => (h.id === editando.id ? mapHorario(actualizado) : h)),
        );
        mostrar("Horario actualizado.");
      }
      setEditando(null);
    } catch (e) {
      mostrar(e instanceof Error ? e.message : "Error al guardar el horario.", "error");
    }
  };

  return (
    <>
      <div className="stat-grid">
        <StatCard
          icono={<ClockIcon size={26} />}
          color="yellow"
          etiqueta="Total horarios"
          valor={metricas.total}
          pista="En total"
        />
        <StatCard
          icono={<ClockIcon size={26} />}
          color="yellow"
          etiqueta="Horarios vigentes"
          valor={metricas.vigentes}
          pista="Actualmente activos"
        />
        <StatCard
          icono={<RefreshIcon size={26} />}
          color="pink"
          etiqueta="Sedes con horario"
          valor={metricas.sedesConHorario}
          pista="Del total de sedes"
        />
      </div>

      <Card>
        <div className="filters">
          <SearchInput
            valor={busqueda}
            alCambiar={setBusqueda}
            placeholder="Buscar horario"
            etiquetaAccesible="Buscar horario por nombre o sede"
          />
          <SelectField
            etiqueta="Sede"
            valor={filtroSede}
            alCambiar={setFiltroSede}
            opciones={[
              { valor: "todas", etiqueta: "Todas las sedes" },
              ...sedesNombres.map((s) => ({ valor: s, etiqueta: s })),
            ]}
          />
          <div className="filters__actions">
            <button
              type="button"
              className="btn btn--primary"
              onClick={() =>
                setEditando({ ...VACIO, sede: sedesActivas[0]?.nombre ?? "" })
              }
            >
              <PlusIcon size={20} /> Nuevo horario
            </button>
          </div>
        </div>
      </Card>

      <Card>
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Sede</th>
                <th>Entrada</th>
                <th>Salida</th>
                <th>Vigencia</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {cargando ? (
                <EmptyRow columnas={6} mensaje="Cargando horarios…" />
              ) : visibles.length === 0 ? (
                <EmptyRow columnas={6} mensaje="No hay horarios registrados." />
              ) : (
                  visibles.map((h) => (
                    <tr key={h.id}>
                      <td>{h.nombre}</td>
                      <td>{h.sede}</td>
                      <td>{h.horaEntrada}</td>
                      <td>{h.horaSalida || "—"}</td>
                      <td>
                        {h.vigenteDesde}
                        {h.vigenteHasta ? ` – ${h.vigenteHasta}` : " – vigente"}
                      </td>
                      <td>
                        <div className="table__actions">
                          <button
                            type="button"
                            className="btn btn--icon"
                            aria-label={`Editar ${h.nombre}`}
                            onClick={() => setEditando(h)}
                          >
                            <EditIcon size={18} />
                          </button>
                          <button
                            type="button"
                            className="btn btn--icon"
                            aria-label={`Eliminar ${h.nombre}`}
                            onClick={() => setAEliminar(h)}
                          >
                            <TrashIcon size={18} />
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
          pagina={pagina}
          totalPaginas={totalPaginas}
          info={`${filtrados.length} horario${filtrados.length !== 1 ? "s" : ""}`}
          irA={irA}
        />
      </Card>

      <Modal
        abierto={editando !== null}
        titulo={editando?.id ? "Editar horario" : "Nuevo horario"}
        alCerrar={() => setEditando(null)}
        pie={
          <>
            <button
              type="button"
              className="btn btn--neutral"
              onClick={() => setEditando(null)}
            >
              Cancelar
            </button>
            <button type="button" className="btn btn--primary" onClick={guardar}>
              {editando?.id ? "Guardar cambios" : "Crear horario"}
            </button>
          </>
        }
      >
        {editando ? (
          <>
            <div className="modal__grid">
              <TextField
                etiqueta="Nombre del horario"
                valor={editando.nombre}
                alCambiar={(v) => setEditando({ ...editando, nombre: v })}
                placeholder="Ej: Turno mañana"
              />
              <SelectField
                etiqueta="Sede *"
                valor={editando.sede}
                alCambiar={(v) => setEditando({ ...editando, sede: v })}
                opciones={sedesActivas.map((s) => ({
                  valor: s.nombre,
                  etiqueta: s.nombre,
                }))}
              />
            </div>

            <div className="modal__grid">
              <TextField
                etiqueta="Hora de entrada *"
                tipo="time"
                valor={editando.horaEntrada}
                alCambiar={(v) => setEditando({ ...editando, horaEntrada: v })}
              />
              <TextField
                etiqueta="Hora de salida"
                tipo="time"
                valor={editando.horaSalida}
                alCambiar={(v) => setEditando({ ...editando, horaSalida: v })}
              />
            </div>

            <div className="modal__grid">
              <TextField
                etiqueta="Vigente desde *"
                tipo="date"
                valor={editando.vigenteDesde}
                alCambiar={(v) => setEditando({ ...editando, vigenteDesde: v })}
              />
              <TextField
                etiqueta="Vigente hasta (opcional)"
                tipo="date"
                valor={editando.vigenteHasta}
                alCambiar={(v) => setEditando({ ...editando, vigenteHasta: v })}
              />
            </div>
          </>
        ) : null}
      </Modal>

      <ConfirmDialog
        abierto={aEliminar !== null}
        titulo="Eliminar horario"
        mensaje={`Se eliminará el horario "${aEliminar?.nombre ?? ""}". Esta acción no se puede deshacer.`}
        alCerrar={() => setAEliminar(null)}
        alConfirmar={async () => {
          if (aEliminar) {
            try {
              await eliminarHorarioApi(Number(aEliminar.id));
              setHorarios((prev) => prev.filter((h) => h.id !== aEliminar.id));
              mostrar("Horario eliminado.");
            } catch (e) {
              mostrar(
                e instanceof Error ? e.message : "Error al eliminar el horario.",
                "error",
              );
            }
          }
          setAEliminar(null);
        }}
      />
    </>
  );
}
