/* Tipos de dominio del panel administrativo. */

export type EstadoRegistro = "a_tiempo" | "tarde" | "ausente" | "sin_registrar";

export interface RegistroEntrada {
  id: string;
  trabajador: string;
  documento: string;
  sede: string;
  entrada: string;
  estado: EstadoRegistro;
  dispositivo: string;
  fecha: string; // ISO (yyyy-mm-dd)
}

export interface Trabajador {
  id: string;
  nombre: string;
  documento: string;
  sede: string;
  cargo: string;
  correo: string;
  telefono: string;
  codigoAlfa: string;
  activo: boolean;
  ingreso: string;
}

export type EstadoDispositivo = "en_linea" | "problemas" | "fuera_de_linea";

export interface Dispositivo {
  id: string;
  nombre: string;
  codigo: string;
  sede: string;
  ultimaConexion: string;
  estado: EstadoDispositivo;
  version: string;
  activo: boolean;
}

export interface Sede {
  id: string;
  nombre: string;
  direccion: string;
  ciudad: string;
  trabajadores: number;
  dispositivos: number;
  activa: boolean;
  telefono: string;
  responsable: string;
}

export type RolCodigo = "SUPER_ADMIN" | "ADMIN" | "SUPERVISOR" | "AUDITOR" | "OPERADOR";

export interface Usuario {
  id: string;
  nombre: string;
  correo: string;
  rol: RolCodigo;
  sede: string;
  activo: boolean;
  ultimoAcceso: string;
}

export type EstadoReporte = "completado" | "procesando" | "error";

export interface Reporte {
  id: string;
  nombre: string;
  rango: string;
  tipo: string;
  generadoPor: string;
  fechaHora: string;
  estado: EstadoReporte;
}

export type ModuloAuditoria =
  | "Trabajadores"
  | "Seguridad"
  | "Sedes"
  | "Dispositivos"
  | "Reportes"
  | "Usuarios";

export type AccionAuditoria = "Crear" | "Actualizar" | "Eliminar" | "Consultar";

export interface Auditoria {
  id: string;
  fechaHora: string;
  usuario: string;
  modulo: ModuloAuditoria;
  accion: AccionAuditoria;
  detalle: string;
  ip: string;
  dispositivo: string;
}

export interface Actividad {
  id: string;
  texto: string;
  tiempo: string;
  iniciales: string;
  color: string;
}

export interface Notificacion {
  id: string;
  texto: string;
  tiempo: string;
}

export interface SesionActiva {
  id: string;
  usuario: string;
  dispositivo: string;
  ip: string;
  inicio: string;
  actual: boolean;
}

export interface UsuarioSesion {
  usuarioId: number;
  nombre: string;
  username: string;
  rolCodigo: string;
  rolNombre: string;
}

/** Resultado paginado genérico usado por las tablas. */
export interface Pagina<T> {
  items: T[];
  total: number;
  pagina: number;
  porPagina: number;
  totalPaginas: number;
}

/* ---------------------------------------------------- Administración ---- */

/** Catálogo maestro: listas de valores que alimentan los formularios. */
export type CatalogoTipo = "cargos" | "documentos" | "motivos" | "tipos_reporte" | "estados_dispositivo";

export interface ItemCatalogo {
  id: string;
  catalogo: CatalogoTipo;
  codigo: string;
  nombre: string;
  descripcion: string;
  orden: number;
  activo: boolean;
}

/** Parámetro del sistema editable sin recompilar la aplicación. */
export type ParametroTipo = "texto" | "numero" | "booleano" | "hora";

export interface Parametro {
  id: string;
  clave: string;
  nombre: string;
  descripcion: string;
  valor: string;
  tipo: ParametroTipo;
  grupo: string;
  editable: boolean;
}
