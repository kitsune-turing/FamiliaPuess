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
} from "../components/ui";
import {
  CursorClickIcon,
  DownloadIcon,
  GridIcon,
  ListChecksIcon,
  RefreshIcon,
  UserCheckIcon,
} from "../components/ui/Icons";
import { useDatos } from "../context/DataProvider";
import { useToast } from "../context/ToastProvider";
import { ACCIONES_AUDITORIA, MODULOS_AUDITORIA } from "../data/initial";
import { usePaginacion } from "../hooks";
import { descargarArchivo, generarCsv, numero } from "../lib/format";
import type { AccionAuditoria, ModuloAuditoria } from "../types/admin";

const POR_PAGINA = 6;

const TONO_MODULO: Record<ModuloAuditoria, "pink" | "orange" | "purple" | "green" | "yellow" | "grey"> = {
  Trabajadores: "pink",
  Seguridad: "orange",
  Sedes: "purple",
  Dispositivos: "green",
  Reportes: "yellow",
  Usuarios: "grey",
};

const TONO_ACCION: Record<AccionAuditoria, "green" | "purple" | "pink" | "grey"> = {
  Crear: "green",
  Actualizar: "purple",
  Eliminar: "pink",
  Consultar: "grey",
};

export function AuditoriaPage() {
  const { auditorias, usuarios } = useDatos();
  const { mostrar } = useToast();

  const [rango, setRango] = useState<RangoFechas>({ desde: "2026-05-01", hasta: "2026-05-12" });
  const [filtroUsuario, setFiltroUsuario] = useState("todos");
  const [filtroModulo, setFiltroModulo] = useState("todos");
  const [filtroAccion, setFiltroAccion] = useState("todas");

  const filtradas = useMemo(
    () =>
      auditorias.filter((entrada) => {
        const porUsuario = filtroUsuario === "todos" || entrada.usuario === filtroUsuario;
        const porModulo = filtroModulo === "todos" || entrada.modulo === filtroModulo;
        const porAccion = filtroAccion === "todas" || entrada.accion === filtroAccion;
        return porUsuario && porModulo && porAccion;
      }),
    [auditorias, filtroUsuario, filtroModulo, filtroAccion],
  );

  const metricas = useMemo(
    () => ({
      total: filtradas.length,
      usuarios: new Set(filtradas.map((a) => a.usuario)).size,
      modulos: new Set(filtradas.map((a) => a.modulo)).size,
      acciones: new Set(filtradas.map((a) => a.accion)).size,
    }),
    [filtradas],
  );

  const paginacion = usePaginacion(filtradas, POR_PAGINA);

  const limpiarFiltros = () => {
    setFiltroUsuario("todos");
    setFiltroModulo("todos");
    setFiltroAccion("todas");
    mostrar("Filtros restablecidos.", "info");
  };

  const exportar = () => {
    const csv = generarCsv(
      ["Fecha / Hora", "Usuario", "Módulo", "Acción", "Detalle", "IP", "Dispositivo"],
      filtradas.map((a) => [a.fechaHora, a.usuario, a.modulo, a.accion, a.detalle, a.ip, a.dispositivo]),
    );
    descargarArchivo("auditoria.csv", csv);
    mostrar("Historial exportado en CSV.");
  };

  const nombresUsuario = Array.from(new Set(usuarios.map((u) => u.nombre)));

  return (
    <>
      {/* ------------------------------------------------------- Filtros - */}
      <Card>
        <div className="filters">
          <DateRangeField etiqueta="Rango de fechas" rango={rango} alCambiar={setRango} />
          <SelectField
            etiqueta="Usuario"
            valor={filtroUsuario}
            alCambiar={setFiltroUsuario}
            opciones={[
              { valor: "todos", etiqueta: "Todos los usuarios" },
              ...nombresUsuario.map((n) => ({ valor: n, etiqueta: n })),
            ]}
          />
          <SelectField
            etiqueta="Módulo"
            valor={filtroModulo}
            alCambiar={setFiltroModulo}
            opciones={[
              { valor: "todos", etiqueta: "Todos los módulos" },
              ...MODULOS_AUDITORIA.map((m) => ({ valor: m, etiqueta: m })),
            ]}
          />
          <SelectField
            etiqueta="Acción"
            valor={filtroAccion}
            alCambiar={setFiltroAccion}
            opciones={[
              { valor: "todas", etiqueta: "Todas las acciones" },
              ...ACCIONES_AUDITORIA.map((a) => ({ valor: a, etiqueta: a })),
            ]}
          />
          <button type="button" className="btn btn--ghost" onClick={limpiarFiltros}>
            <RefreshIcon size={20} /> Limpiar filtros
          </button>
        </div>
      </Card>

      {/* ------------------------------------------------------ Métricas - */}
      <div className="stat-grid">
        <StatCard
          icono={<ListChecksIcon size={26} />}
          color="yellow"
          etiqueta="Total actividades"
          valor={numero(metricas.total)}
          pista="En el periodo seleccionado"
        />
        <StatCard
          icono={<UserCheckIcon size={26} />}
          color="yellow"
          etiqueta="Usuarios únicos"
          valor={metricas.usuarios}
          pista="En el periodo seleccionado"
        />
        <StatCard
          icono={<GridIcon size={26} />}
          color="yellow"
          etiqueta="Módulos utilizados"
          valor={metricas.modulos}
          pista="En el periodo seleccionado"
        />
        <StatCard
          icono={<CursorClickIcon size={26} />}
          color="yellow"
          etiqueta="Acciones realizadas"
          valor={metricas.acciones}
          pista="Tipos diferentes"
        />
      </div>

      {/* -------------------------------------------- Historial de acciones */}
      <Card>
        <div className="card__head">
          <h2 className="card__title">Historial de actividades</h2>
          <button type="button" className="btn btn--ghost" onClick={exportar}>
            <DownloadIcon size={19} /> Exportar
          </button>
        </div>

        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Fecha / Hora</th>
                <th>Usuario</th>
                <th>Módulo</th>
                <th>Acción</th>
                <th>Detalle</th>
                <th>IP</th>
                <th>Dispositivo</th>
              </tr>
            </thead>
            <tbody>
              {paginacion.visibles.length === 0 ? (
                <EmptyRow columnas={7} mensaje={
                  auditorias.length === 0
                    ? "Aún no hay actividad registrada en el sistema."
                    : "No hay actividades que coincidan con los filtros."
                } />
              ) : (
                paginacion.visibles.map((entrada) => (
                  <tr key={entrada.id}>
                    <td>{entrada.fechaHora}</td>
                    <td>{entrada.usuario}</td>
                    <td>
                      <Badge tono={TONO_MODULO[entrada.modulo]}>{entrada.modulo}</Badge>
                    </td>
                    <td>
                      <Badge tono={TONO_ACCION[entrada.accion]}>{entrada.accion}</Badge>
                    </td>
                    <td style={{ maxWidth: 280 }}>{entrada.detalle}</td>
                    <td>{entrada.ip}</td>
                    <td>{entrada.dispositivo}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <Pagination
          pagina={paginacion.pagina}
          totalPaginas={paginacion.totalPaginas}
          info={`Mostrando ${paginacion.desde} a ${paginacion.hasta} de ${paginacion.total} actividades`}
          irA={paginacion.irA}
        />
      </Card>
    </>
  );
}
