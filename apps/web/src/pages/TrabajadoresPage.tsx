import { useEffect, useMemo, useState } from "react";
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
} from "../components/ui";
import { EditIcon, TrashIcon, UploadIcon } from "../components/ui/Icons";
import { useAuth } from "../contexts/AuthContext";
import { useDatos } from "../context/DataProvider";
import { useToast } from "../context/ToastProvider";
import { usePaginacion } from "../hooks";
import { coincide, descargarArchivo, generarCsv } from "../lib/format";
import type { Trabajador } from "../types/admin";

const POR_PAGINA = 10;

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

export function TrabajadoresPage() {
  const { trabajadores, sedes, guardarTrabajador, eliminarTrabajador } = useDatos();
  const { sedeActiva } = useAuth();
  const { mostrar } = useToast();
  const [parametros, setParametros] = useSearchParams();

  const [busqueda, setBusqueda] = useState("");
  const [editando, setEditando] = useState<Trabajador | null>(null);
  const [aEliminar, setAEliminar] = useState<Trabajador | null>(null);
  const [importando, setImportando] = useState(false);
  const [errores, setErrores] = useState<Record<string, string>>({});

  // Permite abrir los diálogos desde las acciones rápidas del dashboard.
  useEffect(() => {
    if (parametros.get("nuevo")) {
      setEditando({ ...VACIO, sede: sedes[0]?.nombre ?? "" });
      parametros.delete("nuevo");
      setParametros(parametros, { replace: true });
    }
    if (parametros.get("importar")) {
      setImportando(true);
      parametros.delete("importar");
      setParametros(parametros, { replace: true });
    }
  }, [parametros, setParametros, sedes]);

  const filtrados = useMemo(
    () =>
      trabajadores.filter((trabajador) => {
        const porSede = sedeActiva === "Todas las sedes" || trabajador.sede === sedeActiva;
        const porTexto =
          coincide(trabajador.nombre, busqueda) ||
          coincide(trabajador.documento, busqueda) ||
          coincide(trabajador.cargo, busqueda) ||
          coincide(trabajador.sede, busqueda);
        return porSede && porTexto;
      }),
    [trabajadores, busqueda, sedeActiva],
  );

  const paginacion = usePaginacion(filtrados, POR_PAGINA);

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

  const confirmarGuardado = () => {
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
      ["Trabajador", "Documento", "Sede", "Cargo", "Correo", "Teléfono", "Estado"],
      filtrados.map((t) => [
        t.nombre,
        t.documento,
        t.sede,
        t.cargo,
        t.correo,
        t.telefono,
        t.activo ? "Activo" : "Inactivo",
      ]),
    );
    descargarArchivo("trabajadores.csv", csv);
    mostrar("Listado exportado en CSV.");
  };

  const opcionesSede = sedes.map((sede) => ({ valor: sede.nombre, etiqueta: sede.nombre }));

  return (
    <>
      {/* --------------------------------------------- Búsqueda y acciones */}
      <Card className="card--pad" pad={false}>
        <div
          style={{
            display: "flex",
            gap: 18,
            alignItems: "center",
            flexWrap: "wrap",
            padding: 24,
            border: "1.5px solid var(--fp-brown)",
            borderRadius: "var(--fp-r-lg)",
          }}
        >
          <SearchInput
            valor={busqueda}
            alCambiar={setBusqueda}
            placeholder="Buscar trabajador"
            etiquetaAccesible="Buscar trabajador por nombre, documento o cargo"
          />
          <button type="button" className="btn btn--primary" onClick={() => setImportando(true)}>
            <UploadIcon size={20} /> Importar
          </button>
          <button
            type="button"
            className="btn btn--primary"
            onClick={() => setEditando({ ...VACIO, sede: sedeActiva !== "Todas las sedes" ? sedeActiva : (sedes[0]?.nombre ?? "") })}
          >
            <UploadIcon size={20} /> Nuevo trabajador
          </button>
        </div>
      </Card>

      {/* ------------------------------------------------------ Listado -- */}
      <Card>
        <div className="table-wrap">
          <table className="table">
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
              {paginacion.visibles.length === 0 ? (
                <EmptyRow columnas={7} mensaje={
                    trabajadores.length === 0
                      ? "Aún no hay trabajadores registrados."
                      : "No hay trabajadores que coincidan con la búsqueda."
                  } />
              ) : (
                paginacion.visibles.map((trabajador) => (
                  <tr key={trabajador.id}>
                    <td>{trabajador.nombre}</td>
                    <td>{trabajador.documento}</td>
                    <td>{trabajador.sede}</td>
                    <td>08:02 a.m</td>
                    <td>
                      <BadgeOutline tono={trabajador.activo ? "neutral" : "pink"}>
                        {trabajador.activo ? "A tiempo" : "Inactivo"}
                      </BadgeOutline>
                    </td>
                    <td>
                      <span className="cell-device">
                        <span className="dot" />
                        PV-01
                      </span>
                    </td>
                    <td>
                      <div className="table__actions">
                        <button
                          type="button"
                          className="btn btn--icon"
                          aria-label={`Editar ${trabajador.nombre}`}
                          onClick={() => setEditando(trabajador)}
                        >
                          <EditIcon size={19} />
                        </button>
                        <button
                          type="button"
                          className="btn btn--icon"
                          aria-label={`Eliminar ${trabajador.nombre}`}
                          onClick={() => setAEliminar(trabajador)}
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
      </Card>

      <Pagination
        pagina={paginacion.pagina}
        totalPaginas={paginacion.totalPaginas}
        info={`Mostrando ${paginacion.desde} a ${paginacion.hasta} de ${paginacion.total} registros`}
        irA={paginacion.irA}
      />

      {/* ------------------------------------------------------- Modales - */}
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
            <button type="button" className="btn btn--primary" onClick={confirmarGuardado}>
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
                opciones={opcionesSede}
                alCambiar={(v) => setEditando({ ...editando, sede: v })}
              />
              <TextField
                etiqueta="Cargo"
                valor={editando.cargo}
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
        abierto={importando}
        titulo="Importar trabajadores"
        subtitulo="Carga un archivo CSV con las columnas: nombre, documento, sede, cargo, correo."
        alCerrar={() => setImportando(false)}
        pie={
          <>
            <button type="button" className="btn btn--neutral" onClick={() => setImportando(false)}>
              Cancelar
            </button>
            <button type="button" className="btn btn--primary" onClick={exportar}>
              Descargar plantilla
            </button>
          </>
        }
      >
        <input
          type="file"
          accept=".csv"
          className="input"
          style={{ paddingTop: 11 }}
          aria-label="Archivo CSV"
          onChange={(e) => {
            const archivo = e.target.files?.[0];
            if (archivo) {
              mostrar(`Archivo "${archivo.name}" listo para procesar.`, "info");
              setImportando(false);
            }
          }}
        />
        <p style={{ fontSize: 13.5, color: "var(--fp-text-muted)", lineHeight: 1.6 }}>
          Los registros duplicados por documento se actualizan en lugar de crearse de nuevo.
        </p>
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
