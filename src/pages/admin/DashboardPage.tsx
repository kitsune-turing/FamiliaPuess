import { useCallback, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { DonutChart } from "../../components/charts/DonutChart";
import { LineChart } from "../../components/charts/LineChart";
import { BadgeOutline, Card, EmptyRow, StatCard } from "../../components/ui";
import {
  CalendarIcon,
  CheckIcon,
  ChevronDownIcon,
  DoorIcon,
  DoorLateIcon,
  MapPinIcon,
  MonitorIcon,
  FileIcon,
  PlusIcon,
  UsersIcon,
} from "../../components/ui/Icons";
import { useAuth } from "../../context/AuthProvider";
import { useDatos } from "../../context/DataProvider";
import { SEGMENTOS_ASISTENCIA } from "../../data/initial";
import { useClickFuera } from "../../hooks";
import { porcentaje } from "../../lib/format";

const PERIODOS = [
  { valor: "hoy", etiqueta: "Hoy" },
  { valor: "semana", etiqueta: "Esta semana" },
  { valor: "mes", etiqueta: "Este mes" },
];

/** Etiqueta legible de cada estado de registro. */
const ETIQUETA_ESTADO: Record<string, string> = {
  a_tiempo: "A tiempo",
  tarde: "Tarde",
  ausente: "Ausente",
  sin_registrar: "Sin registrar",
};

/** Selector compacto de periodo usado en las dos gráficas. */
function PeriodSelect({ valor, alCambiar }: { valor: string; alCambiar: (valor: string) => void }) {
  const [abierto, setAbierto] = useState(false);
  const cerrar = useCallback(() => setAbierto(false), []);
  const ref = useClickFuera<HTMLDivElement>(abierto, cerrar);
  const actual = PERIODOS.find((p) => p.valor === valor);

  return (
    <div className="period-select" ref={ref}>
      <button
        type="button"
        className="period-select__trigger"
        aria-haspopup="listbox"
        aria-expanded={abierto}
        aria-label="Periodo"
        onClick={() => setAbierto((a) => !a)}
      >
        <CalendarIcon size={22} />
        <span>{actual?.etiqueta ?? "Periodo"}</span>
        <ChevronDownIcon
          size={20}
          className={`select__chevron--inline ${abierto ? "select__chevron--open" : ""}`.trim()}
        />
      </button>

      {abierto ? (
        <ul className="select__menu select__menu--derecha" role="listbox">
          {PERIODOS.map((periodo) => (
            <li
              key={periodo.valor}
              role="option"
              aria-selected={periodo.valor === valor}
              className={`select__option ${periodo.valor === valor ? "select__option--activa" : ""}`.trim()}
              onClick={() => {
                alCambiar(periodo.valor);
                setAbierto(false);
              }}
            >
              <span>{periodo.etiqueta}</span>
              {periodo.valor === valor ? <CheckIcon size={18} /> : null}
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}

export function DashboardPage() {
  const navegar = useNavigate();
  const { sedeActiva } = useAuth();
  const { trabajadores, dispositivos, registros } = useDatos();

  const [periodoResumen, setPeriodoResumen] = useState("hoy");
  const [periodoEntradas, setPeriodoEntradas] = useState("hoy");

  const registrosSede = useMemo(
    () => (sedeActiva === "Todas las sedes" ? registros : registros.filter((r) => r.sede === sedeActiva)),
    [registros, sedeActiva],
  );

  const entradasPorHora = useMemo(() => {
    const conteo: Record<string, number> = {};
    for (const r of registrosSede) {
      const hora = r.entrada?.split(":")[0];
      if (hora) conteo[hora] = (conteo[hora] ?? 0) + 1;
    }
    return Object.entries(conteo)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([h, v]) => ({ etiqueta: `${h}:00`, valor: v }));
  }, [registrosSede]);

  const metricas = useMemo(() => {
    const activos = trabajadores.filter((t) => t.activo).length;
    const entradasHoy = registrosSede.filter(
      (r) => r.estado === "a_tiempo" || r.estado === "tarde",
    ).length;
    const tarde = registrosSede.filter((r) => r.estado === "tarde").length;
    const dispositivosActivos = dispositivos.filter((d) => d.activo).length;
    return {
      activos,
      totalTrabajadores: trabajadores.length,
      entradasHoy,
      tarde,
      dispositivosActivos,
      totalDispositivos: dispositivos.length,
    };
  }, [trabajadores, registrosSede, dispositivos]);

  const resumen = useMemo(() => {
    // La clave del segmento se corresponde con el estado del registro.
    const equivalente: Record<string, string> = { ausentes: "ausente" };
    return SEGMENTOS_ASISTENCIA.map((segmento) => ({
      clave: segmento.clave,
      etiqueta: segmento.etiqueta,
      color: segmento.color,
      valor: registrosSede.filter((r) => r.estado === (equivalente[segmento.clave] ?? segmento.clave))
        .length,
    }));
  }, [registrosSede]);

  const totalResumen = resumen.reduce((suma, s) => suma + s.valor, 0);
  const recientes = registrosSede.slice(0, 5);

  return (
    <>
      {/* -------------------------------------------------------- Métricas */}
      <div className="stat-grid">
        <StatCard
          icono={<UsersIcon size={26} />}
          color="pink"
          etiqueta="Trabajadores activos"
          valor={metricas.activos}
          pista={`${porcentaje(metricas.activos, metricas.totalTrabajadores)} del total`}
        />
        <StatCard
          icono={<DoorIcon size={26} />}
          color="yellow"
          etiqueta="Entradas hoy"
          valor={metricas.entradasHoy}
          pista={`${porcentaje(metricas.entradasHoy, registrosSede.length)} del total`}
        />
        <StatCard
          icono={<DoorLateIcon size={26} />}
          color="pink"
          etiqueta="Entradas tarde"
          valor={metricas.tarde}
          pista={`${porcentaje(metricas.tarde, registrosSede.length)} del total`}
        />
        <StatCard
          icono={<MonitorIcon size={26} />}
          color="pink"
          etiqueta="Dispositivos activos"
          valor={metricas.dispositivosActivos}
          pista={`${porcentaje(metricas.dispositivosActivos, metricas.totalDispositivos)} del total`}
        />
      </div>

      {/* ----------------------------------------- Gráficas y accesos ---- */}
      <div className="dash-row">
        <Card className="chart-card">
          <div className="chart-card__head">
            <h2 className="card__title">Resumen asistencia hoy</h2>
            <PeriodSelect valor={periodoResumen} alCambiar={setPeriodoResumen} />
          </div>

          <div className="donut-layout">
            <DonutChart segmentos={resumen} />
            <ul className="donut-legend">
              {resumen.map((segmento) => (
                <li key={segmento.clave} className="donut-legend__row">
                  <span className="donut-legend__swatch" style={{ background: segmento.color }} />
                  <span className="donut-legend__label">{segmento.etiqueta}</span>
                  <span className="donut-legend__value">
                    {segmento.valor} ({porcentaje(segmento.valor, totalResumen, 0)})
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </Card>

        <Card className="chart-card">
          <div className="chart-card__head">
            <h2 className="card__title">Entradas por hora</h2>
            <PeriodSelect valor={periodoEntradas} alCambiar={setPeriodoEntradas} />
          </div>
          <LineChart serie={entradasPorHora} />
        </Card>

        <Card className="chart-card">
          <h2 className="card__title" style={{ marginBottom: 16 }}>
            Acciones rápidas
          </h2>
          <div className="quick-actions">
            <button
              type="button"
              className="btn btn--primary btn--block"
              onClick={() => navegar("/panel/trabajadores?nuevo=1")}
            >
              <PlusIcon size={20} /> Registrar trabajador
            </button>
            <button type="button" className="btn btn--soft" onClick={() => navegar("/panel/reportes")}>
              <FileIcon size={20} /> Generar reporte
            </button>
            <button
              type="button"
              className="btn btn--soft"
              onClick={() => navegar("/panel/dispositivos?nuevo=1")}
            >
              <MonitorIcon size={20} /> Agregar dispositivo
            </button>
            <button type="button" className="btn btn--soft" onClick={() => navegar("/panel/sedes")}>
              <MapPinIcon size={20} /> Configurar sede
            </button>
          </div>
        </Card>
      </div>

      {/* ------------------------------------ Registros recientes ---- */}
      <Card>
        <h2 className="card__title" style={{ marginBottom: 8 }}>
          Registros recientes
        </h2>
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
              {recientes.length === 0 ? (
                <EmptyRow columnas={6} mensaje="Aún no hay registros de entrada." />
              ) : (
                recientes.map((registro) => (
                  <tr key={registro.id}>
                    <td>{registro.trabajador}</td>
                    <td>{registro.documento}</td>
                    <td>{registro.sede}</td>
                    <td>{registro.entrada}</td>
                    <td>
                      <BadgeOutline
                        tono={
                          registro.estado === "a_tiempo"
                            ? "neutral"
                            : registro.estado === "tarde"
                              ? "yellow"
                              : "pink"
                        }
                      >
                        {ETIQUETA_ESTADO[registro.estado] ?? registro.estado}
                      </BadgeOutline>
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
      </Card>
    </>
  );
}
