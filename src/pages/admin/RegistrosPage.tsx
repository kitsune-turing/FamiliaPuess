import { useMemo, useState } from "react";
import {
  BadgeOutline,
  Card,
  DateRangeField,
  EmptyRow,
  Pagination,
  SearchInput,
  SelectField,
  StatCard,
  type RangoFechas,
} from "../../components/ui";
import {
  ClockIcon,
  DoorIcon,
  DoorLateIcon,
  DownloadIcon,
  RefreshIcon,
  UserXIcon,
} from "../../components/ui/Icons";
import { useAuth } from "../../context/AuthProvider";
import { useDatos } from "../../context/DataProvider";
import { useToast } from "../../context/ToastProvider";
import { usePaginacion } from "../../hooks";
import { coincide, descargarExcel, porcentaje } from "../../lib/format";
import type { EstadoRegistro } from "../../types/admin";

const POR_PAGINA = 10;

const ETIQUETA: Record<EstadoRegistro, string> = {
  a_tiempo: "A tiempo",
  tarde: "Tarde",
  ausente: "Ausente",
  sin_registrar: "Sin registrar",
};

const TONO: Record<EstadoRegistro, "neutral" | "yellow" | "pink" | "green"> = {
  a_tiempo: "neutral",
  tarde: "yellow",
  ausente: "pink",
  sin_registrar: "neutral",
};

