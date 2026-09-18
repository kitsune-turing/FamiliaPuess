/* ==========================================================================
   Roles y permisos.

   Administra los roles del sistema y define, módulo por módulo, qué puede
   hacer cada uno. Los roles viven en `DataProvider`, de modo que la pantalla
   de Usuarios y la matriz de Seguridad siempre ven la misma información.
   ========================================================================== */

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
  StatCard,
  Switch,
  TextAreaField,
  TextField,
} from "../../components/ui";
import {
  CopyIcon,
  EditIcon,
  EyeIcon,
  KeyIcon,
  PlusIcon,
  ShieldCheckIcon,
  ShieldOffIcon,
  TrashIcon,
  UserShieldIcon,
} from "../../components/ui/Icons";
import { useAuth } from "../../context/AuthProvider";
import { useDatos } from "../../context/DataProvider";
import { useToast } from "../../context/ToastProvider";
import {
  ACCIONES_PERMISO,
  MODULOS_PERMISOS,
  clavePermiso,
  todosLosPermisos,
} from "../../data/initial";
import { usePaginacion } from "../../hooks";
import { fechaHoraActual, coincide, porcentaje } from "../../lib/format";
import type { AccionPermiso, Rol, TonoRol } from "../../types/admin";

const POR_PAGINA = 5;

const TONOS: { valor: TonoRol; etiqueta: string }[] = [
  { valor: "pink", etiqueta: "Rosa" },
  { valor: "orange", etiqueta: "Naranja" },
  { valor: "purple", etiqueta: "Morado" },
  { valor: "green", etiqueta: "Verde" },
  { valor: "yellow", etiqueta: "Amarillo" },
  { valor: "grey", etiqueta: "Gris" },
];

const VACIO: Rol = {
  id: "",
  codigo: "",
  nombre: "",
  descripcion: "",
  permisos: [],
  activo: true,
  sistema: false,
  tono: "purple",
};

/** Convierte "Coordinador de sede" en "COORDINADOR_DE_SEDE". */
function aCodigo(nombre: string): string {
  return nombre
    .trim()
    .toUpperCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^A-Z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
}

