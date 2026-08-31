import { useEffect, useState } from "react";
import { Card, ConfirmDialog, Switch, TextField } from "../../components/ui";
import { KeyIcon, PowerIcon, SaveIcon, ShieldIcon } from "../../components/ui/Icons";
import { useDatos } from "../../context/DataProvider";
import { MODULOS_PERMISOS, clavePermiso } from "../../data/initial";
import { useToast } from "../../context/ToastProvider";
import { useNavigate } from "react-router-dom";
import type { SesionActiva } from "../../types/admin";

const MODULOS = MODULOS_PERMISOS;

/**
 * Resumen de acceso por módulo. El detalle fino (ver, crear, editar, eliminar)
 * se administra en la pantalla de Roles y permisos; aquí solo se concede o se
 * retira el acceso completo a un módulo.
 */
function accesosPorModulo(permisos: string[]): string[] {
  return MODULOS.filter((modulo) => permisos.some((p) => p.startsWith(`${modulo}:`)));
}

export function SeguridadPage() {
  const { sesiones, cerrarSesionRemota, roles, guardarRol } = useDatos();
  const { mostrar } = useToast();
  const navegar = useNavigate();

  const [actual, setActual] = useState("");
  const [nueva, setNueva] = useState("");
  const [confirmar, setConfirmar] = useState("");

  const [dobleFactor, setDobleFactor] = useState(false);
  const [expirarSesion, setExpirarSesion] = useState(true);
  const [bloqueoIntentos, setBloqueoIntentos] = useState(true);

  // Borrador de la matriz: se confirma con "Guardar permisos".
  const [permisos, setPermisos] = useState<Record<string, string[]>>({});
  const [aCerrar, setACerrar] = useState<SesionActiva | null>(null);

  // Sincroniza el borrador cada vez que cambian los roles del sistema.
  useEffect(() => {
    setPermisos(
      Object.fromEntries(roles.map((rol) => [rol.codigo, accesosPorModulo(rol.permisos)])),
    );
  }, [roles]);

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

  const guardarPermisos = () => {
    for (const rol of roles) {
      const modulosPermitidos = permisos[rol.codigo] ?? [];
      // Conserva el detalle fino de los módulos que siguen habilitados y
      // concede "ver" a los que se acaban de activar.
      const conservados = rol.permisos.filter((p) =>
        modulosPermitidos.some((modulo) => p.startsWith(`${modulo}:`)),
      );
      const nuevos = modulosPermitidos
        .filter((modulo) => !rol.permisos.some((p) => p.startsWith(`${modulo}:`)))
        .map((modulo) => clavePermiso(modulo, "ver"));
      guardarRol({ ...rol, permisos: [...conservados, ...nuevos] });
    }
    mostrar("Permisos guardados.");
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
          <div className="table__actions">
            <button type="button" className="btn btn--ghost" onClick={() => navegar("/panel/roles")}>
              <ShieldIcon size={19} /> Administrar roles
            </button>
            <button type="button" className="btn btn--primary" onClick={guardarPermisos}>
              <SaveIcon size={19} /> Guardar permisos
            </button>
          </div>
        </div>

        <p className="setting-row__hint" style={{ marginBottom: 14 }}>
          Marca el acceso general a cada módulo. Para definir qué puede crear, editar o eliminar cada
          rol, abre la pantalla de Roles y permisos.
        </p>

        <div className="table-wrap">
          <table className="table role-matrix">
            <thead>
              <tr>
                <th>Módulo</th>
                {roles.map((rol) => (
                  <th key={rol.id} style={{ textAlign: "center" }}>
                    {rol.nombre}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {MODULOS.map((modulo) => (
                <tr key={modulo}>
                  <td>{modulo}</td>
                  {roles.map((rol) => (
                    <td key={rol.id} style={{ textAlign: "center" }}>
                      <input
                        type="checkbox"
                        checked={(permisos[rol.codigo] ?? []).includes(modulo)}
                        onChange={() => alternarPermiso(rol.codigo, modulo)}
                        aria-label={`${rol.nombre} puede acceder a ${modulo}`}
                        disabled={rol.codigo === "SUPER_ADMIN"}
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
