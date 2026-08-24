import { useState } from "react";
import { Card, ConfirmDialog, Switch, TextField } from "../components/ui";
import { KeyIcon, PowerIcon, SaveIcon } from "../components/ui/Icons";
import { useDatos } from "../context/DataProvider";
import { MODULOS_PERMISOS } from "../data/initial";
import { useToast } from "../context/ToastProvider";
import { ROLES } from "./UsuariosPage";
import type { SesionActiva } from "../types/admin";

const MODULOS = MODULOS_PERMISOS;

/**
 * Permisos iniciales. El súper administrador conserva acceso total porque es
 * el rol que administra esta misma pantalla; el resto llegará de la API.
 */
const PERMISOS_INICIALES: Record<string, string[]> = {
  SUPER_ADMIN: MODULOS,
  ADMIN: [],
  SUPERVISOR: [],
  AUDITOR: [],
  OPERADOR: [],
};

export function SeguridadPage() {
  const { sesiones, cerrarSesionRemota } = useDatos();
  const { mostrar } = useToast();

  const [actual, setActual] = useState("");
  const [nueva, setNueva] = useState("");
  const [confirmar, setConfirmar] = useState("");

  const [dobleFactor, setDobleFactor] = useState(false);
  const [expirarSesion, setExpirarSesion] = useState(true);
  const [bloqueoIntentos, setBloqueoIntentos] = useState(true);

  const [permisos, setPermisos] = useState<Record<string, string[]>>(PERMISOS_INICIALES);
  const [aCerrar, setACerrar] = useState<SesionActiva | null>(null);

  const cambiarClave = () => {
    if (nueva.length < 8) {
      mostrar("La contraseña nueva debe tener al menos 8 caracteres.", "error");
      return;
    }
    if (nueva !== confirmar) {
      mostrar("Las contraseñas no coinciden.", "error");
      return;
    }
    setActual("");
    setNueva("");
    setConfirmar("");
    mostrar("Contraseña actualizada.");
  };

  const alternarPermiso = (rol: string, modulo: string) => {
    setPermisos((previos) => {
      const actuales = previos[rol] ?? [];
      const nuevos = actuales.includes(modulo)
        ? actuales.filter((m) => m !== modulo)
        : [...actuales, modulo];
      return { ...previos, [rol]: nuevos };
    });
  };

  return (
    <>
      {/* --------------------------------------------- Cambio de contraseña */}
      <Card>
        <h2 className="card__title" style={{ marginBottom: 18 }}>
          Cambiar contraseña
        </h2>
        <div className="settings-grid">
          <TextField etiqueta="Contraseña actual" tipo="password" valor={actual} alCambiar={setActual} />
          <TextField etiqueta="Contraseña nueva" tipo="password" valor={nueva} alCambiar={setNueva} />
          <TextField
            etiqueta="Confirmar contraseña nueva"
            tipo="password"
            valor={confirmar}
            alCambiar={setConfirmar}
          />
        </div>
        <p style={{ marginTop: 12, fontSize: 13.5, color: "var(--fp-text-muted)" }}>
          Usa al menos 8 caracteres, combinando mayúsculas, minúsculas y números.
        </p>
        <div style={{ marginTop: 20, display: "flex", justifyContent: "flex-end" }}>
          <button type="button" className="btn btn--primary" onClick={cambiarClave}>
            <KeyIcon size={19} /> Actualizar contraseña
          </button>
        </div>
      </Card>

      {/* -------------------------------------------- Políticas de acceso - */}
      <Card>
        <h2 className="card__title" style={{ marginBottom: 8 }}>
          Políticas de acceso
        </h2>
        <div className="setting-row">
          <div>
            <p className="setting-row__label">Verificación en dos pasos</p>
            <p className="setting-row__hint">
              Solicita un código enviado por correo cada vez que se inicia sesión desde un equipo nuevo.
            </p>
          </div>
          <Switch marcado={dobleFactor} etiqueta="Verificación en dos pasos" alCambiar={setDobleFactor} />
        </div>
        <div className="setting-row">
          <div>
            <p className="setting-row__label">Cerrar sesión por inactividad</p>
            <p className="setting-row__hint">La sesión termina automáticamente tras 30 minutos sin actividad.</p>
          </div>
          <Switch marcado={expirarSesion} etiqueta="Cerrar sesión por inactividad" alCambiar={setExpirarSesion} />
        </div>
        <div className="setting-row">
          <div>
            <p className="setting-row__label">Bloquear tras intentos fallidos</p>
            <p className="setting-row__hint">
              La cuenta se bloquea 15 minutos después de 5 intentos de acceso incorrectos.
            </p>
          </div>
          <Switch
            marcado={bloqueoIntentos}
            etiqueta="Bloquear tras intentos fallidos"
            alCambiar={setBloqueoIntentos}
          />
        </div>
      </Card>

      {/* --------------------------------------------- Sesiones activas --- */}
      <Card>
        <h2 className="card__title" style={{ marginBottom: 18 }}>
          Sesiones activas
        </h2>
        <div className="security-list">
          {sesiones.length === 0 ? (
            <p style={{ color: "var(--fp-text-muted)", fontSize: 15 }}>No hay otras sesiones abiertas.</p>
          ) : (
            sesiones.map((sesion) => (
              <div key={sesion.id} className="session-item">
                <div>
                  <p className="setting-row__label">
                    {sesion.usuario}
                    {sesion.actual ? " · esta sesión" : ""}
                  </p>
                  <p className="session-item__meta">
                    {sesion.dispositivo} · {sesion.ip} · {sesion.inicio}
                  </p>
                </div>
                <button
                  type="button"
                  className="btn btn--ghost"
                  disabled={sesion.actual}
                  onClick={() => setACerrar(sesion)}
                >
                  <PowerIcon size={18} /> Cerrar sesión
                </button>
              </div>
            ))
          )}
        </div>
      </Card>

      {/* ------------------------------------------- Permisos por rol ----- */}
      <Card>
        <div className="card__head">
          <h2 className="card__title">Permisos por rol</h2>
          <button type="button" className="btn btn--primary" onClick={() => mostrar("Permisos guardados.")}>
            <SaveIcon size={19} /> Guardar permisos
          </button>
        </div>

        <div className="table-wrap">
          <table className="table role-matrix">
            <thead>
              <tr>
                <th>Módulo</th>
                {ROLES.map((rol) => (
                  <th key={rol.valor} style={{ textAlign: "center" }}>
                    {rol.etiqueta}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {MODULOS.map((modulo) => (
                <tr key={modulo}>
                  <td>{modulo}</td>
                  {ROLES.map((rol) => (
                    <td key={rol.valor} style={{ textAlign: "center" }}>
                      <input
                        type="checkbox"
                        checked={(permisos[rol.valor] ?? []).includes(modulo)}
                        onChange={() => alternarPermiso(rol.valor, modulo)}
                        aria-label={`${rol.etiqueta} puede acceder a ${modulo}`}
                        disabled={rol.valor === "SUPER_ADMIN"}
                      />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <ConfirmDialog
        abierto={aCerrar !== null}
        titulo="Cerrar sesión remota"
        mensaje={`Se cerrará la sesión de ${aCerrar?.usuario ?? ""} en ${aCerrar?.dispositivo ?? ""}.`}
        textoConfirmar="Cerrar sesión"
        alCerrar={() => setACerrar(null)}
        alConfirmar={() => {
          if (aCerrar) {
            cerrarSesionRemota(aCerrar.id);
            mostrar("Sesión cerrada.");
          }
          setACerrar(null);
        }}
      />
    </>
  );
}
