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
} from "../components/ui";
import {
  EditIcon,
  PlusIcon,
  RefreshIcon,
  ShieldCheckIcon,
  TrashIcon,
  UserCheckIcon,
  UserXIcon,
  UsersIcon,
} from "../components/ui/Icons";
import { useDatos } from "../context/DataProvider";
import { useToast } from "../context/ToastProvider";
import { usePaginacion } from "../hooks";
import { coincide, porcentaje } from "../lib/format";
import type { RolCodigo, Usuario } from "../types/admin";

const POR_PAGINA = 5;

export const ROLES: { valor: RolCodigo; etiqueta: string; tono: "pink" | "orange" | "purple" | "green" | "grey" }[] = [
  { valor: "SUPER_ADMIN", etiqueta: "Súper admin", tono: "pink" },
  { valor: "ADMIN", etiqueta: "Administrador", tono: "orange" },
  { valor: "SUPERVISOR", etiqueta: "Supervisor", tono: "purple" },
  { valor: "AUDITOR", etiqueta: "Auditor", tono: "green" },
  { valor: "OPERADOR", etiqueta: "Operador", tono: "grey" },
];

function rolInfo(codigo: RolCodigo) {
  return ROLES.find((r) => r.valor === codigo) ?? ROLES[4];
}

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
  const { usuarios, sedes, guardarUsuario, eliminarUsuario } = useDatos();
  const { mostrar } = useToast();

  const [busqueda, setBusqueda] = useState("");
  const [filtroRol, setFiltroRol] = useState("todos");
  const [filtroSede, setFiltroSede] = useState("todas");
  const [filtroEstado, setFiltroEstado] = useState("todos");
  const [editando, setEditando] = useState<Usuario | null>(null);
  const [aEliminar, setAEliminar] = useState<Usuario | null>(null);

  const metricas = useMemo(() => {
    const total = usuarios.length;
    const activos = usuarios.filter((u) => u.activo).length;
    return {
      total,
      activos,
      inactivos: total - activos,
      roles: new Set(usuarios.map((u) => u.rol)).size,
    };
  }, [usuarios]);

  const filtrados = useMemo(
    () =>
      usuarios.filter((usuario) => {
        const porTexto = coincide(usuario.nombre, busqueda) || coincide(usuario.correo, busqueda);
        const porRol = filtroRol === "todos" || usuario.rol === filtroRol;
        const porSede = filtroSede === "todas" || usuario.sede === filtroSede;
        const porEstado =
          filtroEstado === "todos" || (filtroEstado === "activo" ? usuario.activo : !usuario.activo);
        return porTexto && porRol && porSede && porEstado;
      }),
    [usuarios, busqueda, filtroRol, filtroSede, filtroEstado],
  );

  const paginacion = usePaginacion(filtrados, POR_PAGINA);

  const limpiarFiltros = () => {
    setBusqueda("");
    setFiltroRol("todos");
    setFiltroSede("todas");
    setFiltroEstado("todos");
    mostrar("Filtros restablecidos.", "info");
  };

  const guardar = () => {
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
    guardarUsuario({ ...editando, id: editando.id || `user-${Date.now()}` });
    setEditando(null);
    mostrar(esNuevo ? "Usuario creado." : "Usuario actualizado.");
  };

  return (
    <>
      <div className="page-actions">
        <button
          type="button"
          className="btn btn--primary"
          onClick={() => setEditando({ ...VACIO, sede: sedes[0]?.nombre ?? "" })}
        >
          <PlusIcon size={20} /> Nuevo usuario
        </button>
      </div>

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
          <SearchInput valor={busqueda} alCambiar={setBusqueda} placeholder="Buscar usuario" />
          <SelectField
            etiqueta="Rol"
            valor={filtroRol}
            alCambiar={setFiltroRol}
            opciones={[
              { valor: "todos", etiqueta: "Todos los roles" },
              ...ROLES.map((r) => ({ valor: r.valor, etiqueta: r.etiqueta })),
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
                <th>Sede</th>
                <th>Estado</th>
                <th>Último acceso</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {paginacion.visibles.length === 0 ? (
                <EmptyRow columnas={7} mensaje={
                  usuarios.length === 0
                    ? "Aún no hay usuarios registrados."
                    : "No hay usuarios que coincidan con los filtros."
                } />
              ) : (
                paginacion.visibles.map((usuario) => {
                  const rol = rolInfo(usuario.rol);
                  return (
                    <tr key={usuario.id}>
                      <td>{usuario.nombre}</td>
                      <td>{usuario.correo}</td>
                      <td>
                        <Badge tono={rol?.tono ?? "grey"}>{rol?.etiqueta ?? usuario.rol}</Badge>
                      </td>
                      <td>{usuario.sede}</td>
                      <td>
                        <Badge tono={usuario.activo ? "green" : "grey"}>
                          {usuario.activo ? "Activa" : "Inactiva"}
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
                opciones={ROLES.map((r) => ({ valor: r.valor, etiqueta: r.etiqueta }))}
                alCambiar={(v) => setEditando({ ...editando, rol: v as RolCodigo })}
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
        alConfirmar={() => {
          if (aEliminar) {
            eliminarUsuario(aEliminar.id);
            mostrar("Usuario eliminado.");
          }
          setAEliminar(null);
        }}
      />
    </>
  );
}
