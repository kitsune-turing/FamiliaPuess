/* ==========================================================================
   Capa de acceso a datos del panel administrativo.

   `iniciarSesion` intenta primero contra el endpoint real `POST /auth/login`
   de la API. Si la API no está disponible todavía, cae en las credenciales de
   demostración definidas en `data/initial.ts`, de modo que la interfaz se puede
   recorrer completa sin backend.

   Para conectar el panel a la API real basta con definir VITE_API_BASE_URL en
   un archivo `.env` y borrar el bloque de respaldo marcado más abajo.
   ========================================================================== */

import type { PermisoModulo, Perfil, RolApi, UsuarioSesion } from "../types/admin";
import type {
  RegistroRequest,
  RegistroResponse,
  TokenValidarResponse,
} from "../types/registro";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

const CLAVE_SESION = "fp_sesion";
const CLAVE_TOKEN = "fp_access_token";
const CLAVE_RECORDAR = "fp_recordar";
const CLAVE_PERFIL = "fp_perfil";
const CLAVE_REFRESH = "fp_refresh_token";

/** Indica si el panel está apuntando a la API real o a los datos de demostración. */
export function hayApi(): boolean {
  return true;
}

/** Permiso tal como lo devuelve la API: un módulo con cuatro banderas. */
interface PermisoApi {
  modulo_codigo: string;
  modulo_nombre: string;
  puede_leer: boolean;
  puede_escribir: boolean;
  puede_eliminar: boolean;
  puede_administrar: boolean;
}

interface RespuestaLogin {
  access_token: string;
  refresh_token: string;
  usuario_id: number;
  nombre: string;
  username: string;
  rol_codigo: string;
  rol_nombre: string;
  debe_cambiar_pw?: boolean;
  permisos?: PermisoApi[];
}

export interface ResultadoLogin {
  usuario: UsuarioSesion;
  token: string;
  refresh?: string;
}

/** Traduce los permisos de la API al formato que usa la interfaz. */
function traducirPermisos(permisos: PermisoApi[] = []): PermisoModulo[] {
  return permisos.map((p) => ({
    moduloCodigo: p.modulo_codigo,
    moduloNombre: p.modulo_nombre,
    leer: p.puede_leer,
    escribir: p.puede_escribir,
    eliminar: p.puede_eliminar,
    administrar: p.puede_administrar,
  }));
}

export class ErrorCredenciales extends Error {}

export async function iniciarSesion(
  usuario: string,
  clave: string,
): Promise<ResultadoLogin> {
  // ---- Intento contra la API real ----------------------------------------
  {
    try {
      const respuesta = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: usuario, password: clave }),
      });

      if (respuesta.ok) {
        const datos = (await respuesta.json()) as RespuestaLogin;
        return {
          token: datos.access_token,
          refresh: datos.refresh_token,
          usuario: {
            usuarioId: datos.usuario_id,
            nombre: datos.nombre,
            username: datos.username,
            rolCodigo: datos.rol_codigo,
            rolNombre: datos.rol_nombre,
            debeCambiarClave: datos.debe_cambiar_pw ?? false,
            permisos: traducirPermisos(datos.permisos),
          },
        };
      }

      const cuerpo = (await respuesta.json().catch(() => null)) as { detail?: string } | null;
      throw new ErrorCredenciales(cuerpo?.detail ?? "Usuario o contraseña incorrectos.");
    } catch (error) {
      if (error instanceof ErrorCredenciales) throw error;
      throw new Error("No se pudo conectar con el servidor. Inténtalo de nuevo más tarde.");
    }
  }
}

/* --------------------------------------------------------- Persistencia -- */

export function guardarSesion(
  usuario: UsuarioSesion,
  token: string,
  recordar: boolean,
  refresh?: string,
): void {
  const almacen = recordar ? window.localStorage : window.sessionStorage;
  almacen.setItem(CLAVE_SESION, JSON.stringify(usuario));
  almacen.setItem(CLAVE_TOKEN, token);
  if (refresh) almacen.setItem(CLAVE_REFRESH, refresh);
  window.localStorage.setItem(CLAVE_RECORDAR, recordar ? "1" : "0");
}

/** Reemplaza solo los tokens tras un refresco, conservando el almacén usado. */
function guardarTokens(token: string, refresh: string): void {
  for (const almacen of [window.localStorage, window.sessionStorage]) {
    if (almacen.getItem(CLAVE_SESION)) {
      almacen.setItem(CLAVE_TOKEN, token);
      almacen.setItem(CLAVE_REFRESH, refresh);
    }
  }
}

