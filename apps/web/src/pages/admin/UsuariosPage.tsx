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
  TextField,
} from "../../components/ui";
import {
  EditIcon,
  PlusIcon,
  RefreshIcon,
  ShieldCheckIcon,
  TrashIcon,
  UserCheckIcon,
  UserXIcon,
  UsersIcon,
} from "../../components/ui/Icons";
import { useDatos } from "../../context/DataProvider";
import { useToast } from "../../context/ToastProvider";
import { usePaginacion } from "../../hooks";
import { coincide, porcentaje } from "../../lib/format";
import type { Usuario } from "../../types/admin";

const POR_PAGINA = 5;

const VACIO: Usuario = {
  id: "",
  nombre: "",
  correo: "",
  rol: "OPERADOR",
  sede: "",
  activo: true,
  ultimoAcceso: "Sin accesos",
};

export function UsuariosPage() {
  const { usuarios, roles, guardarUsuario, eliminarUsuario } = useDatos();
  const { mostrar } = useToast();

  const [busqueda, setBusqueda] = useState("");
  const [filtroRol, setFiltroRol] = useState("todos");
  const [filtroEstado, setFiltroEstado] = useState("todos");
  const [editando, setEditando] = useState<Usuario | null>(null);
  const [aEliminar, setAEliminar] = useState<Usuario | null>(null);

  /** Solo los roles activos se pueden asignar a un usuario. */
  const rolesAsignables = useMemo(() => roles.filter((r) => r.activo), [roles]);

  const metricas = useMemo(() => {
    const total = usuarios.length;
    const activos = usuarios.filter((u) => u.activo).length;
    return {
      total,
      activos,
      inactivos: total - activos,
      roles: roles.length,
    };
  }, [usuarios, roles]);

  const filtrados = useMemo(
    () =>
      usuarios.filter((usuario) => {
        const porTexto = coincide(usuario.nombre, busqueda) || coincide(usuario.correo, busqueda);
        const porRol = filtroRol === "todos" || usuario.rol === filtroRol;
        const porEstado =
          filtroEstado === "todos" || (filtroEstado === "activo" ? usuario.activo : !usuario.activo);
        return porTexto && porRol && porEstado;
      }),
    [usuarios, busqueda, filtroRol, filtroEstado],
  );

  const paginacion = usePaginacion(filtrados, POR_PAGINA);

  const limpiarFiltros = () => {
    setBusqueda("");
    setFiltroRol("todos");
    setFiltroEstado("todos");
    mostrar("Filtros restablecidos.", "info");
  };

  const guardar = async () => {
    if (!editando) return;
    if (!editando.nombre.trim()) {
      mostrar("El nombre del usuario es obligatorio.", "error");
      return;
    }
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(editando.correo)) {
      mostrar("Escribe un correo electrónico válido.", "error");
      return;
    }
    const esNuevo = !editando.id;
    try {
      await guardarUsuario({ ...editando, id: editando.id || `user-${Date.now()}` });
      setEditando(null);
      mostrar(esNuevo ? "Usuario creado." : "Usuario actualizado.");
    } catch (e) {
      mostrar(e instanceof Error ? e.message : "Error al guardar el usuario.", "error");
    }
  };

  return (
    <>
      <div className="stat-grid">
        <StatCard
          icono={<UsersIcon size={26} />}
          color="yellow"
          etiqueta="Total usuarios"
          valor={metricas.total}
          pista="En total"
        />
        <StatCard
          icono={<UserCheckIcon size={26} />}
          color="yellow"
          etiqueta="Usuarios activos"
          valor={metricas.activos}
          pista={`${porcentaje(metricas.activos, metricas.total)} del total`}
        />
        <StatCard
          icono={<UserXIcon size={26} />}
          color="pink"
          etiqueta="Usuarios inactivos"
          valor={metricas.inactivos}
          pista={`${porcentaje(metricas.inactivos, metricas.total)} del total`}
        />
        <StatCard
          icono={<ShieldCheckIcon size={26} />}
          color="yellow"
          etiqueta="Roles registrados"
          valor={metricas.roles}
          pista="En total"
        />
      </div>

      <Card>
        <div className="filters">
          <SearchInput valor={busqueda} alCambiar={setBusqueda} placeholder="Buscar usuario" etiquetaAccesible="Buscar usuario por nombre o correo" />
          <SelectField
            etiqueta="Rol"
            valor={filtroRol}
            alCambiar={setFiltroRol}
            opciones={[
              { valor: "todos", etiqueta: "Todos los roles" },
              ...roles.map((r) => ({ valor: r.codigo, etiqueta: r.nombre })),
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
          <button type="button" className="btn btn--ghost" onClick={limpiarFiltros}>
            <RefreshIcon size={20} /> Limpiar filtros
          </button>
          <button
            type="button"
            className="btn btn--primary"
            onClick={() =>
              setEditando({
                ...VACIO,
                rol: rolesAsignables[0]?.codigo ?? "OPERADOR",
              })
            }
          >
            <PlusIcon size={20} /> Nuevo usuario
          </button>
        </div>
      </Card>

      <Card>
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Correo electrónico</th>
                <th>Rol</th>
                <th>Estado</th>
                <th>Último acceso</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {paginacion.visibles.length === 0 ? (
                <EmptyRow columnas={6} mensaje={
                  usuarios.length === 0
                    ? "Aún no hay usuarios registrados."
                    : "No hay usuarios que coincidan con los filtros."
                } />
              ) : (
                paginacion.visibles.map((usuario) => {
                  const rol = roles.find((r) => r.codigo === usuario.rol);
                  return (
                    <tr key={usuario.id}>
                      <td>{usuario.nombre}</td>
                      <td>{usuario.correo}</td>
                      <td>
                        <Badge tono={rol?.tono ?? "grey"}>{rol?.nombre ?? usuario.rol}</Badge>
                      </td>
                      <td>
                        <Badge tono={usuario.activo ? "green" : "grey"}>
                          {usuario.activo ? "Activo" : "Inactivo"}
                        </Badge>
                      </td>
                      <td>{usuario.ultimoAcceso}</td>
                      <td>
                        <div className="table__actions">
                          <button
                            type="button"
                            className="btn btn--icon"
                            aria-label={`Editar ${usuario.nombre}`}
                            onClick={() => setEditando(usuario)}
                          >
                            <EditIcon size={19} />
                          </button>
                          <button
                            type="button"
                            className="btn btn--icon"
                            aria-label={`Eliminar ${usuario.nombre}`}
                            onClick={() => setAEliminar(usuario)}
                          >
                            <TrashIcon size={19} />
                          </button>
                        </div>
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
          info={`Mostrando ${paginacion.desde} a ${paginacion.hasta} de ${paginacion.total} usuarios`}
          irA={paginacion.irA}
        />
      </Card>

      <Modal
        abierto={editando !== null}
        titulo={editando?.id ? "Editar usuario" : "Nuevo usuario"}
        subtitulo="El rol determina a qué módulos puede acceder la persona."
        ancho="ancho"
        alCerrar={() => setEditando(null)}
        pie={
          <>
            <button type="button" className="btn btn--neutral" onClick={() => setEditando(null)}>
              Cancelar
            </button>
            <button type="button" className="btn btn--primary" onClick={guardar}>
              Guardar usuario
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
                alCambiar={(v) => setEditando({ ...editando, nombre: v })}
              />
              <TextField
                etiqueta="Correo electrónico"
                requerido
                tipo="email"
                placeholder="usuario@familiapuess.com"
                valor={editando.correo}
                alCambiar={(v) => setEditando({ ...editando, correo: v })}
              />
              <SelectField
                etiqueta="Rol"
                valor={editando.rol}
                opciones={rolesAsignables.map((r) => ({ valor: r.codigo, etiqueta: r.nombre }))}
                alCambiar={(v) => setEditando({ ...editando, rol: v })}
              />
            </div>
            <div className="setting-row">
              <div>
                <p className="setting-row__label">Usuario activo</p>
                <p className="setting-row__hint">
                  Un usuario inactivo conserva su historial pero no puede iniciar sesión.
                </p>
              </div>
              <Switch
                marcado={editando.activo}
                etiqueta="Usuario activo"
                alCambiar={(v) => setEditando({ ...editando, activo: v })}
              />
            </div>
          </>
        ) : null}
      </Modal>

      <ConfirmDialog
        abierto={aEliminar !== null}
        titulo="Eliminar usuario"
        mensaje={`Se eliminará la cuenta de ${aEliminar?.nombre ?? ""}. Las acciones que registró en auditoría se conservan.`}
        alCerrar={() => setAEliminar(null)}
        alConfirmar={async () => {
          if (aEliminar) {
            try {
              await eliminarUsuario(aEliminar.id);
              mostrar("Usuario eliminado.");
            } catch (e) {
              mostrar(e instanceof Error ? e.message : "Error al eliminar el usuario.", "error");
            }
          }
          setAEliminar(null);
        }}
      />
    </>
  );
}
