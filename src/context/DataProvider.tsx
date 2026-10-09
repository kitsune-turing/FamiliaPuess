import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  listarEmpleados,
  crearEmpleado,
  actualizarEmpleado,
  eliminarEmpleadoApi,
  activarEmpleado,
  listarSedes,
  crearSede,
  actualizarSede,
  eliminarSedeApi,
  activarSede,
  listarDispositivos,
  crearDispositivo,
  actualizarDispositivo,
  eliminarDispositivoApi,
  activarDispositivo,
  desactivarDispositivo,
  listarUsuarios,
  crearUsuario,
  actualizarUsuario,
  eliminarUsuarioApi,
  activarUsuario,
  listarRoles,
  eliminarRolApi,
  listarPermisosRol,
  listarAuditoria,
  listarReportesSemanales,
  listarRegistrosAsistencia,
  listarCatalogo,
  crearItemCatalogo,
  actualizarItemCatalogo,
  eliminarItemCatalogoApi,
  type EmpleadoApi,
  type SedeApi,
  type DispositivoApi,
  type UsuarioApi,
  type AuditoriaApi,
  type ReporteSemanalApi,
  type RegistroAsistenciaApi,
  type ItemCatalogoApi,
} from "../services/adminApi";
import type { PermisoModulo, RolApi } from "../types/admin";
import { useAuth } from "./AuthProvider";
import {
  PARAMETROS,
  SESIONES,
} from "../data/initial";
import type {
  Auditoria,
  Dispositivo,
  ItemCatalogo,
  Parametro,
  RegistroEntrada,
  Reporte,
  Rol,
  Sede,
  SesionActiva,
  Trabajador,
  Usuario,
} from "../types/admin";

/* ========== Mappers: API → tipos de Sara ========== */

function mapEmpleado(e: EmpleadoApi): Trabajador {
  return {
    id: String(e.id),
    nombre: `${e.nombre} ${e.apellido}`,
    documento: e.documento,
    sede: "",
    cargo: e.cargo ?? "",
    correo: e.updated_at ?? "",
    telefono: "",
    codigoAlfa: "",
    activo: e.id_estado === 1,
    ingreso: e.created_at?.slice(0, 10) ?? "",
  };
}

function mapSede(s: SedeApi, _empleados: EmpleadoApi[], dispositivos: DispositivoApi[]): Sede {
  return {
    id: String(s.id),
    nombre: s.nombre,
    direccion: s.direccion,
    ciudad: s.updated_at,
    trabajadores: 0,
    dispositivos: dispositivos.filter((d) => d.id_sede === s.id && d.id_estado === 1).length,
    activa: s.id_estado === 1,
    telefono: "",
    responsable: "",
  };
}

function mapDispositivo(d: DispositivoApi): Dispositivo {
  return {
    id: String(d.id),
    nombre: d.descripcion ?? d.identificador,
    codigo: d.identificador,
    sede: d.sede_nombre ?? "",
    ultimaConexion: d.updated_at ?? "",
    estado: d.id_estado === 1 ? "en_linea" : "fuera_de_linea",
    version: "",
    activo: d.id_estado === 1,
  };
}

function mapUsuario(u: UsuarioApi): Usuario {
  return {
    id: String(u.id),
    nombre: u.nombre,
    correo: u.correo,
    rol: u.rol_codigo,
    sede: u.updated_at ?? "",
    activo: u.id_estado === 1,
    ultimoAcceso: u.ultimo_login ?? "Sin accesos",
  };
}

function mapAuditoria(a: AuditoriaApi): Auditoria {
  return {
    id: String(a.id),
    fechaHora: a.timestamp_accion,
    usuario: String(a.id_usuario ?? "Sistema"),
    modulo: (a.recurso as Auditoria["modulo"]) || "Seguridad",
    accion: (a.operacion as Auditoria["accion"]) || "Consultar",
    detalle: a.detalle ?? "",
    ip: a.ip_address ?? "",
    dispositivo: "",
  };
}

