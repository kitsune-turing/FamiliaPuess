import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Badge,
  Card,
  EmptyRow,
  Modal,
  Pagination,
  SearchInput,
  SelectField,
  StatCard,
  Switch,
  TextField,
} from "../../components/ui";
import {
  BriefcaseIcon,
  DownloadIcon,
  EditIcon,
  EyeIcon,
  MoreIcon,
  PlusIcon,
  UserCheckIcon,
  UsersIcon,
} from "../../components/ui/Icons";
import { useDatos } from "../../context/DataProvider";
import { useToast } from "../../context/ToastProvider";
import { useClickFuera, usePaginacion } from "../../hooks";
import { coincide, descargarExcel, porcentaje } from "../../lib/format";
import type { Trabajador } from "../../types/admin";

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
}: {
  trabajador: Trabajador;
  alVer: () => void;
  alEditar: () => void;
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
        </div>
      ) : null}
    </div>
  );
}

export function RegistroTrabajadoresPage() {
  const { trabajadores, itemsCatalogo, guardarTrabajador } =
    useDatos();
  const { mostrar } = useToast();
  const [parametros, setParametros] = useSearchParams();

  const [busqueda, setBusqueda] = useState("");
  const [editando, setEditando] = useState<Trabajador | null>(null);
  const [viendo, setViendo] = useState<Trabajador | null>(null);
  const [errores, setErrores] = useState<Record<string, string>>({});

  // Permite abrir el formulario desde las acciones rápidas del dashboard.
  useEffect(() => {
    if (parametros.get("nuevo")) {
      setEditando({ ...VACIO });
      parametros.delete("nuevo");
      setParametros(parametros, { replace: true });
    }
  }, [parametros, setParametros]);

  const filtrados = useMemo(
    () =>
      trabajadores
        .filter((trabajador) =>
          coincide(trabajador.nombre, busqueda) || coincide(trabajador.documento, busqueda),
        )
        .sort((a, b) => (a.activo === b.activo ? 0 : a.activo ? -1 : 1)),
    [trabajadores, busqueda],
  );

  const metricas = useMemo(() => {
    const activos = filtrados.filter((t) => t.activo).length;
    return {
      total: filtrados.length,
      activos,
      cargos: new Set(filtrados.map((t) => t.cargo)).size,
    };
  }, [filtrados]);

  const paginacion = usePaginacion(filtrados, POR_PAGINA);

  const validar = (valor: Trabajador): boolean => {
    const nuevos: Record<string, string> = {};
    if (!valor.nombre.trim()) nuevos.nombre = "El nombre es obligatorio.";
    if (!valor.documento.trim()) nuevos.documento = "El documento es obligatorio.";
    setErrores(nuevos);
    return Object.keys(nuevos).length === 0;
  };

  const guardar = async () => {
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
      "registro-de-trabajadores",
      ["Trabajador", "Documento", "Cargo", "Estado", "Ingreso"],
      filtrados.map((t) => [
        t.nombre,
        t.documento,
        t.cargo,
        t.activo ? "Activo" : "Inactivo",
        t.ingreso,
      ]),
    );
    mostrar("Registro exportado en Excel.");
  };

  // Los cargos se administran desde Catálogos › Cargos.
  const opcionesCargo = itemsCatalogo
    .filter((i) => i.catalogo === "cargos" && i.activo)
    .sort((a, b) => a.orden - b.orden)
    .map((i) => ({ valor: i.nombre, etiqueta: i.nombre }));

  return (
    <>
      {/* ------------------------------------------------------- Métricas -- */}
      <div className="stat-grid">
        <StatCard
          icono={<UsersIcon size={26} />}
          color="yellow"
          etiqueta="Total trabajadores"
          valor={metricas.total}
          pista="Registrados en el sistema"
        />
        <StatCard
          icono={<UserCheckIcon size={26} />}
          color="yellow"
          etiqueta="Trabajadores activos"
          valor={metricas.activos}
          pista={`${porcentaje(metricas.activos, metricas.total)} del total`}
        />
        <StatCard
          icono={<BriefcaseIcon size={26} />}
          color="pink"
          etiqueta="Cargos distintos"
          valor={metricas.cargos}
          pista="Tipos diferentes"
        />
      </div>

      {/* ------------------------------------------- Filtros y acciones -- */}
      <Card>
        <div className="filters">
          <SearchInput
            valor={busqueda}
            alCambiar={setBusqueda}
            placeholder="Buscar trabajador"
            etiquetaAccesible="Buscar trabajador por nombre o documento"
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

      {/* ---------------------------------------------------------- Tabla -- */}
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
                      : "No se encontraron trabajadores."
                  } />
              ) : (
                paginacion.visibles.map((trabajador) => (
                    <tr key={trabajador.id}>
                      <td>{trabajador.nombre}</td>
                      <td>{trabajador.documento}</td>
                      <td>{trabajador.cargo || "—"}</td>
                      <td>
                        <Badge tono={trabajador.activo ? "green" : "grey"}>{trabajador.activo ? "Activo" : "Inactivo"}</Badge>
                      </td>
                      <td>
                        <MenuFila
                          trabajador={trabajador}
                          alVer={() => setViendo(trabajador)}
                          alEditar={() => setEditando(trabajador)}
                        />
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
                etiqueta="Cargo"
                valor={editando.cargo}
                opciones={[{ valor: "", etiqueta: "Sin asignar" }, ...opcionesCargo]}
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
              <span className="setting-row__label">Cargo</span>
              <span>{viendo.cargo || "—"}</span>
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

    </>
  );
}
