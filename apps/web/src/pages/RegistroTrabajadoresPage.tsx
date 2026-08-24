import { useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Badge,
  Card,
  ConfirmDialog,
  EmptyRow,
  Modal,
  Pagination,
  SelectField,
  StatCard,
  Switch,
  TextField,
} from "../components/ui";
import {
  BriefcaseIcon,
  EditIcon,
  EyeIcon,
  MapPinIcon,
  MoreIcon,
  PlusIcon,
  TrashIcon,
  UploadIcon,
  UserCheckIcon,
  UsersIcon,
} from "../components/ui/Icons";
import { useAuth } from "../contexts/AuthContext";
import { useDatos } from "../context/DataProvider";
import { useToast } from "../context/ToastProvider";
import { useClickFuera, usePaginacion } from "../hooks";
import { coincide, descargarArchivo, generarCsv, porcentaje } from "../lib/format";
import type { Trabajador } from "../types/admin";

const POR_PAGINA = 6;

const VACIO: Trabajador = {
  id: "",
  nombre: "",
  documento: "",
  sede: "",
  cargo: "",
  correo: "",
  telefono: "",
  codigoAlfa: "",
  activo: true,
  ingreso: "",
};

/** Menú "…" con las acciones de cada fila. */
function MenuFila({
  trabajador,
  alVer,
  alEditar,
  alEliminar,
}: {
  trabajador: Trabajador;
  alVer: () => void;
  alEditar: () => void;
  alEliminar: () => void;
}) {
  const [abierto, setAbierto] = useState(false);
  const ref = useClickFuera<HTMLDivElement>(abierto, () => setAbierto(false));

  return (
    <div style={{ position: "relative" }} ref={ref}>
      <button
        type="button"
        className="btn btn--icon"
        aria-label={`Acciones para ${trabajador.nombre}`}
        aria-expanded={abierto}
        aria-haspopup="menu"
        onClick={() => setAbierto((v) => !v)}
      >
        <MoreIcon size={20} />
      </button>

      {abierto ? (
        <div className="dropdown" role="menu" style={{ minWidth: 180 }}>
          <button
            type="button"
            role="menuitem"
            className="dropdown__item"
            onClick={() => {
              setAbierto(false);
              alVer();
            }}
          >
            <EyeIcon size={18} /> Ver detalle
          </button>
          <button
            type="button"
            role="menuitem"
            className="dropdown__item"
            onClick={() => {
              setAbierto(false);
              alEditar();
            }}
          >
            <EditIcon size={18} /> Editar
          </button>
          <div className="dropdown__divider" />
          <button
            type="button"
            role="menuitem"
            className="dropdown__item dropdown__item--danger"
            onClick={() => {
              setAbierto(false);
              alEliminar();
            }}
          >
            <TrashIcon size={18} /> Eliminar
          </button>
        </div>
      ) : null}
    </div>
  );
}

