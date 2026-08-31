import type { LoginRequest, LoginResponse } from "../types/auth";
import type { DashboardIndicadores } from "../types/dashboard";
import type {
  ApiError,
  RegistroRequest,
  RegistroResponse,
  TokenValidarResponse,
} from "../types/registro";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export interface ApiList<T> {
  items: T[];
  total: number;
}

export interface ApiUsuario {
  id: number; nombre: string; correo: string; username: string; id_rol: number; rol_codigo: string; rol_nombre: string; id_estado: number; debe_cambiar_pw: boolean; ultimo_login: string | null; created_at: string; updated_at: string;
}
export interface ApiEmpleado {
  id: number; documento: string; nombre: string; apellido: string; cargo: string; id_estado: number; id_sede: number; sede_nombre: string; created_at: string; updated_at: string;
}
export interface ApiSede {
  id: number; nombre: string; direccion: string; id_estado: number; created_at: string; updated_at: string;
}
export interface ApiDispositivo {
  id: number; identificador: string; id_sede: number; sede_nombre: string; descripcion: string | null; id_estado: number; created_at: string; updated_at: string; ultimo_ping?: string | null;
}
export interface ApiAuditoria {
  id: number; recurso: string; operacion: string; ip_address: string | null; detalle: string | null; timestamp_accion: string; id_usuario: number | null;
}
export interface ApiReporteSemanal {
  id: number; fecha_inicio: string; fecha_fin: string; total_registros: number; total_novedades: number; created_at: string;
}
export interface ApiRol {
  id: number; codigo: string; nombre: string; id_estado: number;
}

export class SessionExpiredError extends Error {
  constructor() {
    super("La sesion ha expirado. Inicie sesion nuevamente.");
    this.name = "SessionExpiredError";
  }
}

let onSessionExpired: (() => void) | null = null;

export function setSessionExpiredHandler(handler: () => void): void {
  onSessionExpired = handler;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (response.status === 401) {
    onSessionExpired?.();
    throw new SessionExpiredError();
  }
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as ApiError | null;
    throw new Error(body?.detail ?? "Error inesperado del servidor");
  }
  return response.json() as Promise<T>;
}

async function handleNoContent(response: Response): Promise<void> {
  if (response.status === 401) {
    onSessionExpired?.();
    throw new SessionExpiredError();
  }
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as ApiError | null;
    throw new Error(body?.detail ?? "Error inesperado del servidor");
  }
}

function authHeaders(token: string): Record<string, string> {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

async function fetchList<T>(path: string, token: string): Promise<ApiList<T>> {
  const response = await fetch(`${API_BASE}${path}`, { headers: authHeaders(token) });
  return handleResponse<ApiList<T>>(response);
}

// ─── Auth ───────────────────────────────────────────────────
export async function login(payload: LoginRequest): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<LoginResponse>(response);
}

// ─── Dashboard ──────────────────────────────────────────────
export async function fetchDashboard(token: string): Promise<DashboardIndicadores> {
  const response = await fetch(`${API_BASE}/dashboard`, { headers: authHeaders(token) });
  return handleResponse<DashboardIndicadores>(response);
}

// ─── Registro ───────────────────────────────────────────────
export async function validarToken(token: string): Promise<TokenValidarResponse> {
  const response = await fetch(`${API_BASE}/registro/validar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });
  return handleResponse<TokenValidarResponse>(response);
}

export async function registrarAsistencia(payload: RegistroRequest): Promise<RegistroResponse> {
  const response = await fetch(`${API_BASE}/registro/registrar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<RegistroResponse>(response);
}

// ─── Usuarios ───────────────────────────────────────────────
export const fetchUsuarios = (token: string) => fetchList<ApiUsuario>("/usuarios", token);

export async function createUsuario(token: string, data: { nombre: string; correo: string; username: string; password: string; id_rol: number }) {
  const response = await fetch(`${API_BASE}/usuarios`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(data) });
  return handleResponse<ApiUsuario>(response);
}

export async function updateUsuario(token: string, id: number, data: { nombre?: string; correo?: string; username?: string; id_rol?: number; updated_at: string }) {
  const response = await fetch(`${API_BASE}/usuarios/${id}`, { method: "PUT", headers: authHeaders(token), body: JSON.stringify(data) });
  return handleResponse<ApiUsuario>(response);
}

export async function deleteUsuario(token: string, id: number) {
  const response = await fetch(`${API_BASE}/usuarios/${id}`, { method: "DELETE", headers: authHeaders(token) });
  return handleNoContent(response);
}

export async function activateUsuario(token: string, id: number) {
  const response = await fetch(`${API_BASE}/usuarios/${id}/activar`, { method: "POST", headers: authHeaders(token) });
  return handleResponse<ApiUsuario>(response);
}

// ─── Roles ──────────────────────────────────────────────────
export async function fetchRoles(token: string): Promise<ApiList<ApiRol>> {
  const response = await fetch(`${API_BASE}/roles`, { headers: authHeaders(token) });
  return handleResponse<ApiList<ApiRol>>(response);
}

// ─── Empleados ──────────────────────────────────────────────
export const fetchEmpleados = (token: string) => fetchList<ApiEmpleado>("/empleados", token);

export async function createEmpleado(token: string, data: { documento: string; nombre: string; apellido: string; cargo: string; id_sede: number }) {
  const response = await fetch(`${API_BASE}/empleados`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(data) });
  return handleResponse<ApiEmpleado>(response);
}