export function RegistrosPage() {
  const { registros, sedes, dispositivos } = useDatos();
  const { sedeActiva } = useAuth();
  const { mostrar } = useToast();

  const [busqueda, setBusqueda] = useState("");
  const [rango, setRango] = useState<RangoFechas>(() => {
    const hoy = new Date();
    const hace30 = new Date(hoy);
    hace30.setDate(hace30.getDate() - 30);
    return {
      desde: hace30.toISOString().slice(0, 10),
      hasta: hoy.toISOString().slice(0, 10),
    };
  });
  const [filtroSede, setFiltroSede] = useState("todas");
  const [filtroEstado, setFiltroEstado] = useState("todos");
  const [filtroDispositivo, setFiltroDispositivo] = useState("todos");

  const filtrados = useMemo(
    () =>
      registros.filter((registro) => {
        const porSedeGlobal = sedeActiva === "Todas las sedes" || registro.sede === sedeActiva;
        const porTexto =
          coincide(registro.trabajador, busqueda) || coincide(registro.documento, busqueda);
        const porSede = filtroSede === "todas" || registro.sede === filtroSede;
        const porEstado = filtroEstado === "todos" || registro.estado === filtroEstado;
        const porDispositivo =
          filtroDispositivo === "todos" || registro.dispositivo === filtroDispositivo;
        const porFecha = registro.fecha >= rango.desde && registro.fecha <= rango.hasta;
        return porSedeGlobal && porTexto && porSede && porEstado && porDispositivo && porFecha;
      }),
    [registros, sedeActiva, busqueda, filtroSede, filtroEstado, filtroDispositivo, rango],
  );

  const metricas = useMemo(() => {
    const total = filtrados.length;
    return {
      total,
      aTiempo: filtrados.filter((r) => r.estado === "a_tiempo").length,
      tarde: filtrados.filter((r) => r.estado === "tarde").length,
      ausentes: filtrados.filter((r) => r.estado === "ausente").length,
    };
  }, [filtrados]);

  const paginacion = usePaginacion(filtrados, POR_PAGINA);

  const limpiarFiltros = () => {
    setBusqueda("");
    setFiltroSede("todas");
    setFiltroEstado("todos");
    setFiltroDispositivo("todos");
    mostrar("Filtros restablecidos.", "info");
  };

  const exportar = () => {
    descargarExcel(
      "registros-de-entrada",
      ["Trabajador", "Documento", "Sede", "Entrada", "Estado", "Dispositivo", "Fecha"],
      filtrados.map((r) => [
        r.trabajador,
        r.documento,
        r.sede,
        r.entrada,
        ETIQUETA[r.estado],
        r.dispositivo,
        r.fecha,
      ]),
    );
    mostrar("Registros exportados en Excel.");
  };

  const codigosDispositivo = Array.from(new Set(dispositivos.map((d) => d.nombre)));

  return (
    <>
      <div className="stat-grid">
        <StatCard
          icono={<ClockIcon size={26} />}
          color="pink"
          etiqueta="Registros del periodo"
          valor={metricas.total}
          pista="En el rango seleccionado"
        />
        <StatCard
          icono={<DoorIcon size={26} />}
          color="yellow"
          etiqueta="Entradas a tiempo"
          valor={metricas.aTiempo}
          pista={`${porcentaje(metricas.aTiempo, metricas.total)} del total`}
        />
        <StatCard
          icono={<DoorLateIcon size={26} />}
          color="yellow"
          etiqueta="Entradas tarde"
          valor={metricas.tarde}
          pista={`${porcentaje(metricas.tarde, metricas.total)} del total`}
        />
        <StatCard
          icono={<UserXIcon size={26} />}
          color="pink"
          etiqueta="Ausencias"
          valor={metricas.ausentes}
          pista={`${porcentaje(metricas.ausentes, metricas.total)} del total`}
        />
      </div>

      <Card>
        <div className="filters">
          <SearchInput valor={busqueda} alCambiar={setBusqueda} placeholder="Buscar por nombre o documento" />
          <DateRangeField etiqueta="Rango de fechas" rango={rango} alCambiar={setRango} />
          <SelectField
            etiqueta="Sede"
            valor={filtroSede}
            alCambiar={setFiltroSede}
            opciones={[
              { valor: "todas", etiqueta: "Todas las sedes" },
              ...sedes.map((s) => ({ valor: s.nombre, etiqueta: s.nombre })),
            ]}
          />
          <SelectField
            etiqueta="Estado"
            valor={filtroEstado}
            alCambiar={setFiltroEstado}
            opciones={[
              { valor: "todos", etiqueta: "Todos los estados" },
              { valor: "a_tiempo", etiqueta: "A tiempo" },
              { valor: "tarde", etiqueta: "Tarde" },
              { valor: "ausente", etiqueta: "Ausente" },
              { valor: "sin_registrar", etiqueta: "Sin registrar" },
            ]}
          />
          <SelectField
            etiqueta="Dispositivo"
            valor={filtroDispositivo}
            alCambiar={setFiltroDispositivo}
            opciones={[
              { valor: "todos", etiqueta: "Todos los dispositivos" },
              ...codigosDispositivo.map((c) => ({ valor: c, etiqueta: c })),
            ]}
          />
          <div className="filters__actions">
            <button type="button" className="btn btn--ghost" onClick={limpiarFiltros}>
              <RefreshIcon size={20} /> Limpiar filtros
            </button>
            <button type="button" className="btn btn--primary" onClick={exportar}>
              <DownloadIcon size={19} /> Exportar
            </button>
          </div>
        </div>
      </Card>

      <Card>
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Trabajador</th>
                <th>Documento</th>
                <th>Sede</th>
                <th>Entrada</th>
                <th>Estado</th>
                <th>Dispositivo</th>
              </tr>
            </thead>
            <tbody>
              {paginacion.visibles.length === 0 ? (
                <EmptyRow columnas={6} mensaje={
                  registros.length === 0
                    ? "Aún no hay registros de entrada."
                    : "No hay registros en el periodo seleccionado."
                } />
              ) : (
                paginacion.visibles.map((registro) => (
                  <tr key={registro.id}>
                    <td>{registro.trabajador}</td>
                    <td>{registro.documento}</td>
                    <td>{registro.sede}</td>
                    <td>{registro.entrada}</td>
                    <td>
                      <BadgeOutline tono={TONO[registro.estado]}>{ETIQUETA[registro.estado]}</BadgeOutline>
                    </td>
                    <td>
                      <span className="cell-device">
                        <span className="dot" />
                        {registro.dispositivo}
                      </span>
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
