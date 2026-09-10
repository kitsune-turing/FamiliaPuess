import { useCallback, useEffect, useState } from "react";
import { Card, SelectField, StatCard, Switch, TextField } from "../../components/ui";
import { ClockIcon, MapPinIcon, MonitorIcon, SaveIcon, UsersIcon } from "../../components/ui/Icons";
import { useDatos } from "../../context/DataProvider";
import { useToast } from "../../context/ToastProvider";
import { guardarConfigGeneral, obtenerConfigGeneral } from "../../services/adminApi";

export function ConfiguracionPage() {
  const { sedes, trabajadores, dispositivos } = useDatos();
  const { mostrar } = useToast();

  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);

  const [nombreEmpresa, setNombreEmpresa] = useState("");
  const [nit, setNit] = useState("");
  const [zonaHoraria, setZonaHoraria] = useState("America/Bogota");
  const [idioma, setIdioma] = useState("es-CO");
  const [toleranciaMin, setToleranciaMin] = useState("");
  const [duracionQr, setDuracionQr] = useState("");
  const [exigirCodigo, setExigirCodigo] = useState(false);

  const cargar = useCallback(async () => {
    try {
      const v = await obtenerConfigGeneral();
      setNombreEmpresa(v.NOMBRE_EMPRESA ?? "");
      setNit(v.NIT ?? "");
      setZonaHoraria(v.ZONA_HORARIA ?? "America/Bogota");
      setIdioma(v.IDIOMA ?? "es-CO");
      setToleranciaMin(v.TOLERANCIA_MIN ?? "");
      setDuracionQr(v.QR_EXPIRACION_SEG ?? "");
      setExigirCodigo(v.EXIGIR_CODIGO === "true");
    } catch {
      mostrar("No se pudo cargar la configuración.", "error");
    } finally {
      setCargando(false);
    }
  }, [mostrar]);

  useEffect(() => {
    cargar();
  }, [cargar]);

  const guardar = async () => {
    setGuardando(true);
    try {
      await guardarConfigGeneral({
        NOMBRE_EMPRESA: nombreEmpresa,
        NIT: nit,
        ZONA_HORARIA: zonaHoraria,
        IDIOMA: idioma,
        TOLERANCIA_MIN: toleranciaMin,
        QR_EXPIRACION_SEG: duracionQr,
        EXIGIR_CODIGO: exigirCodigo ? "true" : "false",
      });
      mostrar("Configuración guardada.");
    } catch {
      mostrar("Error al guardar la configuración.", "error");
    } finally {
      setGuardando(false);
    }
  };

  if (cargando) {
    return <p style={{ padding: 24 }}>Cargando configuración…</p>;
  }

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
          etiqueta="Tolerancia"
          valor={toleranciaMin ? `${toleranciaMin} min` : "—"}
          pista="Para registro de entrada"
        />
      </div>

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
      </Card>

      <Card>
        <h2 className="card__title" style={{ marginBottom: 18 }}>
          Registro de entrada
        </h2>
        <p className="setting-row__hint" style={{ marginBottom: 16 }}>
          Estas opciones aplican tanto a la web como a la aplicación Desktop. Los horarios de entrada se
          configuran desde la sección de Horarios (pueden existir múltiples horarios).
        </p>
        <div className="settings-grid">
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
              <p className="setting-row__label">Exigir código alfanumérico</p>
              <p className="setting-row__hint">
                Además del documento, el trabajador debe escribir su código personal al registrarse
                (aplica en web y en la aplicación Desktop).
              </p>
            </div>
            <Switch marcado={exigirCodigo} etiqueta="Exigir código alfanumérico" alCambiar={setExigirCodigo} />
          </div>
        </div>
      </Card>

      <div style={{ marginTop: 22, display: "flex", justifyContent: "flex-end" }}>
        <button type="button" className="btn btn--primary" onClick={guardar} disabled={guardando}>
          <SaveIcon size={19} /> {guardando ? "Guardando…" : "Guardar cambios"}
        </button>
      </div>
    </>
  );
}
