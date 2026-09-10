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

/** Códigos de los roles base. Los roles creados desde el panel usan su propio código. */
export type RolCodigo = "SUPER_ADMIN" | "ADMIN" | "SUPERVISOR" | "AUDITOR" | "OPERADOR";

export interface Usuario {
  id: string;
  nombre: string;
  correo: string;
  /** Código del rol asignado. Se resuelve contra la colección de roles. */
  rol: string;
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

/* ------------------------------------------------------ Roles y permisos */

/** Acción concreta que un rol puede ejecutar sobre un módulo. */
export type AccionPermiso = "ver" | "crear" | "editar" | "eliminar";

/** Permiso con la forma "Módulo:acción". Por ejemplo: "Sedes:crear". */
export type ClavePermiso = string;

/** Color de la etiqueta con la que se pinta el rol en las tablas. */
export type TonoRol = "pink" | "orange" | "purple" | "green" | "yellow" | "grey";

export interface Rol {
  id: string;
  /** Código estable que usan la API y el resto de la interfaz. */
  codigo: string;
  nombre: string;
  descripcion: string;
  permisos: ClavePermiso[];
  activo: boolean;
  /** Los roles del sistema no se pueden eliminar ni renombrar su código. */
  sistema: boolean;
  tono: TonoRol;
}

/* ------------------------------------------------------------- Mi perfil */

export interface Perfil {
  nombre: string;
  correo: string;
  documento: string;
  telefono: string;
  cargo: string;
  sede: string;
  zonaHoraria: string;
  idioma: string;
  /** Imagen en base64 guardada en el navegador. Vacío = iniciales. */
  avatar: string;
  descripcion: string;
  notificarCorreo: boolean;
  resumenDiario: boolean;
}

export type ModuloAuditoria =
  | "Trabajadores"
  | "Seguridad"
  | "Sedes"
  | "Dispositivos"
  | "Reportes"
  | "Usuarios"
  | "Roles"
  | "Perfil";

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

/**
 * Permiso sobre un módulo, con las cuatro banderas que maneja la API
 * (`puede_leer`, `puede_escribir`, `puede_eliminar`, `puede_administrar`).
 */
export interface PermisoModulo {
  /** Id del registro PERMISO_ROL. Ausente si el permiso aún no existe. */
  id?: number;
  idModulo?: number;
  moduloCodigo: string;
  moduloNombre: string;
  leer: boolean;
  escribir: boolean;
  eliminar: boolean;
  administrar: boolean;
}

/** Rol tal como lo entrega `GET /roles`. */
export interface RolApi {
  id: number;
  codigo: string;
  nombre: string;
  descripcion: string;
  idEstado: number;
}

export interface UsuarioSesion {
  usuarioId: number;
  nombre: string;
  username: string;
  rolCodigo: string;
  rolNombre: string;
  /** La API obliga a cambiar la contraseña en el primer ingreso. */
  debeCambiarClave?: boolean;
  /** Permisos efectivos del rol. Vacío en modo de demostración. */
  permisos?: PermisoModulo[];
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
export type CatalogoTipo = "cargos" | "documentos" | "motivos";

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