export function RegistroTrabajadoresPage() {
  const { trabajadores, sedes, registros, itemsCatalogo, guardarTrabajador, eliminarTrabajador } =
    useDatos();
  const { sedeActiva } = useAuth();
  const { mostrar } = useToast();
  const [parametros, setParametros] = useSearchParams();
  const inputArchivo = useRef<HTMLInputElement | null>(null);

  const [busqueda] = useState("");
  const [editando, setEditando] = useState<Trabajador | null>(null);
  const [viendo, setViendo] = useState<Trabajador | null>(null);
  const [aEliminar, setAEliminar] = useState<Trabajador | null>(null);
  const [errores, setErrores] = useState<Record<string, string>>({});

  // Permite abrir el formulario desde las acciones rápidas del dashboard.
  useEffect(() => {
    if (parametros.get("nuevo")) {
      setEditando({ ...VACIO, sede: sedes[0]?.nombre ?? "" });
      parametros.delete("nuevo");
      setParametros(parametros, { replace: true });
    }
    if (parametros.get("importar")) {
      inputArchivo.current?.click();
      parametros.delete("importar");
      setParametros(parametros, { replace: true });
    }
  }, [parametros, setParametros, sedes]);

  const filtrados = useMemo(
    () =>
      trabajadores.filter((trabajador) => {
        const porSede = sedeActiva === "Todas las sedes" || trabajador.sede === sedeActiva;
        const porTexto =
          coincide(trabajador.nombre, busqueda) || coincide(trabajador.documento, busqueda);
        return porSede && porTexto;
      }),
    [trabajadores, sedeActiva, busqueda],
  );

  const metricas = useMemo(() => {
    const activos = filtrados.filter((t) => t.activo).length;
    return {
      total: filtrados.length,
      activos,
      sedes: new Set(filtrados.map((t) => t.sede)).size,
      cargos: new Set(filtrados.map((t) => t.cargo)).size,
    };
  }, [filtrados]);

  const paginacion = usePaginacion(filtrados, POR_PAGINA);

  /** Último registro de asistencia del trabajador, para la columna de estado. */
  const ultimoRegistro = (nombre: string) => registros.find((r) => r.trabajador === nombre);

  const validar = (valor: Trabajador): boolean => {
    const nuevos: Record<string, string> = {};
    if (!valor.nombre.trim()) nuevos.nombre = "El nombre es obligatorio.";
    if (!valor.documento.trim()) nuevos.documento = "El documento es obligatorio.";
    if (valor.correo && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(valor.correo)) {
      nuevos.correo = "Escribe un correo válido.";
    }
    setErrores(nuevos);
    return Object.keys(nuevos).length === 0;
  };

  const guardar = () => {
    if (!editando || !validar(editando)) return;
    const esNuevo = !editando.id;
    guardarTrabajador({
      ...editando,
      id: editando.id || `trab-${Date.now()}`,
      ingreso: editando.ingreso || new Date().toLocaleDateString("es-CO"),
    });
    setEditando(null);
    setErrores({});
    mostrar(esNuevo ? "Trabajador registrado." : "Trabajador actualizado.");
  };

  const exportar = () => {
    const csv = generarCsv(
      ["Trabajador", "Documento", "Sede", "Cargo", "Correo", "Teléfono", "Estado", "Ingreso"],
      filtrados.map((t) => [
        t.nombre,
        t.documento,
        t.sede,
        t.cargo,
        t.correo,
        t.telefono,
        t.activo ? "Activo" : "Inactivo",
        t.ingreso,
      ]),
    );
    descargarArchivo("registro-de-trabajadores.csv", csv);
    mostrar("Registro exportado en CSV.");
  };

  // Los cargos se administran desde Catálogos › Cargos.
  const opcionesCargo = itemsCatalogo
    .filter((i) => i.catalogo === "cargos" && i.activo)
    .sort((a, b) => a.orden - b.orden)
    .map((i) => ({ valor: i.nombre, etiqueta: i.nombre }));

  return (
    <>
      {/* ------------------------------------------------ Acciones de página */}
      <div className="page-actions">
        <input
          ref={inputArchivo}
          type="file"
          accept=".csv"
          className="sr-only"
          aria-label="Archivo CSV de trabajadores"
          onChange={(e) => {
            const archivo = e.target.files?.[0];
            if (archivo) mostrar(`Archivo "${archivo.name}" listo para procesar.`, "info");
            e.target.value = "";
          }}
        />
        <button type="button" className="btn btn--neutral" onClick={() => inputArchivo.current?.click()}>
          <UploadIcon size={20} /> Importar
        </button>
        <button
          type="button"
          className="btn btn--primary"
          onClick={() =>
            setEditando({
              ...VACIO,
              sede: sedeActiva !== "Todas las sedes" ? sedeActiva : (sedes[0]?.nombre ?? ""),
            })
          }
        >
          <PlusIcon size={20} /> Nuevo trabajador
        </button>
      </div>

      {/* ------------------------------------------------------- Métricas -- */}
      <div className="stat-grid">
        <StatCard
          icono={<UsersIcon size={26} />}
          color="yellow"
          etiqueta="Total trabajadores"
          valor={metricas.total}
          pista="En la sede seleccionada"
        />
        <StatCard
          icono={<UserCheckIcon size={26} />}
          color="yellow"
          etiqueta="Trabajadores activos"
          valor={metricas.activos}
          pista={`${porcentaje(metricas.activos, metricas.total)} del total`}
        />
        <StatCard
          icono={<MapPinIcon size={26} />}
          color="pink"
          etiqueta="Sedes cubiertas"
          valor={metricas.sedes}
          pista="Con personal asignado"
        />
        <StatCard
          icono={<BriefcaseIcon size={26} />}
          color="pink"
          etiqueta="Cargos distintos"
          valor={metricas.cargos}
          pista="Tipos diferentes"
        />
      </div>

      <div className="page-actions">
        <button type="button" className="btn btn--primary" onClick={exportar}>
          <UploadIcon size={20} /> Exportar
        </button>
      </div>

      {/* ---------------------------------------------------------- Tabla -- */}
      <Card>
        <h2 className="card__title" style={{ marginBottom: 18 }}>
          Historial de actividades
        </h2>

        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Trabajador</th>
                <th>Documento</th>
                <th>Sede</th>
                <th>Hora de entrada</th>
                <th>Estado</th>
                <th>Dispositivo</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {paginacion.visibles.length === 0 ? (
                <EmptyRow columnas={7} mensaje={
                    trabajadores.length === 0
                      ? "Aún no hay trabajadores registrados."
                      : "No hay trabajadores en la sede seleccionada."
                  } />
              ) : (
                paginacion.visibles.map((trabajador) => {
                  const registro = ultimoRegistro(trabajador.nombre);
                  const tarde = registro?.estado === "tarde";
                  return (
                    <tr key={trabajador.id}>
                      <td>{trabajador.nombre}</td>
                      <td>{trabajador.documento}</td>
                      <td>{trabajador.sede}</td>
                      <td>{registro?.entrada ?? "—"}</td>
                      <td>
                        <Badge tono={tarde ? "orange" : "green"}>{tarde ? "Tarde" : "A tiempo"}</Badge>
                      </td>
                      <td>{registro?.dispositivo ?? "—"}</td>
                      <td>
                        <MenuFila
                          trabajador={trabajador}
                          alVer={() => setViendo(trabajador)}
                          alEditar={() => setEditando(trabajador)}
                          alEliminar={() => setAEliminar(trabajador)}
                        />
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        <Pagination
          pagina={paginacion.pagina}
          totalPaginas={paginacion.totalPaginas}
          info={`Mostrando ${paginacion.desde} a ${paginacion.hasta} de ${paginacion.total} registros`}
          irA={paginacion.irA}
        />
      </Card>

      {/* -------------------------------------------------------- Modales -- */}
      <Modal
        abierto={editando !== null}
        titulo={editando?.id ? "Editar trabajador" : "Nuevo trabajador"}
        subtitulo="Los datos se usan para validar el registro de asistencia."
        ancho="ancho"
        alCerrar={() => {
          setEditando(null);
          setErrores({});
        }}
        pie={
          <>
            <button
              type="button"
              className="btn btn--neutral"
              onClick={() => {
                setEditando(null);
                setErrores({});
              }}
            >
              Cancelar
            </button>
            <button type="button" className="btn btn--primary" onClick={guardar}>
              Guardar trabajador
            </button>
          </>
        }
      >
        {editando ? (
          <>
            <div className="modal__grid">
              <TextField
                etiqueta="Nombre completo"
                requerido
                valor={editando.nombre}
                error={errores.nombre}
                alCambiar={(v) => setEditando({ ...editando, nombre: v })}
              />
              <TextField
                etiqueta="Documento"
                requerido
                placeholder="CC 1.234.567"
                valor={editando.documento}
                error={errores.documento}
                alCambiar={(v) => setEditando({ ...editando, documento: v })}
              />
              <SelectField
                etiqueta="Sede"
                valor={editando.sede}
                opciones={sedes.map((s) => ({ valor: s.nombre, etiqueta: s.nombre }))}
                alCambiar={(v) => setEditando({ ...editando, sede: v })}
              />
              <SelectField
                etiqueta="Cargo"
                valor={editando.cargo}
                opciones={[{ valor: "", etiqueta: "Sin asignar" }, ...opcionesCargo]}
                alCambiar={(v) => setEditando({ ...editando, cargo: v })}
              />
              <TextField
                etiqueta="Correo electrónico"
                tipo="email"
                valor={editando.correo}
                error={errores.correo}
                alCambiar={(v) => setEditando({ ...editando, correo: v })}
              />
              <TextField
                etiqueta="Teléfono"
                valor={editando.telefono}
                alCambiar={(v) => setEditando({ ...editando, telefono: v })}
              />
              <TextField
                etiqueta="Código alfanumérico"
                placeholder="ABCD"
                valor={editando.codigoAlfa}
                alCambiar={(v) => setEditando({ ...editando, codigoAlfa: v.toUpperCase().slice(0, 6) })}
              />
            </div>
            <div className="setting-row">
              <div>
                <p className="setting-row__label">Trabajador activo</p>
                <p className="setting-row__hint">
                  Si se desactiva, el trabajador no podrá registrar asistencia desde los dispositivos.
                </p>
              </div>
              <Switch
                marcado={editando.activo}
                etiqueta="Trabajador activo"
                alCambiar={(v) => setEditando({ ...editando, activo: v })}
              />
            </div>
          </>
        ) : null}
      </Modal>

      <Modal
        abierto={viendo !== null}
        titulo={viendo?.nombre ?? ""}
        subtitulo={viendo?.cargo || "Sin cargo asignado"}
        alCerrar={() => setViendo(null)}
        pie={
          <button type="button" className="btn btn--neutral" onClick={() => setViendo(null)}>
            Cerrar
          </button>
        }
      >
        {viendo ? (
          <>
            <div className="setting-row">
              <span className="setting-row__label">Documento</span>
              <span>{viendo.documento}</span>
            </div>
            <div className="setting-row">
              <span className="setting-row__label">Sede</span>
              <span>{viendo.sede}</span>
            </div>
            <div className="setting-row">
              <span className="setting-row__label">Correo</span>
              <span>{viendo.correo || "—"}</span>
            </div>
            <div className="setting-row">
              <span className="setting-row__label">Teléfono</span>
              <span>{viendo.telefono || "—"}</span>
            </div>
            <div className="setting-row">
              <span className="setting-row__label">Código alfanumérico</span>
              <span style={{ fontFamily: "ui-monospace, monospace" }}>{viendo.codigoAlfa || "—"}</span>
            </div>
            <div className="setting-row">
              <span className="setting-row__label">Fecha de ingreso</span>
              <span>{viendo.ingreso || "—"}</span>
            </div>
            <div className="setting-row">
              <span className="setting-row__label">Estado</span>
              <Badge tono={viendo.activo ? "green" : "grey"}>{viendo.activo ? "Activo" : "Inactivo"}</Badge>
            </div>
          </>
        ) : null}
      </Modal>

      <ConfirmDialog
        abierto={aEliminar !== null}
        titulo="Eliminar trabajador"
        mensaje={`Se eliminará a ${aEliminar?.nombre ?? ""} del sistema. Sus registros históricos de asistencia se conservan.`}
        alCerrar={() => setAEliminar(null)}
        alConfirmar={() => {
          if (aEliminar) {
            eliminarTrabajador(aEliminar.id);
            mostrar("Trabajador eliminado.");
          }
          setAEliminar(null);
        }}
      />
    </>
  );
}
