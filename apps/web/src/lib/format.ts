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

/** Fecha y hora actuales con el formato que usa la tabla de auditoría. */
export function fechaHoraActual(): string {
  const ahora = new Date();
  const fecha = ahora.toLocaleDateString("es-CO", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
  const hora = ahora.toLocaleTimeString("es-CO", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  });
  return `${fecha} ${hora}`;
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

/** Genera y descarga un archivo Excel (.xlsx) usando SpreadsheetML XML. */
export function descargarExcel(
  nombre: string,
  encabezados: string[],
  filas: (string | number)[][],
): void {
  const esc = (v: string | number) => String(v).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const celdas = (fila: (string | number)[], esEncabezado = false) =>
    fila
      .map((v) => {
        const tipo = typeof v === "number" ? "Number" : "String";
        const estilo = esEncabezado ? ' ss:StyleID="header"' : "";
        return `<Cell${estilo}><Data ss:Type="${tipo}">${esc(v)}</Data></Cell>`;
      })
      .join("");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
<Styles>
<Style ss:ID="Default"><Font ss:FontName="Calibri" ss:Size="11"/></Style>
<Style ss:ID="header"><Font ss:FontName="Calibri" ss:Size="11" ss:Bold="1"/><Interior ss:Color="#F2E9E0" ss:Pattern="Solid"/></Style>
</Styles>
<Worksheet ss:Name="Datos">
<Table>
${encabezados.map(() => `<Column ss:AutoFitWidth="1" ss:Width="120"/>`).join("\n")}
<Row>${celdas(encabezados, true)}</Row>
${filas.map((f) => `<Row>${celdas(f)}</Row>`).join("\n")}
</Table>
</Worksheet>
</Workbook>`;

  descargarArchivo(`${nombre}.xls`, xml, "application/vnd.ms-excel");
}