function mapReporteSemanal(r: ReporteSemanalApi): Reporte {
  return {
    id: String(r.id),
    nombre: `Reporte ${r.fecha_inicio} – ${r.fecha_fin}`,
    rango: `${r.fecha_inicio} – ${r.fecha_fin}`,
    tipo: "Semanal",
    generadoPor: "Sistema",
    fechaHora: r.created_at,
    estado: "completado",
  };
}

function mapRegistroAsistencia(r: RegistroAsistenciaApi): RegistroEntrada {
  const hora = r.registrado_en ? new Date(r.registrado_en).toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit" }) : "";
  return {
    id: r.id != null ? String(r.id) : `nr-${r.id_empleado}-${r.fecha_registro}`,
    trabajador: r.empleado_nombre,
    documento: r.empleado_documento,
    sede: r.sede_nombre,
    entrada: hora,
    estado:
      r.tipo_registro === "SIN_REGISTRAR"
        ? "sin_registrar"
        : r.tipo_registro === "TARDANZA"
          ? "tarde"
          : "a_tiempo",
    dispositivo: r.dispositivo_nombre ?? "",
    fecha: r.fecha_registro,
  };
}

function mapItemCatalogo(item: ItemCatalogoApi, idx: number): ItemCatalogo {
  return {
    id: `${item.catalogo}-${item.id}`,
    catalogo: item.catalogo as ItemCatalogo["catalogo"],
    codigo: item.codigo,
    nombre: item.nombre,
    descripcion: item.descripcion ?? "",
    orden: idx + 1,
    activo: item.activo,
  };
}

function catalogoNumericId(compositeId: string): number {
  const parts = compositeId.split("-");
  return Number(parts[parts.length - 1]);
}

const CATALOGO_TIPOS_API = ["cargos", "documentos", "motivos"] as const;

const MODULO_CODIGO_A_NOMBRE: Record<string, string> = {
  DASHBOARD: "Dashboard",
  USUARIOS: "Usuarios",
  ROLES: "Roles",
  CATALOGOS: "Catálogos",
  EMPLEADOS: "Trabajadores",
  CARGOS: "Cargos",
  SEDES: "Sedes",
  DISPOSITIVOS: "Dispositivos",
  HORARIOS: "Horarios",
  REPORTES: "Reportes",
  AUDITORIA: "Auditoría",
  CONFIGURACION: "Configuración",
  CALENDARIO: "Calendario",
  NOVEDADES: "Novedades",
};

function permisosApiAClaves(permisos: PermisoModulo[]): string[] {
  const claves: string[] = [];
  for (const p of permisos) {
    const modulo = MODULO_CODIGO_A_NOMBRE[p.moduloCodigo] ?? p.moduloNombre;
    if (p.leer) claves.push(`${modulo}:ver`);
    if (p.escribir) claves.push(`${modulo}:crear`, `${modulo}:editar`);
    if (p.eliminar) claves.push(`${modulo}:eliminar`);
  }
  return claves;
}

function mapRolApi(r: RolApi, permisos: string[] = []): Rol {
  return {
    id: String(r.id),
    codigo: r.codigo,
    nombre: r.nombre,
    descripcion: r.descripcion,
    permisos,
    activo: r.idEstado === 1,
    sistema: ["SUPER_ADMIN", "ADMIN", "SUPERVISOR", "AUDITOR", "OPERADOR"].includes(r.codigo),
    tono: r.codigo === "SUPER_ADMIN" ? "pink" : r.codigo === "ADMIN" ? "orange" : "purple",
  };
}

/* ========== Context interface ========== */

interface DataContextValue {
  sedes: Sede[];
  trabajadores: Trabajador[];
  dispositivos: Dispositivo[];
  usuarios: Usuario[];
  roles: Rol[];
  reportes: Reporte[];
  registros: RegistroEntrada[];
  auditorias: Auditoria[];
  sesiones: SesionActiva[];
  itemsCatalogo: ItemCatalogo[];
  parametros: Parametro[];
  cargando: boolean;

  guardarSede: (sede: Sede) => Promise<void>;
  eliminarSede: (id: string) => Promise<void>;

