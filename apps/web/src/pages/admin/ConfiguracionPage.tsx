import { useState } from "react";
import { Card, SelectField, StatCard, Switch, TextField } from "../../components/ui";
import { ClockIcon, MapPinIcon, MonitorIcon, SaveIcon, UsersIcon } from "../../components/ui/Icons";
import { useDatos } from "../../context/DataProvider";
import { useToast } from "../../context/ToastProvider";

type Pestana = "general" | "asistencia" | "desktop";

const PESTANAS: { valor: Pestana; etiqueta: string }[] = [
  { valor: "general", etiqueta: "General" },
  { valor: "asistencia", etiqueta: "Asistencia" },
  { valor: "desktop", etiqueta: "Aplicación Desktop" },
];

export function ConfiguracionPage() {
  const { sedes, trabajadores, dispositivos } = useDatos();
  const { mostrar } = useToast();

  const [pestana, setPestana] = useState<Pestana>("general");

  // ---- General
  const [nombreEmpresa, setNombreEmpresa] = useState("");
  const [nit, setNit] = useState("");
  const [zonaHoraria, setZonaHoraria] = useState("America/Bogota");
  const [idioma, setIdioma] = useState("es-CO");

  // ---- Asistencia
  const [horaEntrada, setHoraEntrada] = useState("");
  const [toleranciaMin, setToleranciaMin] = useState("");
  const [duracionQr, setDuracionQr] = useState("");
  const [permitirSalida, setPermitirSalida] = useState(false);
  const [bloquearDuplicados, setBloquearDuplicados] = useState(false);
  const [exigirCodigo, setExigirCodigo] = useState(false);

  // ---- Desktop
  const [modoKiosco, setModoKiosco] = useState(false);
  const [inicioAutomatico, setInicioAutomatico] = useState(false);
  const [intervaloQr, setIntervaloQr] = useState("30");
  const [mostrarReloj, setMostrarReloj] = useState(true);

  const guardar = () => mostrar("Configuración guardada.");

  return (
    <>
      <div className="stat-grid">
        <StatCard
          icono={<MapPinIcon size={26} />}
          color="yellow"
          etiqueta="Sedes configuradas"
          valor={sedes.length}
          pista="En total"
        />
        <StatCard
          icono={<UsersIcon size={26} />}
          color="yellow"
          etiqueta="Trabajadores"
          valor={trabajadores.length}
          pista="En total"
        />
        <StatCard
          icono={<MonitorIcon size={26} />}
          color="pink"
          etiqueta="Dispositivos"
          valor={dispositivos.length}
          pista="En total"
        />
        <StatCard
          icono={<ClockIcon size={26} />}
          color="pink"
          etiqueta="Hora de entrada"
          valor={horaEntrada || "—"}
          pista={toleranciaMin ? `Tolerancia de ${toleranciaMin} min` : "Sin configurar"}
        />
      </div>

      <div className="settings-tabs" role="tablist" aria-label="Secciones de configuración">
        {PESTANAS.map((item) => (
          <button
            key={item.valor}
            type="button"
            role="tab"
            aria-selected={pestana === item.valor}
            className={`settings-tab ${pestana === item.valor ? "settings-tab--active" : ""}`.trim()}
            onClick={() => setPestana(item.valor)}
          >
            {item.etiqueta}
          </button>
        ))}
      </div>

      {pestana === "general" ? (
        <Card>
          <h2 className="card__title" style={{ marginBottom: 18 }}>
            Datos de la organización
          </h2>
          <div className="settings-grid">
            <TextField etiqueta="Nombre de la empresa" valor={nombreEmpresa} alCambiar={setNombreEmpresa} />
            <TextField etiqueta="NIT" valor={nit} alCambiar={setNit} />
            <SelectField
              etiqueta="Zona horaria"
              valor={zonaHoraria}
              alCambiar={setZonaHoraria}
              opciones={[
                { valor: "America/Bogota", etiqueta: "América/Bogotá (GMT-5)" },
                { valor: "America/Mexico_City", etiqueta: "América/Ciudad de México (GMT-6)" },
                { valor: "America/Lima", etiqueta: "América/Lima (GMT-5)" },
              ]}
            />
            <SelectField
              etiqueta="Idioma"
              valor={idioma}
              alCambiar={setIdioma}
              opciones={[
                { valor: "es-CO", etiqueta: "Español (Colombia)" },
                { valor: "es-MX", etiqueta: "Español (México)" },
                { valor: "en-US", etiqueta: "Inglés (Estados Unidos)" },
              ]}
            />
          </div>
          <div style={{ marginTop: 22, display: "flex", justifyContent: "flex-end" }}>
            <button type="button" className="btn btn--primary" onClick={guardar}>
              <SaveIcon size={19} /> Guardar cambios
            </button>
          </div>
        </Card>
      ) : null}

      {pestana === "asistencia" ? (
        <Card>
          <h2 className="card__title" style={{ marginBottom: 18 }}>
            Reglas de asistencia
          </h2>
          <div className="settings-grid">
            <TextField etiqueta="Hora de entrada" tipo="time" valor={horaEntrada || "—"} alCambiar={setHoraEntrada} />
            <TextField
              etiqueta="Tolerancia (minutos)"
              tipo="number"
              valor={toleranciaMin}
              alCambiar={setToleranciaMin}
            />
            <TextField
              etiqueta="Vigencia del código QR (segundos)"
              tipo="number"
              valor={duracionQr}
              alCambiar={setDuracionQr}
            />
          </div>

          <div style={{ marginTop: 12 }}>
            <div className="setting-row">
              <div>
                <p className="setting-row__label">Registrar hora de salida</p>
                <p className="setting-row__hint">
                  Habilita un segundo escaneo al final del turno para calcular horas trabajadas.
                </p>
              </div>
              <Switch marcado={permitirSalida} etiqueta="Registrar hora de salida" alCambiar={setPermitirSalida} />
            </div>
            <div className="setting-row">
              <div>
                <p className="setting-row__label">Bloquear registros duplicados</p>
                <p className="setting-row__hint">
                  Impide que un trabajador registre entrada dos veces en la misma jornada.
                </p>
              </div>
              <Switch
                marcado={bloquearDuplicados}
                etiqueta="Bloquear registros duplicados"
                alCambiar={setBloquearDuplicados}
              />
            </div>
            <div className="setting-row">
              <div>
                <p className="setting-row__label">Exigir código alfanumérico</p>
                <p className="setting-row__hint">
                  Además del documento, el trabajador debe escribir su código personal al registrarse.
                </p>
              </div>
              <Switch marcado={exigirCodigo} etiqueta="Exigir código alfanumérico" alCambiar={setExigirCodigo} />
            </div>
          </div>

          <div style={{ marginTop: 22, display: "flex", justifyContent: "flex-end" }}>
            <button type="button" className="btn btn--primary" onClick={guardar}>
              <SaveIcon size={19} /> Guardar cambios
            </button>
          </div>
        </Card>
      ) : null}

      {pestana === "desktop" ? (
        <Card>
          <h2 className="card__title" style={{ marginBottom: 18 }}>
            Aplicación Desktop
          </h2>
          <p className="setting-row__hint" style={{ marginBottom: 16 }}>
            Configura el comportamiento de la aplicación instalada en cada computador de registro.
          </p>
          <div className="settings-grid">
            <TextField
              etiqueta="Intervalo de renovación QR (segundos)"
              tipo="number"
              valor={intervaloQr}
              alCambiar={setIntervaloQr}
            />
          </div>
          <div style={{ marginTop: 12 }}>
            <div className="setting-row">
              <div>
                <p className="setting-row__label">Modo kiosco</p>
                <p className="setting-row__hint">
                  Bloquea la pantalla para que solo se pueda usar la aplicación de registro.
                </p>
              </div>
              <Switch marcado={modoKiosco} etiqueta="Modo kiosco" alCambiar={setModoKiosco} />
            </div>
            <div className="setting-row">
              <div>
                <p className="setting-row__label">Inicio automático</p>
                <p className="setting-row__hint">
                  La aplicación se abre automáticamente al encender el computador.
                </p>
              </div>
              <Switch marcado={inicioAutomatico} etiqueta="Inicio automático" alCambiar={setInicioAutomatico} />
            </div>
            <div className="setting-row">
              <div>
                <p className="setting-row__label">Mostrar reloj en pantalla</p>
                <p className="setting-row__hint">
                  Muestra la hora actual en la pantalla de registro.
                </p>
              </div>
              <Switch marcado={mostrarReloj} etiqueta="Mostrar reloj" alCambiar={setMostrarReloj} />
            </div>
          </div>
          <div style={{ marginTop: 22, display: "flex", justifyContent: "flex-end" }}>
            <button type="button" className="btn btn--primary" onClick={guardar}>
              <SaveIcon size={19} /> Guardar cambios
            </button>
          </div>
        </Card>
      ) : null}

    </>
  );
}
