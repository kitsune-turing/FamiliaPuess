/* ==========================================================================
   Estado inicial de la aplicación.

   Todas las colecciones nacen vacías: la información real llegará desde la
   base de datos a través de la API. Este archivo solo define:

   1. Colecciones vacías tipadas, que `DataProvider` usa como estado inicial.
   2. Enumeraciones de código (roles, estados, módulos) que la interfaz
      necesita para pintar colores de etiquetas y armar los desplegables de
      filtro. No son datos de negocio: son el vocabulario que comparten el
      frontend y la API.

   Cuando conectes la base de datos, reemplaza las colecciones vacías por las
   respuestas de la API en `context/DataProvider.tsx`. Nada más cambia.
   ========================================================================== */

import type {
  Actividad,
  Auditoria,
  AccionAuditoria,
  CatalogoTipo,
  Dispositivo,
  ItemCatalogo,
  ModuloAuditoria,
  Notificacion,
  Parametro,
  RegistroEntrada,
  Reporte,
  Sede,
  SesionActiva,
  Trabajador,
  Usuario,
} from "../types/admin";

/* ========================================================================
   1. Colecciones de negocio — vacías hasta conectar la base de datos
   ======================================================================== */

export const SEDES: Sede[] = [];
export const TRABAJADORES: Trabajador[] = [];
export const DISPOSITIVOS: Dispositivo[] = [];
export const USUARIOS: Usuario[] = [];
export const REPORTES: Reporte[] = [];
export const REGISTROS: RegistroEntrada[] = [];
export const AUDITORIAS: Auditoria[] = [];
export const ACTIVIDADES: Actividad[] = [];
export const NOTIFICACIONES: Notificacion[] = [];
export const SESIONES: SesionActiva[] = [];
export const ITEMS_CATALOGO: ItemCatalogo[] = [];
export const PARAMETROS: Parametro[] = [];

/** Serie horaria de entradas del dashboard. La alimentará la API. */
export const ENTRADAS_POR_HORA: { etiqueta: string; valor: number }[] = [];

/** Ciudades disponibles en el filtro de sedes. Se derivarán de la tabla de sedes. */
export const CIUDADES: string[] = [];

/* ========================================================================
   2. Vocabulario del sistema — enumeraciones de código, no datos
   ======================================================================== */

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
  { valor: "tipos_reporte", etiqueta: "Tipos de reporte", descripcion: "Reportes disponibles en el generador." },
  {
    valor: "estados_dispositivo",
    etiqueta: "Estados de dispositivo",
    descripcion: "Estados de conexión que reportan los equipos.",
  },
];

/** Módulos auditables del sistema. Determinan el color de la etiqueta. */
export const MODULOS_AUDITORIA: ModuloAuditoria[] = [
  "Trabajadores",
  "Seguridad",
  "Sedes",
  "Dispositivos",
  "Reportes",
  "Usuarios",
];

/** Acciones auditables del sistema. */
export const ACCIONES_AUDITORIA: AccionAuditoria[] = ["Crear", "Actualizar", "Eliminar", "Consultar"];

/** Módulos sobre los que se otorgan permisos por rol. */
export const MODULOS_PERMISOS = [
  "Dashboard",
  "Registros de entrada",
  "Trabajadores",
  "Dispositivos",
  "Sedes",
  "Reportes",
  "Usuarios",
  "Auditoría",
];

/* ========================================================================
   3. Acceso temporal
   ======================================================================== */

/**
 * Credencial provisional para poder recorrer la interfaz mientras la API de
 * autenticación no esté conectada. No es un dato de negocio: es la llave de
 * entrada al panel.
 *
 * ELIMINAR al conectar la base de datos: basta con borrar este arreglo y el
 * bloque de respaldo marcado en `services/adminApi.ts`.
 */
export const CREDENCIALES_DEMO = [
  {
    usuario: "admin@familiapuess.com",
    clave: "admin123",
    nombre: "Admin General",
    rol: "Súper administrador",
  },
];
