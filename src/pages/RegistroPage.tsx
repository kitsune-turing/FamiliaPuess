import { type FormEvent, useCallback, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { registrarAsistencia, validarToken } from "../services/adminApi";
import marcaImg from "../assets/images/marca.png";
import mazorcaImg from "../assets/images/mazorca.png";
import mapPinIcon from "../assets/icons/map-pin.png";
import idCardIcon from "../assets/icons/id-card.svg";
import keyIcon from "../assets/icons/key.png";
import arrowIcon from "../assets/icons/arrow-right.svg";
import "../styles/registro.css";

type PageState =
  | { kind: "loading" }
  | { kind: "invalid"; message: string }
  | { kind: "form"; token: string; sedeNombre: string; exigirCodigo: boolean }
  | { kind: "submitting"; token: string; sedeNombre: string; exigirCodigo: boolean }
  | { kind: "success"; empleadoNombre: string; sedeNombre: string; registradoEn: string }
  | { kind: "error"; message: string; token: string; sedeNombre: string; exigirCodigo: boolean };

function MazorcaDecorations() {
  return (
    <>
      <img src={mazorcaImg} alt="" className="mazorca mazorca--top-left" />
      <img src={mazorcaImg} alt="" className="mazorca mazorca--bottom-left" />
      <img src={mazorcaImg} alt="" className="mazorca mazorca--top-right" />
      <img src={mazorcaImg} alt="" className="mazorca mazorca--bottom-right" />
    </>
  );
}

export function RegistroPage() {
  const [searchParams] = useSearchParams();
  const [state, setState] = useState<PageState>({ kind: "loading" });
  const [documento, setDocumento] = useState("");
  const [codigoAlfa, setCodigoAlfa] = useState("");

  useEffect(() => {
    const token = searchParams.get("token");
    if (!token) {
      setState({
        kind: "invalid",
        message: "El acceso al registro de asistencia unicamente puede realizarse mediante el escaneo del codigo QR.",
      });
      return;
    }

    let cancelled = false;
    validarToken(token)
      .then((result) => {
        if (!cancelled) {
          setState({ kind: "form", token: result.token, sedeNombre: result.sede_nombre, exigirCodigo: result.exigir_codigo ?? true });
        }
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setState({ kind: "invalid", message: err.message });
        }
      });

    return () => { cancelled = true; };
  }, [searchParams]);

  const handleSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();
      if (state.kind !== "form" && state.kind !== "error") return;

      const { token, sedeNombre, exigirCodigo } = state;
      setState({ kind: "submitting", token, sedeNombre, exigirCodigo });

      registrarAsistencia({ token, documento, ...(exigirCodigo ? { codigo_alfa: codigoAlfa } : {}) })
        .then((result) => {
          setState({
            kind: "success",
            empleadoNombre: result.empleado_nombre,
            sedeNombre: result.sede_nombre,
            registradoEn: new Date(result.registrado_en).toLocaleTimeString("es-CO", {
              hour: "2-digit",
              minute: "2-digit",
            }),
          });
        })
        .catch((err: Error) => {
          setState({ kind: "error", message: err.message, token, sedeNombre, exigirCodigo });
        });
    },
    [state, documento, codigoAlfa],
  );

  if (state.kind === "loading") {
    return (
      <div className="registro-page">
        <MazorcaDecorations />
        <div className="registro-loading">
          <div className="registro-loading__spinner" />
          <p className="registro-loading__text">Validando codigo QR...</p>
        </div>
      </div>
    );
  }

  if (state.kind === "invalid") {
    return (
      <div className="registro-page">
        <MazorcaDecorations />
        <div className="registro-message registro-message--error">
          <div className="registro-message__icon">&#9888;</div>
          <h2 className="registro-message__title">Acceso no disponible</h2>
          <p className="registro-message__text">{state.message}</p>
          <p className="registro-message__text" style={{ marginTop: 12 }}>
            Escanee nuevamente el codigo QR para continuar.
          </p>
        </div>
      </div>
    );
  }

  if (state.kind === "success") {
    return (
      <div className="registro-page">
        <MazorcaDecorations />
        <div className="registro-message registro-message--error registro-message--success">
          <div className="registro-message__icon">&#10004;</div>
          <h2 className="registro-message__title">Asistencia registrada</h2>
          <p className="registro-message__text">
            {state.empleadoNombre}, su asistencia ha sido registrada
            correctamente a las {state.registradoEn} en {state.sedeNombre}.
          </p>
        </div>
      </div>
    );
  }

  const formSede = state.sedeNombre;
  const exigirCodigo = state.exigirCodigo;
  const isSubmitting = state.kind === "submitting";

  return (
    <div className="registro-page">
      <MazorcaDecorations />
      <div className="registro-card">
        <img src={marcaImg} alt="Familia Puess" className="registro-marca" />

        <div className="registro-sede">
          <img src={mapPinIcon} alt="" className="registro-sede__icon" />
          <span className="registro-sede__text">{formSede}</span>
        </div>

        <form className="registro-form" onSubmit={handleSubmit}>
          <div className="field-group">
            <label className="field-group__label" htmlFor="documento">
              Documento de identidad
            </label>
            <div className="field-group__input-wrapper">
              <img src={idCardIcon} alt="" className="field-group__icon" />
              <input
                id="documento"
                className="field-group__input"
                type="text"
                inputMode="numeric"
                pattern="[0-9A-Za-z\-]{4,30}"
                maxLength={30}
                minLength={4}
                placeholder="1234567819"
                value={documento}
                onChange={(e) => setDocumento(e.target.value.replace(/[^0-9A-Za-z-]/g, ""))}
                required
                disabled={isSubmitting}
                autoComplete="off"
              />
            </div>
          </div>

          {exigirCodigo && (
            <div className="field-group">
              <label className="field-group__label" htmlFor="codigo">
                Codigo alfanumerico
              </label>
              <div className="field-group__input-wrapper">
                <img src={keyIcon} alt="" className="field-group__icon field-group__icon--muted" />
                <input
                  id="codigo"
                  className="field-group__input"
                  type="text"
                  pattern="[A-Z0-9]{4,10}"
                  maxLength={10}
                  minLength={4}
                  placeholder="7K2P9A"
                  value={codigoAlfa}
                  onChange={(e) => setCodigoAlfa(e.target.value.replace(/[^A-Za-z0-9]/g, "").toUpperCase())}
                  required
                  disabled={isSubmitting}
                  autoComplete="off"
                />
              </div>
            </div>
          )}

          {state.kind === "error" && (
            <p className="registro-message__text" style={{ color: "#d32f2f", textAlign: "center" }}>
              {state.message}
            </p>
          )}

          <button
            type="submit"
            className="registro-submit"
            disabled={isSubmitting || !documento.trim() || (exigirCodigo && !codigoAlfa.trim())}
          >
            <img src={arrowIcon} alt="" className="registro-submit__icon" />
            <span className="registro-submit__text">Registrar asistencia</span>
          </button>
        </form>
      </div>
    </div>
  );
}