export function RolesPage() {
  const { roles, usuarios, guardarRol, eliminarRol, registrarAuditoria } = useDatos();
  const { usuario } = useAuth();
  const { mostrar } = useToast();

  const [busqueda, setBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("todos");
  const [editando, setEditando] = useState<Rol | null>(null);
  const [aEliminar, setAEliminar] = useState<Rol | null>(null);
  const [expandido, setExpandido] = useState<string | null>(null);

  /** Cuántos usuarios tiene asignado cada rol. */
  const conteoUsuarios = useMemo(() => {
    const conteo: Record<string, number> = {};
    for (const u of usuarios) conteo[u.rol] = (conteo[u.rol] ?? 0) + 1;
    return conteo;
  }, [usuarios]);

  const metricas = useMemo(() => {
    const total = roles.length;
    const activos = roles.filter((r) => r.activo).length;
    const permisos = roles.reduce((suma, rol) => suma + rol.permisos.length, 0);
    return { total, activos, inactivos: total - activos, permisos };
  }, [roles]);

  const filtrados = useMemo(
    () =>
      roles.filter((rol) => {
        const porTexto =
          coincide(rol.nombre, busqueda) ||
          coincide(rol.codigo, busqueda) ||
          coincide(rol.descripcion, busqueda);
        const porEstado =
          filtroEstado === "todos" || (filtroEstado === "activo" ? rol.activo : !rol.activo);
        return porTexto && porEstado;
      }),
    [roles, busqueda, filtroEstado],
  );

  const paginacion = usePaginacion(filtrados, POR_PAGINA);

  const auditar = (accion: "Crear" | "Actualizar" | "Eliminar", detalle: string) => {
    registrarAuditoria({
      id: `aud-${Date.now()}`,
      fechaHora: fechaHoraActual(),
      usuario: usuario?.nombre ?? "Sistema",
      modulo: "Roles",
      accion,
      detalle,
      ip: "—",
      dispositivo: "Panel web",
    });
  };

  /* ------------------------------------------------- Permisos del modal - */

  const tienePermiso = (modulo: string, accion: AccionPermiso) =>
    editando?.permisos.includes(clavePermiso(modulo, accion)) ?? false;

  const alternarPermiso = (modulo: string, accion: AccionPermiso) => {
    if (!editando) return;
    const clave = clavePermiso(modulo, accion);
    const tiene = editando.permisos.includes(clave);

    let permisos = tiene
      ? editando.permisos.filter((p) => p !== clave)
      : [...editando.permisos, clave];

    // Crear, editar o eliminar no tienen sentido sin poder ver el módulo.
    if (!tiene && accion !== "ver") {
      const ver = clavePermiso(modulo, "ver");
      if (!permisos.includes(ver)) permisos = [...permisos, ver];
    }
    if (tiene && accion === "ver") {
      permisos = permisos.filter((p) => !p.startsWith(`${modulo}:`));
    }

    setEditando({ ...editando, permisos });
  };

  const alternarModulo = (modulo: string) => {
    if (!editando) return;
    const completo = ACCIONES_PERMISO.every((a) =>
      editando.permisos.includes(clavePermiso(modulo, a.valor)),
    );
    const sinModulo = editando.permisos.filter((p) => !p.startsWith(`${modulo}:`));
    setEditando({
      ...editando,
      permisos: completo
        ? sinModulo
        : [...sinModulo, ...ACCIONES_PERMISO.map((a) => clavePermiso(modulo, a.valor))],
    });
  };

  /* ---------------------------------------------------------- Acciones -- */

  const nuevoRol = () => setEditando({ ...VACIO, id: "" });

  const duplicar = (rol: Rol) => {
    setEditando({
      ...rol,
      id: "",
      sistema: false,
      nombre: `${rol.nombre} (copia)`,
      codigo: `${rol.codigo}_COPIA`,
    });
  };

  const guardar = () => {
    if (!editando) return;

    const nombre = editando.nombre.trim();
    if (!nombre) {
      mostrar("El nombre del rol es obligatorio.", "error");
      return;
    }

    const codigo = editando.codigo.trim() || aCodigo(nombre);
    const repetido = roles.some(
      (r) => r.id !== editando.id && r.codigo.toUpperCase() === codigo.toUpperCase(),
    );
    if (repetido) {
      mostrar("Ya existe un rol con ese código.", "error");
      return;
    }
    if (editando.permisos.length === 0) {
      mostrar("Asigna al menos un permiso al rol.", "error");
      return;
    }

    const esNuevo = !editando.id;
    guardarRol({
      ...editando,
      nombre,
      codigo,
      descripcion: editando.descripcion.trim(),
      id: editando.id || `rol-${Date.now()}`,
    });
    auditar(esNuevo ? "Crear" : "Actualizar", `${esNuevo ? "Creó" : "Actualizó"} el rol "${nombre}"`);
    setEditando(null);
    mostrar(esNuevo ? "Rol creado." : "Rol actualizado.");
  };

  const confirmarEliminar = async () => {
    if (!aEliminar) return;
    try {
      await eliminarRol(aEliminar.id);
      auditar("Eliminar", `Eliminó el rol "${aEliminar.nombre}"`);
      mostrar("Rol eliminado.");
    } catch (e) {
      mostrar(e instanceof Error ? e.message : "Error al eliminar el rol.", "error");
    }
    setAEliminar(null);
  };

  const pedirEliminar = (rol: Rol) => {
    if (rol.sistema) {
      mostrar("Los roles del sistema no se pueden eliminar.", "error");
      return;
    }
    if ((conteoUsuarios[rol.codigo] ?? 0) > 0) {
      mostrar("Reasigna primero los usuarios que tienen este rol.", "error");
      return;
    }
    setAEliminar(rol);
  };

  const permisosDelModal = editando?.permisos.length ?? 0;
  const totalPermisos = todosLosPermisos().length;

  return (
    <>
      {/* ------------------------------------------------------ Métricas - */}
      <div className="stat-grid">
        <StatCard
          icono={<UserShieldIcon size={26} />}
          color="pink"
          etiqueta="Total roles"
          valor={metricas.total}
          pista="En total"
        />
        <StatCard
          icono={<ShieldCheckIcon size={26} />}
          color="yellow"
          etiqueta="Roles activos"
          valor={metricas.activos}
          pista={`${porcentaje(metricas.activos, metricas.total)} del total`}
        />
        <StatCard
          icono={<ShieldOffIcon size={26} />}
          color="pink"
          etiqueta="Roles inactivos"
          valor={metricas.inactivos}
          pista={`${porcentaje(metricas.inactivos, metricas.total)} del total`}
        />
        <StatCard
          icono={<KeyIcon size={26} />}
          color="yellow"
          etiqueta="Permisos asignados"
          valor={metricas.permisos}
          pista="En total"
        />
      </div>

      {/* ----------------------------------------- Filtros y acciones -- */}
      <Card>
        <div className="filters">
          <SearchInput valor={busqueda} alCambiar={setBusqueda} placeholder="Buscar rol" etiquetaAccesible="Buscar rol por nombre o código" />
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
          <div className="filters__actions">
            <button type="button" className="btn btn--primary" onClick={nuevoRol}>
              <PlusIcon size={20} /> Nuevo rol
            </button>
          </div>
        </div>
      </Card>

      {/* -------------------------------------------- Listado de roles --- */}
      <Card>
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Rol</th>
                <th>Usuarios</th>
                <th>Permisos</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {paginacion.visibles.length === 0 ? (
                <EmptyRow
                  columnas={5}
                  mensaje={
                    roles.length === 0
                      ? "Aún no hay roles registrados."
                      : "No hay roles que coincidan con la búsqueda."
                  }
                />
              ) : (
                paginacion.visibles.flatMap((rol) => {
                  const estaExpandido = expandido === rol.id;
                  const permisosPorModulo = MODULOS_PERMISOS.map((modulo) => {
                    const acciones = ACCIONES_PERMISO
                      .filter((a) => rol.permisos.includes(clavePermiso(modulo, a.valor)))
                      .map((a) => a.etiqueta);
                    return { modulo, acciones };
                  }).filter((p) => p.acciones.length > 0);

                  return [
                    <tr key={rol.id}>
                      <td>
                        <div className="role-cell">
                          <Badge tono={rol.tono}>{rol.nombre}</Badge>
                          <span className="role-cell__code">{rol.codigo}</span>
                        </div>
                      </td>
                      <td>{conteoUsuarios[rol.codigo] ?? 0}</td>
                      <td>
                        <button
                          type="button"
                          className="btn btn--ghost btn--mini"
                          onClick={() => setExpandido(estaExpandido ? null : rol.id)}
                          style={{ gap: 4 }}
                        >
                          <EyeIcon size={16} />
                          {rol.permisos.length} permiso{rol.permisos.length === 1 ? "" : "s"}
                        </button>
                      </td>
                      <td>
                        <Badge tono={rol.activo ? "green" : "grey"}>
                          {rol.activo ? "Activo" : "Inactivo"}
                        </Badge>
                      </td>
                      <td>
                        <div className="table__actions">
                          <button
                            type="button"
                            className="btn btn--icon"
                            aria-label={`Editar ${rol.nombre}`}
                            onClick={() => setEditando(rol)}
                          >
                            <EditIcon size={19} />
                          </button>
                          <button
                            type="button"
                            className="btn btn--icon"
                            aria-label={`Duplicar ${rol.nombre}`}
                            onClick={() => duplicar(rol)}
                          >
                            <CopyIcon size={19} />
                          </button>
                          <button
                            type="button"
                            className="btn btn--icon"
                            aria-label={`Eliminar ${rol.nombre}`}
                            disabled={rol.sistema}
                            onClick={() => pedirEliminar(rol)}
                          >
                            <TrashIcon size={19} />
                          </button>
                        </div>
                      </td>
                    </tr>,
                    estaExpandido ? (
                      <tr key={`${rol.id}-permisos`} className="perm-detail-row">
                        <td colSpan={5} style={{ padding: "12px 18px", background: "var(--fp-bg)" }}>
                          <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
                            {permisosPorModulo.map((p) => (
                              <div key={p.modulo} style={{ minWidth: 140, fontSize: 13 }}>
                                <strong style={{ display: "block", marginBottom: 2, color: "var(--fp-text)" }}>{p.modulo}</strong>
                                <span style={{ color: "var(--fp-text-body)" }}>{p.acciones.join(", ")}</span>
                              </div>
                            ))}
                            {permisosPorModulo.length === 0 && (
                              <span style={{ color: "var(--fp-text-muted)", fontSize: 13 }}>Sin permisos asignados</span>
                            )}
                          </div>
                        </td>
                      </tr>
                    ) : null,
                  ].filter(Boolean);
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

      {/* --------------------------------------------- Modal de edición -- */}
      <Modal
        abierto={editando !== null}
        titulo={editando?.id ? "Editar rol" : "Nuevo rol"}
        subtitulo="Define el nombre del rol y marca qué puede hacer en cada módulo."
        ancho="ancho"
        alCerrar={() => setEditando(null)}
        pie={
          <>
            <span className="modal__count">
              {permisosDelModal} de {totalPermisos} permisos
            </span>
            <button type="button" className="btn btn--neutral" onClick={() => setEditando(null)}>
              Cancelar
            </button>
            <button type="button" className="btn btn--primary" onClick={guardar}>
              Guardar rol
            </button>
          </>
        }
      >
        {editando ? (
          <>
            <div className="modal__grid">
              <TextField
                etiqueta="Nombre del rol"
                requerido
                valor={editando.nombre}
                placeholder="Coordinador de sede"
                alCambiar={(v) =>
                  setEditando({
                    ...editando,
                    nombre: v,
                    // El código se sugiere solo mientras el rol es nuevo.
                    codigo: editando.sistema || editando.id ? editando.codigo : aCodigo(v),
                  })
                }
              />
              {editando.id ? (
                <TextField
                  etiqueta="Código"
                  valor={editando.codigo}
                  deshabilitado={editando.sistema}
                  ayuda={
                    editando.sistema
                      ? "Los roles del sistema conservan su código."
                      : "Se usa en la API y no debe repetirse."
                  }
                  alCambiar={(v) => setEditando({ ...editando, codigo: aCodigo(v) })}
                />
              ) : null}
              <SelectField
                etiqueta="Color de la etiqueta"
                valor={editando.tono}
                opciones={TONOS.map((t) => ({ valor: t.valor, etiqueta: t.etiqueta }))}
                alCambiar={(v) => setEditando({ ...editando, tono: v as TonoRol })}
              />
              <TextAreaField
                etiqueta="Descripción"
                filas={2}
                valor={editando.descripcion}
                placeholder="Acceso total al sistema"
                alCambiar={(v) => setEditando({ ...editando, descripcion: v })}
              />
            </div>

            <div className="setting-row">
              <div>
                <p className="setting-row__label">Rol activo</p>
                <p className="setting-row__hint">
                  Un rol inactivo conserva su configuración pero no se puede asignar a usuarios nuevos.
                </p>
              </div>
              <Switch
                marcado={editando.activo}
                etiqueta="Rol activo"
                alCambiar={(v) => setEditando({ ...editando, activo: v })}
              />
            </div>

            <div className="perm-head">
              <h3 className="section-title">Permisos por módulo</h3>
              <div className="perm-head__actions">
                <button
                  type="button"
                  className="btn btn--ghost"
                  onClick={() => setEditando({ ...editando, permisos: todosLosPermisos() })}
                >
                  Seleccionar todo
                </button>
                <button
                  type="button"
                  className="btn btn--ghost"
                  onClick={() => setEditando({ ...editando, permisos: [] })}
                >
                  Limpiar
                </button>
              </div>
            </div>

            <div className="table-wrap">
              <table className="table role-matrix perm-matrix">
                <thead>
                  <tr>
                    <th>Módulo</th>
                    {ACCIONES_PERMISO.map((accion) => (
                      <th key={accion.valor} style={{ textAlign: "center" }}>
                        {accion.etiqueta}
                      </th>
                    ))}
                    <th style={{ textAlign: "center" }}>Todo</th>
                  </tr>
                </thead>
                <tbody>
                  {MODULOS_PERMISOS.map((modulo) => (
                    <tr key={modulo}>
                      <td>{modulo}</td>
                      {ACCIONES_PERMISO.map((accion) => (
                        <td key={accion.valor} style={{ textAlign: "center" }}>
                          <input
                            type="checkbox"
                            checked={tienePermiso(modulo, accion.valor)}
                            onChange={() => alternarPermiso(modulo, accion.valor)}
                            aria-label={`${accion.etiqueta} en ${modulo}`}
                          />
                        </td>
                      ))}
                      <td style={{ textAlign: "center" }}>
                        <button
                          type="button"
                          className="btn btn--ghost btn--mini"
                          onClick={() => alternarModulo(modulo)}
                        >
                          {ACCIONES_PERMISO.every((a) => tienePermiso(modulo, a.valor))
                            ? "Quitar"
                            : "Todo"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        ) : null}
      </Modal>

      <ConfirmDialog
        abierto={aEliminar !== null}
        titulo="Eliminar rol"
        mensaje={`Se eliminará el rol "${aEliminar?.nombre ?? ""}" y su configuración de permisos. Esta acción no se puede deshacer.`}
        alCerrar={() => setAEliminar(null)}
        alConfirmar={confirmarEliminar}
      />
    </>
  );
}
