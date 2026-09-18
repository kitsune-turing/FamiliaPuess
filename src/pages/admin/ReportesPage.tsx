import { useMemo, useState } from "react";
import {
  Badge,
  Card,
  DateRangeField,
  EmptyRow,
  Pagination,
  SelectField,
  StatCard,
  type RangoFechas,
} from "../../components/ui";
import {
  DownloadIcon,
  FileCheckIcon,
  FilePlusIcon,
  FolderIcon,
  LoaderIcon,
} from "../../components/ui/Icons";
import { useDatos } from "../../context/DataProvider";
import { useToast } from "../../context/ToastProvider";
import { usePaginacion } from "../../hooks";
import { isoAFecha, porcentaje } from "../../lib/format";
import {
  listarRegistrosAsistencia,
  descargarAsistenciaExcel,
  type RegistroAsistenciaApi,
} from "../../services/adminApi";

const POR_PAGINA = 10;

export function ReportesPage() {
  const { sedes, registros } = useDatos();
  const { mostrar } = useToast();

  const [rango, setRango] = useState<RangoFechas>(() => {
    const hoy = new Date();
    const hace30 = new Date(hoy);
    hace30.setDate(hace30.getDate() - 30);
    return {
      desde: hace30.toISOString().slice(0, 10),
      hasta: hoy.toISOString().slice(0, 10),
    };
  });
  const [sede, setSede] = useState("todas");
  const [generando, setGenerando] = useState(false);
  const [resultados, setResultados] = useState<RegistroAsistenciaApi[]>([]);
  const [consultado, setConsultado] = useState(false);

  const metricas = useMemo(() => {
    const total = resultados.length;
    const aTiempo = resultados.filter((r) => r.tipo_registro !== "TARDANZA").length;
    const tardanzas = resultados.filter((r) => r.tipo_registro === "TARDANZA").length;
    return { total, aTiempo, tardanzas };
  }, [resultados]);

  const paginacion = usePaginacion(resultados, POR_PAGINA);

  const generar = async () => {
    setGenerando(true);
    try {
      const sedeObj = sede !== "todas" ? sedes.find((s) => s.nombre === sede) : null;
      const datos = await listarRegistrosAsistencia({
        fecha_desde: rango.desde || undefined,
        fecha_hasta: rango.hasta || undefined,
        id_sede: sedeObj ? Number(sedeObj.id) : undefined,
      });
      setResultados(datos.items);
      setConsultado(true);
      mostrar(`${datos.total} registro(s) encontrados.`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error al generar el reporte.";
      mostrar(msg, "error");
    } finally {
      setGenerando(false);
    }
  };

  const descargar = async () => {
    try {
      const sedeObj = sede !== "todas" ? sedes.find((s) => s.nombre === sede) : null;
      const blob = await descargarAsistenciaExcel({
        fecha_desde: rango.desde || undefined,
        fecha_hasta: rango.hasta || undefined,
        id_sede: sedeObj ? Number(sedeObj.id) : undefined,
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `reporte-asistencia-${rango.desde}-${rango.hasta}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
      mostrar("Descarga iniciada.");
    } catch {
      mostrar("Error al descargar el archivo.", "error");
    }
  };

  return (
    <>
      {/* ------------------------------------------------------ Métricas - */}
      <div className="stat-grid">
        <StatCard
          icono={<FolderIcon size={26} />}
          color="yellow"
          etiqueta="Registros encontrados"
          valor={metricas.total}
          pista="En el periodo consultado"
        />
        <StatCard
          icono={<FileCheckIcon size={26} />}
          color="yellow"
          etiqueta="A tiempo"
          valor={metricas.aTiempo}
          pista={`${porcentaje(metricas.aTiempo, metricas.total)} del total`}
        />
        <StatCard
          icono={<LoaderIcon size={26} />}
          color="pink"
          etiqueta="Tardanzas"
          valor={metricas.tardanzas}
          pista={`${porcentaje(metricas.tardanzas, metricas.total)} del total`}
        />
        <StatCard
          icono={<FolderIcon size={26} />}
          color="pink"
          etiqueta="Registros del sistema"
          valor={registros.length}
          pista="Total de asistencias"
        />
      </div>

      {/* ------------------------------------------- Filtros y acciones -- */}
      <Card>
        <div className="filters">
          <DateRangeField etiqueta="Rango de fechas" rango={rango} alCambiar={setRango} />
          <SelectField
            etiqueta="Sede"
            valor={sede}
            alCambiar={setSede}
            opciones={[
              { valor: "todas", etiqueta: "Todas las sedes" },
              ...sedes.map((s) => ({ valor: s.nombre, etiqueta: s.nombre })),
            ]}
          />
          <div className="filters__actions">
            <button
              type="button"
              className="btn btn--primary"
              onClick={generar}
              disabled={generando}
            >
              {generando ? <span className="spinner" /> : <FilePlusIcon size={20} />}
              {generando ? "Consultando…" : "Consultar"}
            </button>
            {consultado && resultados.length > 0 && (
              <button type="button" className="btn btn--soft" onClick={descargar}>
                <DownloadIcon size={20} /> Descargar Excel
              </button>
            )}
          </div>
        </div>
      </Card>

      {/* ------------------------------------------ Resultados ----------- */}
      <Card>
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Trabajador</th>
                <th>Documento</th>
                <th>Sede</th>
                <th>Tipo</th>
                <th>Fecha</th>
                <th>Hora</th>
              </tr>
            </thead>
            <tbody>
              {paginacion.visibles.length === 0 ? (
                <EmptyRow
                  columnas={6}
                  mensaje={
                    consultado
                      ? "No se encontraron registros en el periodo."
                      : "Selecciona un rango de fechas y consulta."
                  }
                />
              ) : (
                paginacion.visibles.map((r) => (
                  <tr key={r.id}>
                    <td>{r.empleado_nombre}</td>
                    <td>{r.empleado_documento}</td>
                    <td>{r.sede_nombre}</td>
                    <td>
                      <Badge tono={r.tipo_registro === "TARDANZA" ? "yellow" : "green"}>
                        {r.tipo_registro}
                      </Badge>
                    </td>
                    <td>{isoAFecha(r.fecha_registro)}</td>
                    <td>
                      {new Date(r.registrado_en).toLocaleTimeString("es-CO", {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <Pagination
          pagina={paginacion.pagina}
          totalPaginas={paginacion.totalPaginas}
          info={`Mostrando ${paginacion.desde} a ${paginacion.hasta} de ${paginacion.total} registros`}
          irA={paginacion.irA}
        />
      </Card>
    </>
  );
}
