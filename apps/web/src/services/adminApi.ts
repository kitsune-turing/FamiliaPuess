/* ==========================================================================
   Cliente de los endpoints administrativos de la API.

   `services/api.ts` cubre autenticación, registro por QR y dashboard. Este
   archivo añade el resto de módulos que la API ya expone.

   Nota sobre concurrencia: los endpoints PUT exigen enviar el `updated_at`
   que devolvió la última lectura. Si otro usuario modificó el registro entre
   medias, la API responde 409 y el cambio se rechaza. Por eso los tipos de
   actualización incluyen ese campo como obligatorio.
   ========================================================================== */

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

/* ------------------------------------------------------------- Tipos ---- */

export interface Paginado<T> {
  items: T[];
  total: number;
}

export interface Sede {
  id: number;
  nombre: string;
  direccion: string;
  id_estado: number;
  created_at: string;
  updated_at: string;
}

export interface Empleado {
  id: number;
  documento: string;
  nombre: string;
  apellido: string;
  cargo: string;
  id_estado: number;
  id_sede: number;
  sede_nombre: string;
  created_at: string;
  updated_at: string;
}

export interface Dispositivo {
  id: number;
  identificador: string;
  nombre: string;
  id_sede: number;
  id_estado: number;
  created_at: string;
  updated_at: string;
}

export interface Usuario {
  id: number;
  nombre: string;
  correo: string;
  username: string;
  id_rol: number;
  id_estado: number;
  created_at: string;
  updated_at: string;
}

export interface Rol {
  id: number;
  codigo: string;
  nombre: string;
  descripcion: string | null;
  id_estado: number;
}

export interface Horario {
  id: number;
  id_sede: number;
  hora_entrada: string;
  hora_salida: string;
  tolerancia_minutos: number;
  updated_at: string;
}

export interface RegistroAuditoria {
  id: number;
  fecha_hora: string;
  usuario: string | null;
  modulo: string;
  accion: string;
  detalle: string | null;
  ip_address: string | null;
}

/* --------------------------------------------------- Cliente genérico --- */

/** Marca el vencimiento de sesión para que la app redirija al login. */
let onSessionExpired: (() => void) | null = null;

export function setAdminSessionExpiredHandler(handler: () => void): void {
  onSessionExpired = handler;
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  ruta: string,
  token: string,
  opciones: RequestInit = {},
): Promise<T> {
  const respuesta = await fetch(`${API_BASE}${ruta}`, {
    ...opciones,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...opciones.headers,
    },
  });

  if (respuesta.status === 401) {
    onSessionExpired?.();
    throw new ApiError("La sesión expiró. Inicia sesión nuevamente.", 401);
  }

  if (respuesta.status === 409) {
    throw new ApiError(
      "Otro usuario modificó este registro. Recarga la página e inténtalo de nuevo.",
      409,
    );
  }

  if (!respuesta.ok) {
    const cuerpo = (await respuesta.json().catch(() => null)) as { detail?: string } | null;
    throw new ApiError(cuerpo?.detail ?? "Error inesperado del servidor", respuesta.status);
  }

  // 204 No Content no trae cuerpo.
  if (respuesta.status === 204) return undefined as T;
  return respuesta.json() as Promise<T>;
}

/** Construye una cadena de consulta descartando valores vacíos. */
function query(parametros: Record<string, string | number | boolean | undefined>): string {
  const partes = Object.entries(parametros)
    .filter(([, valor]) => valor !== undefined && valor !== "")
    .map(([clave, valor]) => `${encodeURIComponent(clave)}=${encodeURIComponent(String(valor))}`);
  return partes.length > 0 ? `?${partes.join("&")}` : "";
}

/* ------------------------------------------------------------- Sedes ---- */

export const sedesApi = {
  listar: (token: string, params: { skip?: number; limit?: number } = {}) =>
    request<Paginado<Sede>>(`/sedes${query(params)}`, token),
  obtener: (token: string, id: number) => request<Sede>(`/sedes/${id}`, token),
  crear: (token: string, datos: { nombre: string; direccion: string }) =>
    request<Sede>("/sedes", token, { method: "POST", body: JSON.stringify(datos) }),
  actualizar: (
    token: string,
    id: number,
    datos: { nombre?: string; direccion?: string; updated_at: string },
  ) => request<Sede>(`/sedes/${id}`, token, { method: "PUT", body: JSON.stringify(datos) }),
  desactivar: (token: string, id: number) =>
    request<void>(`/sedes/${id}`, token, { method: "DELETE" }),
  activar: (token: string, id: number) =>
    request<Sede>(`/sedes/${id}/activar`, token, { method: "POST" }),
};

/* --------------------------------------------------------- Empleados --- */

export const empleadosApi = {
  listar: (
    token: string,
    params: { skip?: number; limit?: number; id_sede?: number; buscar?: string } = {},
  ) => request<Paginado<Empleado>>(`/empleados${query(params)}`, token),
  obtener: (token: string, id: number) => request<Empleado>(`/empleados/${id}`, token),
  crear: (
    token: string,
    datos: { documento: string; nombre: string; apellido: string; cargo: string; id_sede: number },
  ) => request<Empleado>("/empleados", token, { method: "POST", body: JSON.stringify(datos) }),
  actualizar: (
    token: string,
    id: number,
    datos: Partial<Omit<Empleado, "id" | "sede_nombre" | "created_at">> & { updated_at: string },
  ) => request<Empleado>(`/empleados/${id}`, token, { method: "PUT", body: JSON.stringify(datos) }),
  desactivar: (token: string, id: number) =>
    request<void>(`/empleados/${id}`, token, { method: "DELETE" }),
  activar: (token: string, id: number) =>
    request<Empleado>(`/empleados/${id}/activar`, token, { method: "POST" }),
};

