import { useMemo, useState } from "react";
import {
  Badge,
  Card,
  ConfirmDialog,
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
  FileXIcon,
  FolderIcon,
  LoaderIcon,
  TrashIcon,
} from "../../components/ui/Icons";
import { useDatos } from "../../context/DataProvider";
import { useToast } from "../../context/ToastProvider";
import { usePaginacion } from "../../hooks";
import { descargarExcel, isoAFecha, porcentaje } from "../../lib/format";
import type { EstadoReporte, Reporte } from "../../types/admin";

const POR_PAGINA = 5;

const ETIQUETA_ESTADO: Record<EstadoReporte, string> = {
  completado: "Completado",
  procesando: "En proceso",
  error: "Con errores",
};

const TONO_ESTADO: Record<EstadoReporte, "green" | "yellow" | "pink"> = {
  completado: "green",
  procesando: "yellow",
  error: "pink",
};

export function ReportesPage() {
  const { reportes, sedes, registros, itemsCatalogo, agregarReporte, eliminarReporte } = useDatos();
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
  const [tipo, setTipo] = useState("");
  const [sede, setSede] = useState("todas");
  const [generando, setGenerando] = useState(false);
  const [aEliminar, setAEliminar] = useState<Reporte | null>(null);

  // Los tipos disponibles se administran desde Catálogos › Tipos de reporte.
  const tipos = useMemo(
    () =>
      itemsCatalogo
        .filter((i) => i.catalogo === "tipos_reporte" && i.activo)
        .sort((a, b) => a.orden - b.orden)
        .map((i) => ({ valor: i.nombre, etiqueta: i.nombre })),
    [itemsCatalogo],
  );

  const metricas = useMemo(() => {
    const total = reportes.length;
    return {
      total,
      completados: reportes.filter((r) => r.estado === "completado").length,
      procesando: reportes.filter((r) => r.estado === "procesando").length,
      error: reportes.filter((r) => r.estado === "error").length,
    };
  }, [reportes]);

  const paginacion = usePaginacion(reportes, POR_PAGINA);

  const generar = () => {
    if (!tipo) {
      mostrar("Configura primero los tipos de reporte en Catálogos.", "error");
      return;
    }
    setGenerando(true);
    // Simula el tiempo de procesamiento del backend.
    window.setTimeout(() => {
      agregarReporte({
        id: `rep-${Date.now()}`,
        nombre: tipo,
        rango: `${isoAFecha(rango.desde)} - ${isoAFecha(rango.hasta)}`,
        tipo,
        generadoPor: "Admin General",
        fechaHora: new Date().toLocaleString("es-CO", {
          day: "2-digit",
          month: "2-digit",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        }),
        estado: "completado",
      });
      setGenerando(false);
      paginacion.irA(1);
      mostrar("Reporte generado correctamente.");
    }, 900);
  };

  const descargar = (reporte: Reporte) => {
    const filas = registros
      .filter((r) => sede === "todas" || r.sede === sede)
      .map((r) => [r.trabajador, r.documento, r.sede, r.entrada, r.estado, r.dispositivo, r.fecha]);
    if (filas.length === 0) {
      mostrar("No hay datos para descargar en el rango seleccionado.", "error");
      return;
    }
    descargarExcel(
      reporte.tipo.toLowerCase().replace(/\s+/g, "-"),
      ["Trabajador", "Documento", "Sede", "Entrada", "Estado", "Dispositivo", "Fecha"],
      filas,
    );
    mostrar("Descarga iniciada.");
  };

  return (
    <>
      {/* ------------------------------------------------------ Métricas - */}
      <div className="stat-grid">
        <StatCard
          icono={<FolderIcon size={26} />}
          color="yellow"
          etiqueta="Total reportes"
          valor={metricas.total}
          pista="En el periodo"
        />
        <StatCard
          icono={<FileCheckIcon size={26} />}
          color="yellow"
          etiqueta="Reportes completados"
          valor={metricas.completados}
          pista={`${porcentaje(metricas.completados, metricas.total)} del total`}
        />
        <StatCard
          icono={<LoaderIcon size={26} />}
          color="pink"
          etiqueta="En procesamiento"
          valor={metricas.procesando}
          pista={`${porcentaje(metricas.procesando, metricas.total)} del total`}
        />
        <StatCard
          icono={<FileXIcon size={26} />}
          color="pink"
          etiqueta="Con errores"
          valor={metricas.error}
          pista={`${porcentaje(metricas.error, metricas.total)} del total`}
        />
      </div>

      {/* ------------------------------------------- Generador de reportes */}
      <Card>
        <div className="filters">
          <DateRangeField etiqueta="Rango de fechas" rango={rango} alCambiar={setRango} />
          <SelectField
            etiqueta="Tipo de reporte"
            valor={tipo}
            alCambiar={setTipo}
            opciones={
              tipos.length > 0
                ? tipos
                : [{ valor: "", etiqueta: "Sin tipos configurados" }]
            }
          />
          <SelectField
            etiqueta="Sede"
            valor={sede}
            alCambiar={setSede}
            opciones={[
              { valor: "todas", etiqueta: "Todas las sedes" },
              ...sedes.map((s) => ({ valor: s.nombre, etiqueta: s.nombre })),
            ]}
          />
          <button
            type="button"
            className="btn btn--primary"
            onClick={generar}
            disabled={generando || tipos.length === 0}
          >
            {generando ? <span className="spinner" /> : <FilePlusIcon size={20} />}
            {generando ? "Generando…" : "Generar reporte"}
          </button>
        </div>
      </Card>

      {/* ------------------------------------------ Reportes generados --- */}
      <Card>
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Reporte</th>
                <th>Rango de fechas</th>
                <th>Tipo</th>
                <th>Generado por</th>
                <th>Fecha/Hora</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {paginacion.visibles.length === 0 ? (
                <EmptyRow columnas={7} mensaje="Todavía no se han generado reportes." />
              ) : (
                paginacion.visibles.map((reporte) => (
                  <tr key={reporte.id}>
                    <td>{reporte.nombre}</td>
                    <td>{reporte.rango}</td>
                    <td>{reporte.tipo}</td>
                    <td>{reporte.generadoPor}</td>
                    <td>{reporte.fechaHora}</td>
                    <td>
                      <Badge tono={TONO_ESTADO[reporte.estado]}>{ETIQUETA_ESTADO[reporte.estado]}</Badge>
                    </td>
                    <td>
                      <div className="table__actions">
                        <button
                          type="button"
                          className="btn btn--icon"
                          aria-label={`Descargar ${reporte.nombre}`}
                          disabled={reporte.estado !== "completado"}
                          onClick={() => descargar(reporte)}
                        >
                          <DownloadIcon size={19} />
                        </button>
                        <button
                          type="button"
                          className="btn btn--icon"
                          aria-label={`Eliminar ${reporte.nombre}`}
                          onClick={() => setAEliminar(reporte)}
                        >
                          <TrashIcon size={19} />
                        </button>
                      </div>
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
          info={`Mostrando ${paginacion.desde} a ${paginacion.hasta} de ${paginacion.total} reportes`}
          irA={paginacion.irA}
        />
      </Card>

      <ConfirmDialog
        abierto={aEliminar !== null}
        titulo="Eliminar reporte"
        mensaje={`Se eliminará el reporte "${aEliminar?.nombre ?? ""}" del historial.`}
        alCerrar={() => setAEliminar(null)}
        alConfirmar={() => {
          if (aEliminar) {
            eliminarReporte(aEliminar.id);
            mostrar("Reporte eliminado.");
          }
          setAEliminar(null);
        }}
      />
    </>
  );
}
