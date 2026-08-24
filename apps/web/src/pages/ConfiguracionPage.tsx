import { useState } from "react";
import { Card, SelectField, StatCard, Switch, TextField } from "../components/ui";
import { ClockIcon, MapPinIcon, MonitorIcon, SaveIcon, UsersIcon } from "../components/ui/Icons";
import { useAuth } from "../contexts/AuthContext";
import { useDatos } from "../context/DataProvider";
import { useToast } from "../context/ToastProvider";

type Pestana = "general" | "asistencia" | "notificaciones" | "perfil";

const PESTANAS: { valor: Pestana; etiqueta: string }[] = [
  { valor: "general", etiqueta: "General" },
  { valor: "asistencia", etiqueta: "Asistencia" },
  { valor: "notificaciones", etiqueta: "Notificaciones" },
  { valor: "perfil", etiqueta: "Mi perfil" },
];

export function ConfiguracionPage() {
  const { user } = useAuth();
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

  // ---- Notificaciones
  const [avisoTarde, setAvisoTarde] = useState(false);
  const [avisoDispositivo, setAvisoDispositivo] = useState(false);
  const [resumenDiario, setResumenDiario] = useState(false);
  const [correoAvisos, setCorreoAvisos] = useState("");

  // ---- Perfil
  const [nombrePerfil, setNombrePerfil] = useState(user?.nombre ?? "");
  const [correoPerfil, setCorreoPerfil] = useState(user?.username ?? "");

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

      {pestana === "notificaciones" ? (
        <Card>
          <h2 className="card__title" style={{ marginBottom: 18 }}>
            Avisos del sistema
          </h2>
          <TextField
            etiqueta="Correo para avisos"
            tipo="email"
            valor={correoAvisos}
            alCambiar={setCorreoAvisos}
          />
          <div style={{ marginTop: 12 }}>
            <div className="setting-row">
              <div>
                <p className="setting-row__label">Avisar entradas tarde</p>
                <p className="setting-row__hint">Envía un correo cuando alguien registra fuera de la tolerancia.</p>
              </div>
              <Switch marcado={avisoTarde} etiqueta="Avisar entradas tarde" alCambiar={setAvisoTarde} />
            </div>
            <div className="setting-row">
              <div>
                <p className="setting-row__label">Avisar dispositivos sin conexión</p>
                <p className="setting-row__hint">
                  Notifica cuando un dispositivo lleva más de 30 minutos sin reportarse.
                </p>
              </div>
              <Switch
                marcado={avisoDispositivo}
                etiqueta="Avisar dispositivos sin conexión"
                alCambiar={setAvisoDispositivo}
              />
            </div>
            <div className="setting-row">
              <div>
                <p className="setting-row__label">Resumen diario</p>
                <p className="setting-row__hint">Envía un consolidado de asistencia al cerrar la jornada.</p>
              </div>
              <Switch marcado={resumenDiario} etiqueta="Resumen diario" alCambiar={setResumenDiario} />
            </div>
          </div>
          <div style={{ marginTop: 22, display: "flex", justifyContent: "flex-end" }}>
            <button type="button" className="btn btn--primary" onClick={guardar}>
              <SaveIcon size={19} /> Guardar cambios
            </button>
          </div>
        </Card>
      ) : null}

      {pestana === "perfil" ? (
        <Card>
          <h2 className="card__title" style={{ marginBottom: 18 }}>
            Mi perfil
          </h2>
          <div className="settings-grid">
            <TextField etiqueta="Nombre" valor={nombrePerfil} alCambiar={setNombrePerfil} />
            <TextField etiqueta="Correo electrónico" tipo="email" valor={correoPerfil} alCambiar={setCorreoPerfil} />
          </div>
          <p style={{ marginTop: 14, fontSize: 14, color: "var(--fp-text-muted)" }}>
            Rol asignado: {user?.rol_nombre ?? "Sin rol"}
          </p>
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