function leerToken(): string | null {
  return (
    window.localStorage.getItem(CLAVE_TOKEN) ?? window.sessionStorage.getItem(CLAVE_TOKEN)
  );
}

function leerRefresh(): string | null {
  return (
    window.localStorage.getItem(CLAVE_REFRESH) ?? window.sessionStorage.getItem(CLAVE_REFRESH)
  );
}

export function leerSesion(): { usuario: UsuarioSesion; token: string } | null {
  for (const almacen of [window.localStorage, window.sessionStorage]) {
    const crudo = almacen.getItem(CLAVE_SESION);
    const token = almacen.getItem(CLAVE_TOKEN);
    if (crudo && token) {
      try {
        return { usuario: JSON.parse(crudo) as UsuarioSesion, token };
      } catch {
        almacen.removeItem(CLAVE_SESION);
        almacen.removeItem(CLAVE_TOKEN);
      }
    }
  }
  return null;
}

export function borrarSesion(): void {
  for (const almacen of [window.localStorage, window.sessionStorage]) {
    almacen.removeItem(CLAVE_SESION);
    almacen.removeItem(CLAVE_TOKEN);
    almacen.removeItem(CLAVE_REFRESH);
  }
}

/** Reescribe los datos de la sesión sin tocar el token (usado por Mi perfil). */
export function actualizarUsuarioSesion(usuario: UsuarioSesion): void {
  for (const almacen of [window.localStorage, window.sessionStorage]) {
    if (almacen.getItem(CLAVE_SESION)) {
      almacen.setItem(CLAVE_SESION, JSON.stringify(usuario));
    }
  }
}

/* ------------------------------------------------------------- Mi perfil */

export function leerPerfil(): Partial<Perfil> | null {
  const crudo = window.localStorage.getItem(CLAVE_PERFIL);
  if (!crudo) return null;
  try {
    return JSON.parse(crudo) as Partial<Perfil>;
  } catch {
    window.localStorage.removeItem(CLAVE_PERFIL);
    return null;
  }
}

export function guardarPerfil(perfil: Perfil): void {
  window.localStorage.setItem(CLAVE_PERFIL, JSON.stringify(perfil));
}

export function borrarPerfil(): void {
  window.localStorage.removeItem(CLAVE_PERFIL);
}

export function leerUsuarioRecordado(): string | null {
  if (window.localStorage.getItem(CLAVE_RECORDAR) !== "1") return null;
  const crudo = window.localStorage.getItem(CLAVE_SESION);
  if (!crudo) return null;
  try {
    return (JSON.parse(crudo) as UsuarioSesion).username;
  } catch {
    return null;
  }
}

/* ==========================================================================
   Cliente autenticado contra la API de FastAPI.

   Todas las llamadas pasan por `peticion`, que adjunta el token, renueva la
   sesión con `POST /auth/refresh` cuando el acceso caduca y avisa a la
   aplicación si la sesión ya no es recuperable.
   ========================================================================== */

export class ErrorSesionExpirada extends Error {
  constructor() {
    super("La sesión expiró. Vuelve a iniciar sesión.");
    this.name = "ErrorSesionExpirada";
  }
}

let alExpirarSesion: (() => void) | null = null;

/** El AuthProvider registra aquí su función de cierre de sesión. */
export function registrarManejadorSesionExpirada(manejador: () => void): void {
  alExpirarSesion = manejador;
}

/** Pide un token nuevo con el refresh token. Devuelve el acceso o null. */
async function refrescarAcceso(): Promise<string | null> {
  const refresh = leerRefresh();
  if (!refresh) return null;

  try {
    const respuesta = await fetch(`${API_BASE}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });
    if (!respuesta.ok) return null;

    const datos = (await respuesta.json()) as {
      access_token: string;
      refresh_token: string;
    };
    guardarTokens(datos.access_token, datos.refresh_token);
    return datos.access_token;
  } catch {
    return null;
  }
}

async function peticion<T>(ruta: string, init: RequestInit = {}, reintento = false): Promise<T> {

  const token = leerToken();
  const respuesta = await fetch(`${API_BASE}${ruta}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init.headers ?? {}),
    },
  });

  // Acceso caducado: se intenta renovar una sola vez.
  if (respuesta.status === 401 && !reintento) {
    const nuevo = await refrescarAcceso();
    if (nuevo) return peticion<T>(ruta, init, true);
    alExpirarSesion?.();
    throw new ErrorSesionExpirada();
  }

  if (respuesta.status === 401) {
    alExpirarSesion?.();
    throw new ErrorSesionExpirada();
  }

  if (respuesta.status === 204) return undefined as T;

  if (!respuesta.ok) {
    const cuerpo = (await respuesta.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(cuerpo?.detail ?? "Error inesperado del servidor.");
  }

  return (await respuesta.json()) as T;
}

