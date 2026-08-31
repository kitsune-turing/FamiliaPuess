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
  listarUsuarios,
  crearUsuario,
  actualizarUsuario,
  eliminarUsuarioApi,
  activarUsuario,
  listarRoles,
  listarPermisosRol,
  listarAuditoria,
  listarReportesSemanales,
  type EmpleadoApi,
  type SedeApi,
  type DispositivoApi,
  type UsuarioApi,
  type AuditoriaApi,
  type ReporteSemanalApi,
} from "../services/adminApi";
import type { PermisoModulo, RolApi } from "../types/admin";
import { useAuth } from "./AuthProvider";
import {
  ITEMS_CATALOGO,
  PARAMETROS,
  REGISTROS,
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
    sede: e.sede_nombre,
    cargo: e.cargo ?? "",
    correo: e.updated_at ?? "",
    telefono: "",
    codigoAlfa: "",
    activo: e.id_estado === 1,
    ingreso: e.created_at?.slice(0, 10) ?? "",
  };
}

function mapSede(s: SedeApi, empleados: EmpleadoApi[], dispositivos: DispositivoApi[]): Sede {
  return {
    id: String(s.id),
    nombre: s.nombre,
    direccion: s.direccion,
    ciudad: s.updated_at,
    trabajadores: empleados.filter((e) => e.id_sede === s.id && e.id_estado === 1).length,
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
    sede: d.sede_nombre,
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
  eliminarRol: (id: string) => void;

  agregarReporte: (reporte: Reporte) => void;
  eliminarReporte: (id: string) => void;

  guardarItemCatalogo: (item: ItemCatalogo) => void;
  eliminarItemCatalogo: (id: string) => void;

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
  const [registros] = useState<RegistroEntrada[]>(REGISTROS);
  const [auditorias, setAuditorias] = useState<Auditoria[]>([]);
  const [sesiones, setSesiones] = useState<SesionActiva[]>(SESIONES);
  const [itemsCatalogo, setItemsCatalogo] = useState<ItemCatalogo[]>(ITEMS_CATALOGO);
  const [parametros, setParametros] = useState<Parametro[]>(PARAMETROS);
  const [cargando, setCargando] = useState(false);

  // Raw API data for sede counts
  const [rawEmpleados, setRawEmpleados] = useState<EmpleadoApi[]>([]);
  const [rawDispositivos, setRawDispositivos] = useState<DispositivoApi[]>([]);

  const cargarDatos = useCallback(async () => {
    setCargando(true);
    try {
      const [empRes, sedeRes, dispRes, usrRes, rolRes, audRes, repRes] = await Promise.all([
        listarEmpleados().catch(() => ({ items: [] as EmpleadoApi[], total: 0 })),
        listarSedes().catch(() => ({ items: [] as SedeApi[], total: 0 })),
        listarDispositivos().catch(() => ({ items: [] as DispositivoApi[], total: 0 })),
        listarUsuarios().catch(() => ({ items: [] as UsuarioApi[], total: 0 })),
        listarRoles().catch(() => [] as RolApi[]),
        listarAuditoria().catch(() => ({ items: [] as AuditoriaApi[], total: 0 })),
        listarReportesSemanales().catch(() => ({ items: [] as ReporteSemanalApi[], total: 0 })),
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

      const cargosUnicos = Array.from(new Set(empRes.items.map((e) => e.cargo).filter(Boolean)));
      setItemsCatalogo((prev) => {
        const sinCargosViejos = prev.filter((i) => i.catalogo !== "cargos");
        const nuevosCargos: ItemCatalogo[] = cargosUnicos.map((c, idx) => ({
          id: `cargo-api-${idx}`,
          catalogo: "cargos" as const,
          codigo: c.toUpperCase().replace(/\s+/g, "_"),
          nombre: c,
          descripcion: "",
          orden: idx + 1,
          activo: true,
        }));

        const tiposReporteExistentes = prev.filter((i) => i.catalogo === "tipos_reporte");
        const tiposReportePorDefecto: ItemCatalogo[] = tiposReporteExistentes.length > 0
          ? []
          : [
              { id: "rep-tipo-1", catalogo: "tipos_reporte" as const, codigo: "ASISTENCIA_GENERAL", nombre: "Asistencia general", descripcion: "Reporte completo de entradas y ausencias.", orden: 1, activo: true },
              { id: "rep-tipo-2", catalogo: "tipos_reporte" as const, codigo: "LLEGADAS_TARDE", nombre: "Llegadas tarde", descripcion: "Detalle de registros con entrada tardía.", orden: 2, activo: true },
              { id: "rep-tipo-3", catalogo: "tipos_reporte" as const, codigo: "AUSENCIAS", nombre: "Ausencias", descripcion: "Trabajadores que no registraron entrada.", orden: 3, activo: true },
              { id: "rep-tipo-4", catalogo: "tipos_reporte" as const, codigo: "POR_SEDE", nombre: "Reporte por sede", descripcion: "Asistencia agrupada por sede.", orden: 4, activo: true },
            ];

        return [...sinCargosViejos, ...nuevosCargos, ...tiposReportePorDefecto];
      });
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
    const sedeObj = sedes.find((s) => s.nombre === trabajador.sede);
    const idSede = sedeObj ? Number(sedeObj.id) : 1;

    if (!trabajador.id || isNaN(numId)) {
      const nuevo = await crearEmpleado({
        documento: trabajador.documento,
        nombre,
        apellido,
        cargo: trabajador.cargo,
        id_sede: idSede,
      });
      setTrabajadores((prev) => [mapEmpleado(nuevo), ...prev]);
    } else {
      const existente = trabajadores.find((t) => t.id === trabajador.id);
      if (existente && trabajador.activo !== existente.activo) {
        const activado = await activarEmpleado(numId);
        setTrabajadores((prev) => prev.map((t) => t.id === trabajador.id ? mapEmpleado(activado) : t));
      }
      const actualizado = await actualizarEmpleado(numId, {
        documento: trabajador.documento,
        nombre,
        apellido,
        cargo: trabajador.cargo,
        id_sede: idSede,
        updated_at: existente?.correo || new Date().toISOString(),
      });
      setTrabajadores((prev) => prev.map((t) => t.id === trabajador.id ? mapEmpleado(actualizado) : t));
    }
  }, [sedes, trabajadores]);

  const eliminarTrabajadorHandler = useCallback(async (id: string) => {
    await eliminarEmpleadoApi(Number(id));
    setTrabajadores((prev) => prev.filter((t) => t.id !== id));
  }, []);

  /* ---- CRUD Dispositivos ---- */

  const guardarDispositivoHandler = useCallback(async (dispositivo: Dispositivo) => {
    const numId = Number(dispositivo.id);
    const sedeObj = sedes.find((s) => s.nombre === dispositivo.sede);
    const idSede = sedeObj ? Number(sedeObj.id) : 1;

    if (!dispositivo.id || isNaN(numId)) {
      const nuevo = await crearDispositivo({
        identificador: dispositivo.codigo || dispositivo.nombre,
        id_sede: idSede,
        descripcion: dispositivo.nombre,
      });
      setDispositivos((prev) => [mapDispositivo(nuevo), ...prev]);
    } else {
      const existente = dispositivos.find((d) => d.id === dispositivo.id);
      if (existente && dispositivo.activo !== existente.activo) {
        const activado = await activarDispositivo(numId);
        setDispositivos((prev) => prev.map((d) => d.id === dispositivo.id ? mapDispositivo(activado) : d));
      }
      const actualizado = await actualizarDispositivo(numId, {
        identificador: dispositivo.codigo,
        descripcion: dispositivo.nombre,
        updated_at: existente?.ultimaConexion || new Date().toISOString(),
      });
      setDispositivos((prev) => prev.map((d) => d.id === dispositivo.id ? mapDispositivo(actualizado) : d));
    }
  }, [sedes]);

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
      eliminarRol: (id) => setRoles((previos) => previos.filter((r) => r.id !== id)),

      agregarReporte: (reporte) => setReportes((previos) => [reporte, ...previos]),
      eliminarReporte: (id) => setReportes((previos) => previos.filter((r) => r.id !== id)),

      guardarItemCatalogo: (item) => setItemsCatalogo((previos) => upsert(previos, item)),
      eliminarItemCatalogo: (id) => setItemsCatalogo((previos) => previos.filter((i) => i.id !== id)),

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
