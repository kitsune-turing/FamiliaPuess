/* Utilidades de formato compartidas por el panel. */

export function porcentaje(parte: number, total: number, decimales = 1): string {
  if (total <= 0) return "0%";
  const valor = (parte / total) * 100;
  const redondeado = Number.isInteger(valor) ? valor.toFixed(0) : valor.toFixed(decimales);
  return `${redondeado}%`;
}

export function numero(valor: number): string {
  return valor.toLocaleString("es-CO");
}

/** Convierte "2026-05-01" en "01/05/2026". */
export function isoAFecha(iso: string): string {
  const partes = iso.split("-");
  const anio = partes[0] ?? "";
  const mes = partes[1] ?? "";
  const dia = partes[2] ?? "";
  return `${dia}/${mes}/${anio}`;
}

/** Convierte "01/05/2026" en "2026-05-01". */
export function fechaAIso(fecha: string): string {
  const partes = fecha.split("/");
  const dia = partes[0] ?? "";
  const mes = partes[1] ?? "";
  const anio = partes[2] ?? "";
  return `${anio}-${mes}-${dia}`;
}

export function iniciales(nombre: string): string {
  return nombre
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((parte) => parte.charAt(0).toUpperCase())
    .join("");
}

/** Normaliza texto para búsquedas: sin tildes, en minúsculas. */
export function normalizar(texto: string): string {
  return texto
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

export function coincide(texto: string, consulta: string): boolean {
  if (!consulta.trim()) return true;
  return normalizar(texto).includes(normalizar(consulta.trim()));
}

/** Descarga un contenido de texto como archivo (usado por los reportes). */
export function descargarArchivo(nombre: string, contenido: string, tipo = "text/csv;charset=utf-8"): void {
  const blob = new Blob([`\uFEFF${contenido}`], { type: tipo });
  const url = URL.createObjectURL(blob);
  const enlace = document.createElement("a");
  enlace.href = url;
  enlace.download = nombre;
  document.body.appendChild(enlace);
  enlace.click();
  document.body.removeChild(enlace);
  URL.revokeObjectURL(url);
}

/** Construye un CSV a partir de encabezados y filas. */
export function generarCsv(encabezados: string[], filas: (string | number)[][]): string {
  const escapar = (valor: string | number) => {
    const texto = String(valor);
    return /[",;\n]/.test(texto) ? `"${texto.replace(/"/g, '""')}"` : texto;
  };
  return [encabezados, ...filas].map((fila) => fila.map(escapar).join(";")).join("\n");
}