/* ------------------------------------------------------ Dispositivos --- */

export const dispositivosApi = {
  listar: (token: string, params: { skip?: number; limit?: number; id_sede?: number } = {}) =>
    request<Paginado<Dispositivo>>(`/dispositivos${query(params)}`, token),
  obtener: (token: string, id: number) => request<Dispositivo>(`/dispositivos/${id}`, token),
  crear: (token: string, datos: { identificador: string; nombre: string; id_sede: number }) =>
    request<Dispositivo>("/dispositivos", token, { method: "POST", body: JSON.stringify(datos) }),
  actualizar: (
    token: string,
    id: number,
    datos: { nombre?: string; id_sede?: number; updated_at: string },
  ) =>
    request<Dispositivo>(`/dispositivos/${id}`, token, {
      method: "PUT",
      body: JSON.stringify(datos),
    }),
  desactivar: (token: string, id: number) =>
    request<void>(`/dispositivos/${id}`, token, { method: "DELETE" }),
  activar: (token: string, id: number) =>
    request<Dispositivo>(`/dispositivos/${id}/activar`, token, { method: "POST" }),
};

/* ---------------------------------------------------------- Usuarios --- */

export const usuariosApi = {
  listar: (token: string, params: { skip?: number; limit?: number } = {}) =>
    request<Paginado<Usuario>>(`/usuarios${query(params)}`, token),
  obtener: (token: string, id: number) => request<Usuario>(`/usuarios/${id}`, token),
  crear: (
    token: string,
    datos: { nombre: string; correo: string; username: string; password: string; id_rol: number },
  ) => request<Usuario>("/usuarios", token, { method: "POST", body: JSON.stringify(datos) }),
  actualizar: (
    token: string,
    id: number,
    datos: { nombre?: string; correo?: string; id_rol?: number; updated_at: string },
  ) => request<Usuario>(`/usuarios/${id}`, token, { method: "PUT", body: JSON.stringify(datos) }),
  desactivar: (token: string, id: number) =>
    request<void>(`/usuarios/${id}`, token, { method: "DELETE" }),
  activar: (token: string, id: number) =>
    request<Usuario>(`/usuarios/${id}/activar`, token, { method: "POST" }),
};

/* ------------------------------------------------- Roles y permisos ---- */

export const rolesApi = {
  listar: (token: string) => request<Paginado<Rol>>("/roles", token),
  obtener: (token: string, id: number) => request<Rol>(`/roles/${id}`, token),
  crear: (token: string, datos: { codigo: string; nombre: string; descripcion?: string }) =>
    request<Rol>("/roles", token, { method: "POST", body: JSON.stringify(datos) }),
  permisos: (token: string, rolId: number) => request<unknown>(`/roles/${rolId}/permisos`, token),
};

/* --------------------------------------------------------- Horarios ---- */

export const horariosApi = {
  listar: (token: string, params: { id_sede?: number } = {}) =>
    request<Paginado<Horario>>(`/horarios${query(params)}`, token),
  crear: (
    token: string,
    datos: {
      id_sede: number;
      hora_entrada: string;
      hora_salida: string;
      tolerancia_minutos: number;
    },
  ) => request<Horario>("/horarios", token, { method: "POST", body: JSON.stringify(datos) }),
  actualizar: (token: string, id: number, datos: Record<string, unknown>) =>
    request<Horario>(`/horarios/${id}`, token, { method: "PUT", body: JSON.stringify(datos) }),
  eliminar: (token: string, id: number) =>
    request<void>(`/horarios/${id}`, token, { method: "DELETE" }),
};

/* --------------------------------------------------------- Reportes ---- */

export const reportesApi = {
  asistencia: (
    token: string,
    params: { fecha_inicio: string; fecha_fin: string; id_sede?: number },
  ) => request<unknown>(`/reportes/asistencia${query(params)}`, token),

  /** Descarga el Excel de asistencia como Blob. */
  asistenciaExcel: async (
    token: string,
    params: { fecha_inicio: string; fecha_fin: string; id_sede?: number },
  ): Promise<Blob> => {
    const respuesta = await fetch(`${API_BASE}/reportes/asistencia/excel${query(params)}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!respuesta.ok) throw new ApiError("No fue posible generar el Excel.", respuesta.status);
    return respuesta.blob();
  },

  semanales: (token: string) => request<unknown>("/reportes/semanales", token),
  generarSemanal: (token: string, datos: Record<string, unknown>) =>
    request<unknown>("/reportes/semanales/generar", token, {
      method: "POST",
      body: JSON.stringify(datos),
    }),
};

/* -------------------------------------------------------- Auditoría ---- */

export const auditoriaApi = {
  listar: (
    token: string,
    params: {
      skip?: number;
      limit?: number;
      fecha_inicio?: string;
      fecha_fin?: string;
      modulo?: string;
      accion?: string;
    } = {},
  ) => request<Paginado<RegistroAuditoria>>(`/auditoria${query(params)}`, token),
};

/* ----------------------------------------------------- Configuración --- */

export const configuracionApi = {
  estadoInicial: (token: string) => request<unknown>("/configuracion/estado-inicial", token),
  completarSetup: (token: string) =>
    request<unknown>("/configuracion/completar-setup", token, { method: "POST" }),
};

/* ---------------------------------------------------------- Novedades -- */

export const novedadesApi = {
  listar: (token: string, params: { skip?: number; limit?: number } = {}) =>
    request<unknown>(`/novedades${query(params)}`, token),
  obtener: (token: string, id: number) => request<unknown>(`/novedades/${id}`, token),
};