/* ------------------------------------------------------------ Sesión ---- */

interface RespuestaMe {
  usuario_id: number;
  nombre: string;
  username: string;
  rol_codigo: string;
  rol_nombre: string;
  permisos?: {
    modulo_codigo: string;
    modulo_nombre: string;
    puede_leer: boolean;
    puede_escribir: boolean;
    puede_eliminar: boolean;
    puede_administrar: boolean;
  }[];
}

/** GET /auth/me: revalida la sesión guardada contra el servidor. */
export async function obtenerSesionActual(): Promise<UsuarioSesion> {
  const datos = await peticion<RespuestaMe>("/auth/me");
  return {
    usuarioId: datos.usuario_id,
    nombre: datos.nombre,
    username: datos.username,
    rolCodigo: datos.rol_codigo,
    rolNombre: datos.rol_nombre,
    debeCambiarClave: false,
    permisos: traducirPermisos(datos.permisos),
  };
}

/** POST /auth/logout: invalida el token en el servidor. */
export async function cerrarSesionEnApi(): Promise<void> {
  if (!API_BASE || !leerToken()) return;
  try {
    await peticion<void>("/auth/logout", { method: "POST" });
  } catch {
    // Si el servidor no responde, la sesión local se borra igual.
  }
}

/* ------------------------------------------------- Roles y permisos ----- */

interface RolApiCrudo {
  id: number;
  codigo: string;
  nombre: string;
  descripcion: string | null;
  id_estado: number;
}

interface PermisoRolCrudo {
  id: number;
  id_rol: number;
  id_modulo: number;
  modulo_codigo: string;
  modulo_nombre: string;
  puede_leer: boolean;
  puede_escribir: boolean;
  puede_eliminar: boolean;
  puede_administrar: boolean;
}

/** GET /roles */
export async function listarRoles(): Promise<RolApi[]> {
  const datos = await peticion<{ items: RolApiCrudo[]; total: number }>("/roles");
  return datos.items.map((r) => ({
    id: r.id,
    codigo: r.codigo,
    nombre: r.nombre,
    descripcion: r.descripcion ?? "",
    idEstado: r.id_estado,
  }));
}

/** POST /roles */
export async function crearRolApi(rol: {
  codigo: string;
  nombre: string;
  descripcion: string;
}): Promise<RolApi> {
  const r = await peticion<RolApiCrudo>("/roles", {
    method: "POST",
    body: JSON.stringify(rol),
  });
  return {
    id: r.id,
    codigo: r.codigo,
    nombre: r.nombre,
    descripcion: r.descripcion ?? "",
    idEstado: r.id_estado,
  };
}

/** PUT /roles/{id} — la API solo admite cambiar nombre y descripción. */
export async function actualizarRolApi(
  id: number,
  cambios: { nombre?: string; descripcion?: string },
): Promise<void> {
  await peticion<RolApiCrudo>(`/roles/${id}`, {
    method: "PUT",
    body: JSON.stringify(cambios),
  });
}

/** DELETE /roles/{id} */
export async function eliminarRolApi(id: number): Promise<void> {
  await peticion<void>(`/roles/${id}`, { method: "DELETE" });
}

/** GET /roles/{id}/permisos */
export async function listarPermisosRol(idRol: number): Promise<PermisoModulo[]> {
  const datos = await peticion<{ items: PermisoRolCrudo[]; total: number }>(
    `/roles/${idRol}/permisos`,
  );
  return datos.items.map((p) => ({
    id: p.id,
    idModulo: p.id_modulo,
    moduloCodigo: p.modulo_codigo,
    moduloNombre: p.modulo_nombre,
    leer: p.puede_leer,
    escribir: p.puede_escribir,
    eliminar: p.puede_eliminar,
    administrar: p.puede_administrar,
  }));
}

/** POST /roles/{idRol}/permisos */
export async function crearPermisoRol(
  idRol: number,
  permiso: {
    id_modulo: number;
    puede_leer: boolean;
    puede_escribir: boolean;
    puede_eliminar: boolean;
    puede_administrar: boolean;
  },
): Promise<void> {
  await peticion<PermisoRolCrudo>(`/roles/${idRol}/permisos`, {
    method: "POST",
    body: JSON.stringify(permiso),
  });
}

