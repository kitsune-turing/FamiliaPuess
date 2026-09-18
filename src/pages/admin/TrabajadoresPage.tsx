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
  Switch,
  TextField,
} from "../../components/ui";
import { DownloadIcon, EditIcon, PlusIcon, TrashIcon } from "../../components/ui/Icons";
import { useDatos } from "../../context/DataProvider";
import { useToast } from "../../context/ToastProvider";
import { usePaginacion } from "../../hooks";
import { coincide, descargarExcel } from "../../lib/format";
import type { Trabajador } from "../../types/admin";

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
  const { trabajadores, guardarTrabajador, eliminarTrabajador } = useDatos();
  const { mostrar } = useToast();
  const [parametros, setParametros] = useSearchParams();

  const [busqueda, setBusqueda] = useState("");
  const [editando, setEditando] = useState<Trabajador | null>(null);
  const [aEliminar, setAEliminar] = useState<Trabajador | null>(null);
  const [errores, setErrores] = useState<Record<string, string>>({});

  useEffect(() => {
    if (parametros.get("nuevo")) {
      setEditando({ ...VACIO });
      parametros.delete("nuevo");
      setParametros(parametros, { replace: true });
    }
  }, [parametros, setParametros]);

  const filtrados = useMemo(
    () =>
      trabajadores.filter((trabajador) =>
        coincide(trabajador.nombre, busqueda) ||
        coincide(trabajador.documento, busqueda) ||
        coincide(trabajador.cargo, busqueda),
      ),
    [trabajadores, busqueda],
  );

  const paginacion = usePaginacion(filtrados, POR_PAGINA);

  const validar = (valor: Trabajador): boolean => {
    const nuevos: Record<string, string> = {};
    if (!valor.nombre.trim()) nuevos.nombre = "El nombre es obligatorio.";
    if (!valor.documento.trim()) nuevos.documento = "El documento es obligatorio.";
    setErrores(nuevos);
    return Object.keys(nuevos).length === 0;
  };

  const confirmarGuardado = async () => {
    if (!editando || !validar(editando)) return;
    const esNuevo = !editando.id;
    try {
      await guardarTrabajador({
        ...editando,
        id: editando.id || `trab-${Date.now()}`,
        ingreso: editando.ingreso || new Date().toLocaleDateString("es-CO"),
      });
      setEditando(null);
      setErrores({});
      mostrar(esNuevo ? "Trabajador registrado." : "Trabajador actualizado.");
    } catch (e) {
      mostrar(e instanceof Error ? e.message : "Error al guardar el trabajador.", "error");
    }
  };

  const exportar = () => {
    descargarExcel(
      "trabajadores",
      ["Trabajador", "Documento", "Cargo", "Estado"],
      filtrados.map((t) => [
        t.nombre,
        t.documento,
        t.cargo,
        t.activo ? "Activo" : "Inactivo",
      ]),
    );
    mostrar("Listado exportado en Excel.");
  };

  return (
    <>
      {/* --------------------------------------------- Filtros y acciones */}
      <Card>
        <div className="filters">
          <SearchInput
            valor={busqueda}
            alCambiar={setBusqueda}
            placeholder="Buscar trabajador"
            etiquetaAccesible="Buscar trabajador por nombre, documento o cargo"
          />
          <div className="filters__actions">
            <button type="button" className="btn btn--ghost" onClick={exportar}>
              <DownloadIcon size={20} /> Exportar
            </button>
            <button
              type="button"
              className="btn btn--primary"
              onClick={() => setEditando({ ...VACIO })}
            >
              <PlusIcon size={20} /> Nuevo trabajador
            </button>
          </div>
        </div>
      </Card>

      {/* -------------------------------------------------------- Tabla -- */}
      <Card>
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Trabajador</th>
                <th>Documento</th>
                <th>Cargo</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {paginacion.visibles.length === 0 ? (
                <EmptyRow columnas={5} mensaje={
                    trabajadores.length === 0
                      ? "Aún no hay trabajadores registrados."
                      : "No hay trabajadores que coincidan con la búsqueda."
                  } />
              ) : (
                paginacion.visibles.map((trabajador) => (
                  <tr key={trabajador.id}>
                    <td>{trabajador.nombre}</td>
                    <td>{trabajador.documento}</td>
                    <td>{trabajador.cargo}</td>
                    <td>
                      <BadgeOutline tono={trabajador.activo ? "neutral" : "pink"}>
                        {trabajador.activo ? "Activo" : "Inactivo"}
                      </BadgeOutline>
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

        <Pagination
          pagina={paginacion.pagina}
          totalPaginas={paginacion.totalPaginas}
          info={`Mostrando ${paginacion.desde} a ${paginacion.hasta} de ${paginacion.total} registros`}
          irA={paginacion.irA}
        />
      </Card>

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
              <TextField
                etiqueta="Cargo"
                valor={editando.cargo}
                alCambiar={(v) => setEditando({ ...editando, cargo: v })}
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

      <ConfirmDialog
        abierto={aEliminar !== null}
        titulo="Eliminar trabajador"
        mensaje={`Se eliminará a ${aEliminar?.nombre ?? ""} del sistema. Sus registros históricos de asistencia se conservan.`}
        alCerrar={() => setAEliminar(null)}
        alConfirmar={async () => {
          if (aEliminar) {
            try {
              await eliminarTrabajador(aEliminar.id);
              mostrar("Trabajador eliminado.");
            } catch (e) {
              mostrar(e instanceof Error ? e.message : "Error al eliminar el trabajador.", "error");
            }
          }
          setAEliminar(null);
        }}
      />
    </>
  );
}