export async function updateEmpleado(token: string, id: number, data: { documento?: string; nombre?: string; apellido?: string; cargo?: string; id_sede?: number; updated_at: string }) {
  const response = await fetch(`${API_BASE}/empleados/${id}`, { method: "PUT", headers: authHeaders(token), body: JSON.stringify(data) });
  return handleResponse<ApiEmpleado>(response);
}

export async function deleteEmpleado(token: string, id: number) {
  const response = await fetch(`${API_BASE}/empleados/${id}`, { method: "DELETE", headers: authHeaders(token) });
  return handleNoContent(response);
}

export async function activateEmpleado(token: string, id: number) {
  const response = await fetch(`${API_BASE}/empleados/${id}/activar`, { method: "POST", headers: authHeaders(token) });
  return handleResponse<ApiEmpleado>(response);
}

// ─── Sedes ──────────────────────────────────────────────────
export const fetchSedes = (token: string) => fetchList<ApiSede>("/sedes", token);

export async function createSede(token: string, data: { nombre: string; direccion: string }) {
  const response = await fetch(`${API_BASE}/sedes`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(data) });
  return handleResponse<ApiSede>(response);
}

export async function updateSede(token: string, id: number, data: { nombre?: string; direccion?: string; updated_at: string }) {
  const response = await fetch(`${API_BASE}/sedes/${id}`, { method: "PUT", headers: authHeaders(token), body: JSON.stringify(data) });
  return handleResponse<ApiSede>(response);
}

export async function deleteSede(token: string, id: number) {
  const response = await fetch(`${API_BASE}/sedes/${id}`, { method: "DELETE", headers: authHeaders(token) });
  return handleNoContent(response);
}

export async function activateSede(token: string, id: number) {
  const response = await fetch(`${API_BASE}/sedes/${id}/activar`, { method: "POST", headers: authHeaders(token) });
  return handleResponse<ApiSede>(response);
}

// ─── Dispositivos ───────────────────────────────────────────
export const fetchDispositivos = (token: string) => fetchList<ApiDispositivo>("/dispositivos", token);

export async function createDispositivo(token: string, data: { identificador: string; id_sede: number; descripcion?: string }) {
  const response = await fetch(`${API_BASE}/dispositivos`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(data) });
  return handleResponse<ApiDispositivo>(response);
}

export async function updateDispositivo(token: string, id: number, data: { identificador?: string; descripcion?: string; updated_at: string }) {
  const response = await fetch(`${API_BASE}/dispositivos/${id}`, { method: "PUT", headers: authHeaders(token), body: JSON.stringify(data) });
  return handleResponse<ApiDispositivo>(response);
}

export async function deleteDispositivo(token: string, id: number) {
  const response = await fetch(`${API_BASE}/dispositivos/${id}`, { method: "DELETE", headers: authHeaders(token) });
  return handleNoContent(response);
}

export async function activateDispositivo(token: string, id: number) {
  const response = await fetch(`${API_BASE}/dispositivos/${id}/activar`, { method: "POST", headers: authHeaders(token) });
  return handleResponse<ApiDispositivo>(response);
}

// ─── Horarios ───────────────────────────────────────────────
export interface ApiHorario {
  id: number; id_sede: number; sede_nombre: string; nombre: string | null; hora_entrada: string; hora_salida: string | null; tolerancia_min: number; vigente_desde: string; vigente_hasta: string | null; created_at: string;
}

export async function fetchHorarios(token: string): Promise<ApiList<ApiHorario>> {
  const response = await fetch(`${API_BASE}/horarios`, { headers: authHeaders(token) });
  return handleResponse<ApiList<ApiHorario>>(response);
}

export async function createHorario(token: string, data: { id_sede: number; nombre?: string; hora_entrada: string; hora_salida?: string; tolerancia_min: number; vigente_desde: string; vigente_hasta?: string }) {
  const response = await fetch(`${API_BASE}/horarios`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(data) });
  return handleResponse<ApiHorario>(response);
}

export async function updateHorario(token: string, id: number, data: { nombre?: string; hora_entrada?: string; hora_salida?: string; tolerancia_min?: number; vigente_hasta?: string }) {
  const response = await fetch(`${API_BASE}/horarios/${id}`, { method: "PUT", headers: authHeaders(token), body: JSON.stringify(data) });
  return handleResponse<ApiHorario>(response);
}

export async function deleteHorario(token: string, id: number) {
  const response = await fetch(`${API_BASE}/horarios/${id}`, { method: "DELETE", headers: authHeaders(token) });
  return handleNoContent(response);
}

// ─── Configuracion ──────────────────────────────────────────
export interface ApiPasoSetup { clave: string; descripcion: string; completado: boolean; }
export interface ApiEstadoInicial { setup_completado: boolean; pasos: ApiPasoSetup[]; }

export async function fetchEstadoInicial(token: string): Promise<ApiEstadoInicial> {
  const response = await fetch(`${API_BASE}/configuracion/estado-inicial`, { headers: authHeaders(token) });
  return handleResponse<ApiEstadoInicial>(response);
}

export async function completarSetup(token: string): Promise<{ detail: string }> {
  const response = await fetch(`${API_BASE}/configuracion/completar-setup`, { method: "POST", headers: authHeaders(token) });
  return handleResponse<{ detail: string }>(response);
}

// ─── Auditoria ──────────────────────────────────────────────
export const fetchAuditoria = (token: string) => fetchList<ApiAuditoria>("/auditoria?limit=200", token);

// ─── Reportes ───────────────────────────────────────────────
export const fetchReportesSemanales = (token: string) => fetchList<ApiReporteSemanal>("/reportes/semanales", token);
