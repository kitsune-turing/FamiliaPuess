import { useMemo, useState } from "react";
import { Badge, Card, ConfirmDialog, EmptyRow, SearchInput, StatCard, Switch } from "../../components/ui";
import {
  LockIcon,
  ParameterIcon,
  RefreshIcon,
  SaveIcon,
  SlidersIcon,
} from "../../components/ui/Icons";
import { useDatos } from "../../context/DataProvider";
import { useToast } from "../../context/ToastProvider";
import { coincide } from "../../lib/format";
import type { Parametro } from "../../types/admin";

export function ParametrosPage() {
  const { parametros, guardarParametro, restablecerParametros } = useDatos();
  const { mostrar } = useToast();

  const [busqueda, setBusqueda] = useState("");
  const [grupoActivo, setGrupoActivo] = useState("todos");
  const [borrador, setBorrador] = useState<Record<string, string>>({});
  const [confirmarReset, setConfirmarReset] = useState(false);

  const grupos = useMemo(
    () => Array.from(new Set(parametros.map((p) => p.grupo))),
    [parametros],
  );

  const filtrados = useMemo(
    () =>
      parametros.filter((parametro) => {
        const porGrupo = grupoActivo === "todos" || parametro.grupo === grupoActivo;
        const porTexto =
          coincide(parametro.nombre, busqueda) ||
          coincide(parametro.clave, busqueda) ||
          coincide(parametro.descripcion, busqueda);
        return porGrupo && porTexto;
      }),
    [parametros, grupoActivo, busqueda],
  );

  /** Valor mostrado: el del borrador si se editó, o el guardado. */
  const valorDe = (parametro: Parametro) => borrador[parametro.id] ?? parametro.valor;

  const cambiosPendientes = Object.keys(borrador).length;

  const editar = (parametro: Parametro, valor: string) => {
    setBorrador((previo) => {
      // Si el valor vuelve al original, deja de contar como cambio pendiente.
      if (valor === parametro.valor) {
        const copia = { ...previo };
        delete copia[parametro.id];
        return copia;
      }
      return { ...previo, [parametro.id]: valor };
    });
  };

  const guardarTodo = () => {
    if (cambiosPendientes === 0) {
      mostrar("No hay cambios por guardar.", "info");
      return;
    }
    parametros
      .filter((p) => borrador[p.id] !== undefined)
      .forEach((p) => guardarParametro({ ...p, valor: borrador[p.id] as string }));
    setBorrador({});
    mostrar(`${cambiosPendientes} parámetro(s) guardado(s).`);
  };

  return (
    <>
      <div className="page-actions">
        <button type="button" className="btn btn--ghost" onClick={() => setConfirmarReset(true)}>
          <RefreshIcon size={20} /> Restablecer
        </button>
        <button type="button" className="btn btn--primary" onClick={guardarTodo} disabled={cambiosPendientes === 0}>
          <SaveIcon size={19} />
          {cambiosPendientes > 0 ? `Guardar (${cambiosPendientes})` : "Guardar cambios"}
        </button>
      </div>

      <div className="stat-grid">
        <StatCard
          icono={<ParameterIcon size={26} />}
          color="yellow"
          etiqueta="Parámetros totales"
          valor={parametros.length}
          pista="En el sistema"
        />
        <StatCard
          icono={<SlidersIcon size={26} />}
          color="yellow"
          etiqueta="Grupos de configuración"
          valor={grupos.length}
          pista="Categorías disponibles"
        />
        <StatCard
          icono={<LockIcon size={26} />}
          color="pink"
          etiqueta="Solo lectura"
          valor={parametros.filter((p) => !p.editable).length}
          pista="No editables desde el panel"
        />
        <StatCard
          icono={<SaveIcon size={26} />}
          color="pink"
          etiqueta="Cambios sin guardar"
          valor={cambiosPendientes}
          pista={cambiosPendientes > 0 ? "Pendientes de aplicar" : "Todo guardado"}
        />
      </div>

      <div className="settings-tabs" role="tablist" aria-label="Grupos de parámetros">
        <button
          type="button"
          role="tab"
          aria-selected={grupoActivo === "todos"}
          className={`settings-tab ${grupoActivo === "todos" ? "settings-tab--active" : ""}`.trim()}
          onClick={() => setGrupoActivo("todos")}
        >
          Todos
        </button>
        {grupos.map((grupo) => (
          <button
            key={grupo}
            type="button"
            role="tab"
            aria-selected={grupoActivo === grupo}
            className={`settings-tab ${grupoActivo === grupo ? "settings-tab--active" : ""}`.trim()}
            onClick={() => setGrupoActivo(grupo)}
          >
            {grupo}
          </button>
        ))}
      </div>

      <Card>
        <div className="card__head">
          <h2 className="card__title">Parámetros del sistema</h2>
          <div style={{ flex: "0 1 320px", display: "flex" }}>
            <SearchInput valor={busqueda} alCambiar={setBusqueda} placeholder="Buscar parámetro" />
          </div>
        </div>

        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Parámetro</th>
                <th>Clave</th>
                <th>Grupo</th>
                <th style={{ width: 240 }}>Valor</th>
              </tr>
            </thead>
            <tbody>
              {filtrados.length === 0 ? (
                <EmptyRow columnas={4} mensaje={
                    parametros.length === 0
                      ? "Aún no hay parámetros configurados."
                      : "No hay parámetros que coincidan con la búsqueda."
                  } />
              ) : (
                filtrados.map((parametro) => (
                  <tr key={parametro.id}>
                    <td>
                      <p style={{ color: "var(--fp-text)" }}>{parametro.nombre}</p>
                      <p className="setting-row__hint" style={{ marginTop: 2 }}>
                        {parametro.descripcion}
                      </p>
                    </td>
                    <td style={{ fontFamily: "ui-monospace, monospace", fontSize: 13.5 }}>
                      {parametro.clave}
                    </td>
                    <td>
                      <Badge tono="grey">{parametro.grupo}</Badge>
                    </td>
                    <td>
                      {!parametro.editable ? (
                        <span
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: 8,
                            color: "var(--fp-text-muted)",
                          }}
                        >
                          <LockIcon size={16} />
                          {parametro.valor}
                        </span>
                      ) : parametro.tipo === "booleano" ? (
                        <Switch
                          marcado={valorDe(parametro) === "true"}
                          etiqueta={parametro.nombre}
                          alCambiar={(v) => editar(parametro, v ? "true" : "false")}
                        />
                      ) : (
                        <input
                          className="input"
                          style={{ height: 42 }}
                          type={
                            parametro.tipo === "numero"
                              ? "number"
                              : parametro.tipo === "hora"
                                ? "time"
                                : "text"
                          }
                          value={valorDe(parametro)}
                          aria-label={parametro.nombre}
                          onChange={(e) => editar(parametro, e.target.value)}
                        />
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <ConfirmDialog
        abierto={confirmarReset}
        titulo="Restablecer parámetros"
        mensaje="Todos los parámetros volverán a sus valores de fábrica. Los cambios sin guardar también se descartan."
        textoConfirmar="Restablecer"
        alCerrar={() => setConfirmarReset(false)}
        alConfirmar={() => {
          restablecerParametros();
          setBorrador({});
          setConfirmarReset(false);
          mostrar("Parámetros restablecidos.");
        }}
      />
    </>
  );
}