  guardarTrabajador: (trabajador: Trabajador) => Promise<void>;
  eliminarTrabajador: (id: string) => Promise<void>;

  guardarDispositivo: (dispositivo: Dispositivo) => Promise<void>;
  eliminarDispositivo: (id: string) => Promise<void>;

  guardarUsuario: (usuario: Usuario) => Promise<void>;
  eliminarUsuario: (id: string) => Promise<void>;

  guardarRol: (rol: Rol) => void;
  eliminarRol: (id: string) => Promise<void>;

  agregarReporte: (reporte: Reporte) => void;
  eliminarReporte: (id: string) => void;

  guardarItemCatalogo: (item: ItemCatalogo) => Promise<void>;
  eliminarItemCatalogo: (id: string) => Promise<void>;

  guardarParametro: (parametro: Parametro) => void;
  restablecerParametros: () => void;

  cerrarSesionRemota: (id: string) => void;
  registrarAuditoria: (entrada: Auditoria) => void;

  recargar: () => void;
}

const DataContext = createContext<DataContextValue | null>(null);

export function DataProvider({ children }: { children: ReactNode }) {
  const { usuario } = useAuth();

  const [trabajadores, setTrabajadores] = useState<Trabajador[]>([]);
  const [sedes, setSedes] = useState<Sede[]>([]);
  const [dispositivos, setDispositivos] = useState<Dispositivo[]>([]);
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [roles, setRoles] = useState<Rol[]>([]);
  const [reportes, setReportes] = useState<Reporte[]>([]);
  const [registros, setRegistros] = useState<RegistroEntrada[]>([]);
  const [auditorias, setAuditorias] = useState<Auditoria[]>([]);
  const [sesiones, setSesiones] = useState<SesionActiva[]>(SESIONES);
  const [itemsCatalogo, setItemsCatalogo] = useState<ItemCatalogo[]>([]);
  const [parametros, setParametros] = useState<Parametro[]>(PARAMETROS);
  const [cargando, setCargando] = useState(false);

  // Raw API data for sede counts
  const [rawEmpleados, setRawEmpleados] = useState<EmpleadoApi[]>([]);
  const [rawDispositivos, setRawDispositivos] = useState<DispositivoApi[]>([]);

  const cargarDatos = useCallback(async () => {
    setCargando(true);
    try {
      const [empRes, sedeRes, dispRes, usrRes, rolRes, audRes, repRes, regRes] = await Promise.all([
        listarEmpleados().catch(() => ({ items: [] as EmpleadoApi[], total: 0 })),
        listarSedes().catch(() => ({ items: [] as SedeApi[], total: 0 })),
        listarDispositivos().catch(() => ({ items: [] as DispositivoApi[], total: 0 })),
        listarUsuarios().catch(() => ({ items: [] as UsuarioApi[], total: 0 })),
        listarRoles().catch(() => [] as RolApi[]),
        listarAuditoria().catch(() => ({ items: [] as AuditoriaApi[], total: 0 })),
        listarReportesSemanales().catch(() => ({ items: [] as ReporteSemanalApi[], total: 0 })),
        listarRegistrosAsistencia().catch(() => ({ items: [] as RegistroAsistenciaApi[], total: 0 })),
      ]);

      setRawEmpleados(empRes.items);
      setRawDispositivos(dispRes.items);

      setTrabajadores(empRes.items.map(mapEmpleado));
      setSedes(sedeRes.items.map((s) => mapSede(s, empRes.items, dispRes.items)));
      setDispositivos(dispRes.items.map(mapDispositivo));
      setUsuarios(usrRes.items.map(mapUsuario));
      const rolesConPermisos = Array.isArray(rolRes)
        ? await Promise.all(
            rolRes.map(async (r) => {
              const permisos = await listarPermisosRol(r.id).catch(() => [] as PermisoModulo[]);
              return mapRolApi(r, permisosApiAClaves(permisos));
            }),
          )
        : [];
      setRoles(rolesConPermisos);
      setAuditorias(audRes.items.map(mapAuditoria));
      setReportes(repRes.items.map(mapReporteSemanal));
      setRegistros(regRes.items.map(mapRegistroAsistencia));

      const catalogoResults = await Promise.all(
        CATALOGO_TIPOS_API.map((tipo) =>
          listarCatalogo(tipo)
            .then((items) => items.map((item, idx) => mapItemCatalogo(item, idx)))
            .catch(() => [] as ItemCatalogo[]),
        ),
      );
      setItemsCatalogo(catalogoResults.flat());
    } catch {
      // Data stays empty on failure
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    if (usuario) {
      cargarDatos();
    }
  }, [usuario, cargarDatos]);

  const registrarAuditoria = useCallback((entrada: Auditoria) => {
    setAuditorias((previas) => [entrada, ...previas]);
  }, []);

  /* ---- CRUD Sedes ---- */

  const guardarSedeHandler = useCallback(async (sede: Sede) => {
    const numId = Number(sede.id);
    if (!sede.id || isNaN(numId)) {
      const nueva = await crearSede({ nombre: sede.nombre, direccion: sede.direccion });
      setSedes((prev) => [mapSede(nueva, rawEmpleados, rawDispositivos), ...prev]);
    } else {
      const existente = sedes.find((s) => s.id === sede.id);
      const estadoCambio = existente && sede.activa !== existente.activa;

      if (estadoCambio) {
        const activada = await activarSede(numId);
        setSedes((prev) => prev.map((s) => s.id === sede.id ? mapSede(activada, rawEmpleados, rawDispositivos) : s));
      }

      const nombreCambio = sede.nombre !== existente?.nombre;
      const direccionCambio = sede.direccion !== existente?.direccion;
      if (nombreCambio || direccionCambio) {
        const actualizada = await actualizarSede(numId, {
          nombre: nombreCambio ? sede.nombre : undefined,
          direccion: direccionCambio ? sede.direccion : undefined,
          updated_at: existente?.ciudad ?? new Date().toISOString(),
        });
        setSedes((prev) => prev.map((s) => s.id === sede.id ? mapSede(actualizada, rawEmpleados, rawDispositivos) : s));
      }
    }
  }, [rawEmpleados, rawDispositivos, sedes]);

  const eliminarSedeHandler = useCallback(async (id: string) => {
    await eliminarSedeApi(Number(id));
    setSedes((prev) => prev.filter((s) => s.id !== id));
  }, []);

  /* ---- CRUD Trabajadores ---- */

  const guardarTrabajadorHandler = useCallback(async (trabajador: Trabajador) => {
    const numId = Number(trabajador.id);
    const partes = trabajador.nombre.trim().split(/\s+/);
    const nombre = partes[0] ?? "";
    const apellido = partes.slice(1).join(" ") || nombre;

    if (!trabajador.id || isNaN(numId)) {
      const nuevo = await crearEmpleado({
        documento: trabajador.documento,
        nombre,
        apellido,
        cargo: trabajador.cargo,
      });
      setTrabajadores((prev) => [mapEmpleado(nuevo), ...prev]);
    } else {
      const existente = trabajadores.find((t) => t.id === trabajador.id);
      if (existente && trabajador.activo !== existente.activo) {
        if (trabajador.activo) {
          const activado = await activarEmpleado(numId);
          setTrabajadores((prev) => prev.map((t) => t.id === trabajador.id ? mapEmpleado(activado) : t));
        } else {
          await eliminarEmpleadoApi(numId);
          const res = await listarEmpleados();
          setTrabajadores(res.items.map(mapEmpleado));
        }
        return;
      }
      const actualizado = await actualizarEmpleado(numId, {
        documento: trabajador.documento,
        nombre,
        apellido,
        cargo: trabajador.cargo,
        updated_at: existente?.correo || new Date().toISOString(),
      });
      setTrabajadores((prev) => prev.map((t) => t.id === trabajador.id ? mapEmpleado(actualizado) : t));
    }
  }, [trabajadores]);

  const eliminarTrabajadorHandler = useCallback(async (id: string) => {
    await eliminarEmpleadoApi(Number(id));
    setTrabajadores((prev) => prev.filter((t) => t.id !== id));
  }, []);

  /* ---- CRUD Dispositivos ---- */

  const guardarDispositivoHandler = useCallback(async (dispositivo: Dispositivo) => {
    const numId = Number(dispositivo.id);
    const sedeObj = dispositivo.sede ? sedes.find((s) => s.nombre === dispositivo.sede) : null;
    const idSede: number | null = sedeObj ? Number(sedeObj.id) : null;

    if (!dispositivo.id || isNaN(numId)) {
      const nuevo = await crearDispositivo({
        identificador: dispositivo.codigo || dispositivo.nombre,
        id_sede: idSede ?? 1,
        descripcion: dispositivo.nombre,
      });
      setDispositivos((prev) => [mapDispositivo(nuevo), ...prev]);
    } else {
      const existente = dispositivos.find((d) => d.id === dispositivo.id);
      if (existente && dispositivo.activo !== existente.activo) {
        if (dispositivo.activo) {
          const activado = await activarDispositivo(numId);
          setDispositivos((prev) => prev.map((d) => d.id === dispositivo.id ? mapDispositivo(activado) : d));
        } else {
          const desactivado = await desactivarDispositivo(numId);
          setDispositivos((prev) => prev.map((d) => d.id === dispositivo.id ? mapDispositivo(desactivado) : d));
        }
        cargarDatos();
        return;
      }
      const updateData: { identificador?: string; descripcion?: string; id_sede?: number | null; updated_at: string } = {
        updated_at: existente?.ultimaConexion || new Date().toISOString(),
      };
      if (dispositivo.codigo !== existente?.codigo) {
        updateData.identificador = dispositivo.codigo;
      }
      if (dispositivo.nombre !== existente?.nombre) {
        updateData.descripcion = dispositivo.nombre;
      }
      if (dispositivo.sede !== existente?.sede) {
        updateData.id_sede = idSede;
      }
      const actualizado = await actualizarDispositivo(numId, updateData);
      setDispositivos((prev) => prev.map((d) => d.id === dispositivo.id ? mapDispositivo(actualizado) : d));
    }
    cargarDatos();
  }, [sedes, dispositivos, cargarDatos]);

  const eliminarDispositivoHandler = useCallback(async (id: string) => {
    await eliminarDispositivoApi(Number(id));
    setDispositivos((prev) => prev.filter((d) => d.id !== id));
  }, []);

  /* ---- CRUD Usuarios ---- */

  const guardarUsuarioHandler = useCallback(async (usuario: Usuario) => {
    const numId = Number(usuario.id);
    const rolObj = roles.find((r) => r.codigo === usuario.rol);
    const idRol = rolObj ? Number(rolObj.id) : 1;

    if (!usuario.id || isNaN(numId)) {
      const username = usuario.correo.split("@")[0] ?? usuario.nombre.toLowerCase().replace(/\s+/g, ".");
      const nuevo = await crearUsuario({
        nombre: usuario.nombre,
        correo: usuario.correo,
        username,
        password: "TempPass123!@#",
        id_rol: idRol,
      });
      setUsuarios((prev) => [mapUsuario(nuevo), ...prev]);
    } else {
      const existente = usuarios.find((u) => u.id === usuario.id);
      if (existente && usuario.activo !== existente.activo) {
        const activado = await activarUsuario(numId);
        setUsuarios((prev) => prev.map((u) => u.id === usuario.id ? mapUsuario(activado) : u));
      }
      const actualizado = await actualizarUsuario(numId, {
        nombre: usuario.nombre,
        correo: usuario.correo,
        id_rol: idRol,
        updated_at: existente?.sede || new Date().toISOString(),
      });
      setUsuarios((prev) => prev.map((u) => u.id === usuario.id ? mapUsuario(actualizado) : u));
    }
  }, [roles, usuarios]);

  const eliminarUsuarioHandler = useCallback(async (id: string) => {
    await eliminarUsuarioApi(Number(id));
    setUsuarios((prev) => prev.filter((u) => u.id !== id));
  }, []);

  /* ---- Upsert helpers (sync, for local-only entities) ---- */

  function upsert<T extends { id: string }>(lista: T[], elemento: T): T[] {
    const indice = lista.findIndex((item) => item.id === elemento.id);
    if (indice === -1) return [elemento, ...lista];
    const copia = [...lista];
    copia[indice] = elemento;
    return copia;
  }

  const valor = useMemo<DataContextValue>(
    () => ({
      sedes,
      trabajadores,
      dispositivos,
      usuarios,
      roles,
      reportes,
      registros,
      auditorias,
      sesiones,
      itemsCatalogo,
      parametros,
      cargando,

      guardarSede: guardarSedeHandler,
      eliminarSede: eliminarSedeHandler,

      guardarTrabajador: guardarTrabajadorHandler,
      eliminarTrabajador: eliminarTrabajadorHandler,

      guardarDispositivo: guardarDispositivoHandler,
      eliminarDispositivo: eliminarDispositivoHandler,

      guardarUsuario: guardarUsuarioHandler,
      eliminarUsuario: eliminarUsuarioHandler,

      guardarRol: (rol) => setRoles((previos) => upsert(previos, rol)),
      eliminarRol: async (id) => {
        await eliminarRolApi(Number(id));
        setRoles((previos) => previos.filter((r) => r.id !== id));
      },

      agregarReporte: (reporte) => setReportes((previos) => [reporte, ...previos]),
      eliminarReporte: (id) => setReportes((previos) => previos.filter((r) => r.id !== id)),

      guardarItemCatalogo: async (item) => {
        const tipo = item.catalogo;
        const numId = item.id ? catalogoNumericId(item.id) : NaN;
        if (!item.id || isNaN(numId)) {
          const nuevo = await crearItemCatalogo(tipo, {
            codigo: item.codigo,
            nombre: item.nombre,
            descripcion: item.descripcion || undefined,
          });
          setItemsCatalogo((prev) => [mapItemCatalogo(nuevo, prev.length), ...prev]);
        } else {
          const updated = await actualizarItemCatalogo(tipo, numId, {
            codigo: item.codigo,
            nombre: item.nombre,
            descripcion: item.descripcion,
            activo: item.activo,
          });
          setItemsCatalogo((prev) =>
            prev.map((i) => (i.id === item.id ? mapItemCatalogo(updated, 0) : i)),
          );
        }
      },
      eliminarItemCatalogo: async (id) => {
        const item = itemsCatalogo.find((i) => i.id === id);
        if (item) {
          await eliminarItemCatalogoApi(item.catalogo, catalogoNumericId(id));
        }
        setItemsCatalogo((prev) => prev.filter((i) => i.id !== id));
      },

      guardarParametro: (parametro) => setParametros((previos) => upsert(previos, parametro)),
      restablecerParametros: () => setParametros(PARAMETROS),

      cerrarSesionRemota: (id) => setSesiones((previas) => previas.filter((s) => s.id !== id)),
      registrarAuditoria,

      recargar: cargarDatos,
    }),
    [
      sedes,
      trabajadores,
      dispositivos,
      usuarios,
      roles,
      reportes,
      registros,
      auditorias,
      sesiones,
      itemsCatalogo,
      parametros,
      cargando,
      guardarSedeHandler,
      eliminarSedeHandler,
      guardarTrabajadorHandler,
      eliminarTrabajadorHandler,
      guardarDispositivoHandler,
      eliminarDispositivoHandler,
      guardarUsuarioHandler,
      eliminarUsuarioHandler,
      registrarAuditoria,
      cargarDatos,
    ],
  );

  return <DataContext.Provider value={valor}>{children}</DataContext.Provider>;
}

export function useDatos(): DataContextValue {
  const ctx = useContext(DataContext);
  if (!ctx) throw new Error("useDatos debe usarse dentro de DataProvider");
  return ctx;
}