/** PUT /roles/{idRol}/permisos/{idPermiso} */
export async function actualizarPermisoRol(
  idRol: number,
  idPermiso: number,
  cambios: {
    puede_leer?: boolean;
    puede_escribir?: boolean;
    puede_eliminar?: boolean;
    puede_administrar?: boolean;
  },
): Promise<void> {
  await peticion<PermisoRolCrudo>(`/roles/${idRol}/permisos/${idPermiso}`, {
    method: "PUT",
    body: JSON.stringify(cambios),
  });
}

/** DELETE /roles/{idRol}/permisos/{idPermiso} */
export async function eliminarPermisoRol(idRol: number, idPermiso: number): Promise<void> {
  await peticion<void>(`/roles/${idRol}/permisos/${idPermiso}`, { method: "DELETE" });
}

/* ------------------------------------- Registro público de asistencia --- */

/**
 * GET /registro/validar/{token}
 *
 * Nota: la versión anterior del panel llamaba a este endpoint con POST y el
 * token en el cuerpo, lo que siempre fallaba. Aquí se usa la forma real que
 * expone el router de FastAPI.
 */
export async function validarToken(token: string): Promise<TokenValidarResponse> {
  const respuesta = await fetch(
    `${API_BASE}/registro/validar/${encodeURIComponent(token)}`,
  );
  if (!respuesta.ok) {
    const cuerpo = (await respuesta.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(cuerpo?.detail ?? "El código QR no es válido o ya expiró.");
  }
  return (await respuesta.json()) as TokenValidarResponse;
}

/** POST /registro/registrar */
export async function registrarAsistencia(
  datos: RegistroRequest,
): Promise<RegistroResponse> {
  const respuesta = await fetch(`${API_BASE}/registro/registrar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
  if (!respuesta.ok) {
    const cuerpo = (await respuesta.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(cuerpo?.detail ?? "No se pudo registrar la asistencia.");
  }
  return (await respuesta.json()) as RegistroResponse;
}

/* ==========================================================================
   CRUD de entidades — usan `peticion()` para autenticación y refresh.
   ========================================================================== */

/* ----------------------------------------------------------- Empleados --- */

export interface EmpleadoApi {
  id: number;
  documento: string;
  nombre: string;
  apellido: string;
  cargo: string;
  id_estado: number;
  created_at: string;
  updated_at: string;
}

export async function listarEmpleados(): Promise<{ items: EmpleadoApi[]; total: number }> {
  return peticion<{ items: EmpleadoApi[]; total: number }>("/empleados");
}

export async function crearEmpleado(data: {
  documento: string;
  nombre: string;
  apellido: string;
  cargo: string;
}): Promise<EmpleadoApi> {
  return peticion<EmpleadoApi>("/empleados", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function actualizarEmpleado(
  id: number,
  data: {
    documento?: string;
    nombre?: string;
    apellido?: string;
    cargo?: string;
    updated_at: string;
  },
): Promise<EmpleadoApi> {
  return peticion<EmpleadoApi>(`/empleados/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function eliminarEmpleadoApi(id: number): Promise<void> {
  await peticion<void>(`/empleados/${id}`, { method: "DELETE" });
}

export async function activarEmpleado(id: number): Promise<EmpleadoApi> {
  return peticion<EmpleadoApi>(`/empleados/${id}/activar`, { method: "POST" });
}

/* -------------------------------------------------------------- Sedes --- */

export interface SedeApi {
  id: number;
  nombre: string;
  direccion: string;
  id_estado: number;
  created_at: string;
  updated_at: string;
}

export async function listarSedes(): Promise<{ items: SedeApi[]; total: number }> {
  return peticion<{ items: SedeApi[]; total: number }>("/sedes?id_estado=1");
}

export async function crearSede(data: {
  nombre: string;
  direccion: string;
}): Promise<SedeApi> {
  return peticion<SedeApi>("/sedes", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function actualizarSede(
  id: number,
  data: { nombre?: string; direccion?: string; updated_at: string },
): Promise<SedeApi> {
  return peticion<SedeApi>(`/sedes/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function eliminarSedeApi(id: number): Promise<void> {
  await peticion<void>(`/sedes/${id}`, { method: "DELETE" });
}

export async function activarSede(id: number): Promise<SedeApi> {
  return peticion<SedeApi>(`/sedes/${id}/activar`, { method: "POST" });
}

/* -------------------------------------------------------- Dispositivos --- */

export interface DispositivoApi {
  id: number;
  identificador: string;
  id_sede: number | null;
  sede_nombre: string | null;
  descripcion: string | null;
  id_estado: number;
  created_at: string;
  updated_at: string;
}

export async function listarDispositivos(): Promise<{ items: DispositivoApi[]; total: number }> {
  return peticion<{ items: DispositivoApi[]; total: number }>("/dispositivos");
}

export async function crearDispositivo(data: {
  identificador: string;
  id_sede: number;
  descripcion?: string;
}): Promise<DispositivoApi> {
  return peticion<DispositivoApi>("/dispositivos", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function actualizarDispositivo(
  id: number,
  data: { identificador?: string; descripcion?: string; id_sede?: number | null; updated_at: string },
): Promise<DispositivoApi> {
  return peticion<DispositivoApi>(`/dispositivos/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function eliminarDispositivoApi(id: number): Promise<void> {
  await peticion<void>(`/dispositivos/${id}`, { method: "DELETE" });
}

export async function activarDispositivo(id: number): Promise<DispositivoApi> {
  return peticion<DispositivoApi>(`/dispositivos/${id}/activar`, { method: "POST" });
}

export async function desactivarDispositivo(id: number): Promise<DispositivoApi> {
  return peticion<DispositivoApi>(`/dispositivos/${id}/desactivar`, { method: "POST" });
}

/* ----------------------------------------------------------- Usuarios --- */

export interface UsuarioApi {
  id: number;
  nombre: string;
  correo: string;
  username: string;
  id_rol: number;
  rol_codigo: string;
  rol_nombre: string;
  id_estado: number;
  debe_cambiar_pw: boolean;
  ultimo_login: string | null;
  created_at: string;
  updated_at: string;
}

export async function listarUsuarios(): Promise<{ items: UsuarioApi[]; total: number }> {
  return peticion<{ items: UsuarioApi[]; total: number }>("/usuarios?id_estado=1");
}

export async function crearUsuario(data: {
  nombre: string;
  correo: string;
  username: string;
  password: string;
  id_rol: number;
}): Promise<UsuarioApi> {
  return peticion<UsuarioApi>("/usuarios", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function actualizarUsuario(
  id: number,
  data: { nombre?: string; correo?: string; username?: string; id_rol?: number; updated_at: string },
): Promise<UsuarioApi> {
  return peticion<UsuarioApi>(`/usuarios/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function eliminarUsuarioApi(id: number): Promise<void> {
  await peticion<void>(`/usuarios/${id}`, { method: "DELETE" });
}

export async function activarUsuario(id: number): Promise<UsuarioApi> {
  return peticion<UsuarioApi>(`/usuarios/${id}/activar`, { method: "POST" });
}

/* ---------------------------------------------------------- Auditoria --- */

export interface AuditoriaApi {
  id: number;
  id_usuario: number | null;
  recurso: string;
  id_recurso: string | null;
  operacion: string;
  ip_address: string | null;
  detalle: string | null;
  timestamp_accion: string;
}

export async function listarAuditoria(): Promise<{ items: AuditoriaApi[]; total: number }> {
  return peticion<{ items: AuditoriaApi[]; total: number }>("/auditoria?limit=200");
}

/* ----------------------------------------------------------- Dashboard --- */

export interface DashboardApi {
  empleados_activos: number;
  asistencias_hoy: number;
  novedades_hoy: number;
  tardanzas_hoy: number;
}

export async function obtenerDashboard(): Promise<DashboardApi> {
  return peticion<DashboardApi>("/dashboard");
}

/* ------------------------------------------------------------ Reportes --- */

export interface ReporteSemanalApi {
  id: number;
  fecha_inicio: string;
  fecha_fin: string;
  total_registros: number;
  total_novedades: number;
  created_at: string;
}

export async function listarReportesSemanales(): Promise<{ items: ReporteSemanalApi[]; total: number }> {
  return peticion<{ items: ReporteSemanalApi[]; total: number }>("/reportes/semanales");
}

/* ------------------------------------------------- Registros asistencia -- */

export interface RegistroAsistenciaApi {
  id: number;
  id_empleado: number;
  empleado_nombre: string;
  empleado_documento: string;
  id_sede: number;
  sede_nombre: string;
  tipo_registro: string;
  fecha_registro: string;
  registrado_en: string;
}

export async function listarRegistrosAsistencia(params?: {
  fecha_desde?: string;
  fecha_hasta?: string;
  id_sede?: number;
  id_empleado?: number;
}): Promise<{ items: RegistroAsistenciaApi[]; total: number }> {
  const qs = new URLSearchParams();
  if (params?.fecha_desde) qs.set("fecha_desde", params.fecha_desde);
  if (params?.fecha_hasta) qs.set("fecha_hasta", params.fecha_hasta);
  if (params?.id_sede) qs.set("id_sede", String(params.id_sede));
  if (params?.id_empleado) qs.set("id_empleado", String(params.id_empleado));
  const query = qs.toString();
  return peticion<{ items: RegistroAsistenciaApi[]; total: number }>(
    `/reportes/asistencia${query ? `?${query}` : ""}`,
  );
}

export async function descargarAsistenciaExcel(params?: {
  fecha_desde?: string;
  fecha_hasta?: string;
  id_sede?: number;
}): Promise<Blob> {
  const qs = new URLSearchParams();
  if (params?.fecha_desde) qs.set("fecha_desde", params.fecha_desde);
  if (params?.fecha_hasta) qs.set("fecha_hasta", params.fecha_hasta);
  if (params?.id_sede) qs.set("id_sede", String(params.id_sede));
  const query = qs.toString();

  const token = leerToken();
  const respuesta = await fetch(`${API_BASE}/reportes/asistencia/excel${query ? `?${query}` : ""}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  if (!respuesta.ok) {
    throw new Error("Error al descargar el archivo.");
  }

  return respuesta.blob();
}

/* ---------------------------------------------------------- Catálogos --- */

export interface ItemCatalogoApi {
  id: number;
  catalogo: string;
  codigo: string;
  nombre: string;
  descripcion: string | null;
  activo: boolean;
  created_at: string;
  updated_at: string;
}

export async function listarCatalogo(tipo: string): Promise<ItemCatalogoApi[]> {
  return peticion<ItemCatalogoApi[]>(`/catalogos/${tipo}`);
}

export async function crearItemCatalogo(
  tipo: string,
  data: { codigo: string; nombre: string; descripcion?: string },
): Promise<ItemCatalogoApi> {
  return peticion<ItemCatalogoApi>(`/catalogos/${tipo}`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function actualizarItemCatalogo(
  tipo: string,
  id: number,
  data: { codigo?: string; nombre?: string; descripcion?: string; activo?: boolean },
): Promise<ItemCatalogoApi> {
  return peticion<ItemCatalogoApi>(`/catalogos/${tipo}/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function eliminarItemCatalogoApi(tipo: string, id: number): Promise<void> {
  await peticion<void>(`/catalogos/${tipo}/${id}`, { method: "DELETE" });
}

/* ----------------------------------------------------------- Horarios --- */

export interface HorarioApi {
  id: number;
  id_sede: number;
  sede_nombre: string;
  nombre: string | null;
  hora_entrada: string;
  hora_salida: string | null;
  tolerancia_min: number;
  vigente_desde: string;
  vigente_hasta: string | null;
  created_at: string;
}

export async function listarHorarios(): Promise<{ items: HorarioApi[]; total: number }> {
  return peticion<{ items: HorarioApi[]; total: number }>("/horarios");
}

export async function crearHorario(data: {
  id_sede: number;
  nombre?: string;
  hora_entrada: string;
  hora_salida?: string;
  vigente_desde: string;
  vigente_hasta?: string;
}): Promise<HorarioApi> {
  return peticion<HorarioApi>("/horarios", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function actualizarHorario(
  id: number,
  data: {
    nombre?: string;
    hora_entrada?: string;
    hora_salida?: string;
    vigente_hasta?: string;
  },
): Promise<HorarioApi> {
  return peticion<HorarioApi>(`/horarios/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function eliminarHorarioApi(id: number): Promise<void> {
  await peticion<void>(`/horarios/${id}`, { method: "DELETE" });
}

/* ------------------------------------------------------- Configuración ---- */

export async function obtenerConfigGeneral(): Promise<Record<string, string>> {
  const res = await peticion<{ valores: Record<string, string> }>("/configuracion/general");
  return res.valores;
}

export async function guardarConfigGeneral(valores: Record<string, string>): Promise<void> {
  await peticion<unknown>("/configuracion/general", {
    method: "PUT",
    body: JSON.stringify({ valores }),
  });
}
