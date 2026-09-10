import type {
  AccionPermiso,
  Actividad,
  AccionAuditoria,
  CatalogoTipo,
  ModuloAuditoria,
  Notificacion,
  Parametro,
  SesionActiva,
} from "../types/admin";

export const ACTIVIDADES: Actividad[] = [];
export const NOTIFICACIONES: Notificacion[] = [];
export const SESIONES: SesionActiva[] = [];
export const PARAMETROS: Parametro[] = [];

/** Segmentos de la gráfica de asistencia. Los valores los calcula el dashboard. */
export const SEGMENTOS_ASISTENCIA = [
  { clave: "a_tiempo", etiqueta: "A tiempo", color: "#6cbf5f" },
  { clave: "tarde", etiqueta: "Tarde", color: "#f2a20c" },
  { clave: "ausentes", etiqueta: "Ausentes", color: "#f24976" },
  { clave: "sin_registrar", etiqueta: "Sin registrar", color: "#f0e0c0" },
] as const;

/** Catálogos maestros que administra la pantalla de Catálogos. */
export const CATALOGOS: { valor: CatalogoTipo; etiqueta: string; descripcion: string }[] = [
  { valor: "cargos", etiqueta: "Cargos", descripcion: "Puestos de trabajo asignables a un trabajador." },
  { valor: "documentos", etiqueta: "Tipos de documento", descripcion: "Documentos de identidad aceptados." },
  { valor: "motivos", etiqueta: "Motivos de ausencia", descripcion: "Causas justificables de una inasistencia." },
];

/** Módulos auditables del sistema. Determinan el color de la etiqueta. */
export const MODULOS_AUDITORIA: ModuloAuditoria[] = [
  "Trabajadores",
  "Seguridad",
  "Sedes",
  "Dispositivos",
  "Reportes",
  "Usuarios",
  "Roles",
  "Perfil",
];

/** Acciones auditables del sistema. */
export const ACCIONES_AUDITORIA: AccionAuditoria[] = ["Crear", "Actualizar", "Eliminar", "Consultar"];

/** Módulos sobre los que se otorgan permisos por rol. */
export const MODULOS_PERMISOS = [
  "Dashboard",
  "Trabajadores",
  "Dispositivos",
  "Sedes",
  "Horarios",
  "Reportes",
  "Usuarios",
  "Roles",
  "Auditoría",
  "Configuración",
  "Catálogos",
];

/** Acciones que se pueden conceder sobre cada módulo. */
export const ACCIONES_PERMISO: { valor: AccionPermiso; etiqueta: string }[] = [
  { valor: "ver", etiqueta: "Ver" },
  { valor: "crear", etiqueta: "Crear" },
  { valor: "editar", etiqueta: "Editar" },
  { valor: "eliminar", etiqueta: "Eliminar" },
];

/** Construye la clave de permiso que guarda cada rol. */
export function clavePermiso(modulo: string, accion: AccionPermiso): string {
  return `${modulo}:${accion}`;
}

/** Todos los permisos posibles del sistema (acceso total). */
export function todosLosPermisos(): string[] {
  return MODULOS_PERMISOS.flatMap((modulo) =>
    ACCIONES_PERMISO.map((accion) => clavePermiso(modulo, accion.valor)),
  );
}


export const CREDENCIALES_DEMO = [
  {
    usuario: "admin@familiapuess.com",
    clave: "admin123",
    nombre: "Admin General",
    rol: "Súper administrador",
  },
];
