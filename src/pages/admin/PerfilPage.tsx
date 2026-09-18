/* ==========================================================================
   Mi perfil.

   Muestra los datos de la persona que tiene la sesión abierta y permite
   editarlos. Los cambios se guardan en `AuthProvider`, por lo que la barra
   superior (nombre y foto) se actualiza de inmediato.
   ========================================================================== */

import { useMemo, useRef, useState } from "react";
import {
  Badge,
  Card,
  SelectField,
  TextAreaField,
  TextField,
} from "../../components/ui";
import {
  CameraIcon,
  EditIcon,
  KeyIcon,
  MailIcon,
  MapPinIcon,
  PhoneIcon,
  SaveIcon,
  ShieldIcon,
  TrashIcon,
  XIcon,
} from "../../components/ui/Icons";
import { useAuth } from "../../context/AuthProvider";
import { useDatos } from "../../context/DataProvider";
import { useToast } from "../../context/ToastProvider";
import { MODULOS_PERMISOS } from "../../data/initial";
import { fechaHoraActual, iniciales } from "../../lib/format";
import type { Perfil } from "../../types/admin";

const ZONAS = [
  { valor: "America/Bogota", etiqueta: "Bogotá (GMT-5)" },
  { valor: "America/Mexico_City", etiqueta: "Ciudad de México (GMT-6)" },
  { valor: "America/Lima", etiqueta: "Lima (GMT-5)" },
  { valor: "America/Santiago", etiqueta: "Santiago (GMT-4)" },
];

const IDIOMAS = [
  { valor: "es-CO", etiqueta: "Español (Colombia)" },
  { valor: "es-MX", etiqueta: "Español (México)" },
  { valor: "en-US", etiqueta: "Inglés" },
];

const TAMANO_MAXIMO = 1024 * 1024; // 1 MB

export function PerfilPage() {
  const { usuario, perfil, actualizarPerfil } = useAuth();
  const { sedes, roles, registrarAuditoria } = useDatos();
  const { mostrar } = useToast();

  const [editando, setEditando] = useState(false);
  const [borrador, setBorrador] = useState<Perfil | null>(null);
  const [errores, setErrores] = useState<Record<string, string>>({});

  const [claveActual, setClaveActual] = useState("");
  const [claveNueva, setClaveNueva] = useState("");
  const [claveConfirmar, setClaveConfirmar] = useState("");


  const refArchivo = useRef<HTMLInputElement>(null);

  /** Rol completo de la persona: da el color de la etiqueta y sus permisos. */
  const rol = useMemo(
    () => roles.find((r) => r.codigo === usuario?.rolCodigo),
    [roles, usuario],
  );

  /** Módulos a los que el rol tiene acceso, para el resumen lateral. */
  const modulosDelRol = useMemo(() => {
    if (!rol) return [];
    return MODULOS_PERMISOS.filter((modulo) =>
      rol.permisos.some((permiso) => permiso.startsWith(`${modulo}:`)),
    );
  }, [rol]);

  if (!perfil) {
    return (
      <Card>
        <p className="empty-note">No hay una sesión activa.</p>
      </Card>
    );
  }

  const datos = borrador ?? perfil;

  const auditar = (detalle: string) => {
    registrarAuditoria({
      id: `aud-${Date.now()}`,
      fechaHora: fechaHoraActual(),
      usuario: perfil.nombre,
      modulo: "Perfil",
      accion: "Actualizar",
      detalle,
      ip: "—",
      dispositivo: "Panel web",
    });
  };

  const empezarEdicion = () => {
    setBorrador({ ...perfil });
    setErrores({});
    setEditando(true);
  };

  const cancelar = () => {
    setBorrador(null);
    setErrores({});
    setEditando(false);
  };

  const cambiar = (campo: keyof Perfil, valor: string | boolean) => {
    setBorrador({ ...datos, [campo]: valor } as Perfil);
  };

  const validar = (valores: Perfil) => {
    const nuevos: Record<string, string> = {};
    if (!valores.nombre.trim()) nuevos.nombre = "Escribe tu nombre completo.";
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(valores.correo)) {
      nuevos.correo = "Escribe un correo electrónico válido.";
    }
    if (valores.telefono.trim() && !/^[\d\s+()-]{7,20}$/.test(valores.telefono.trim())) {
      nuevos.telefono = "El teléfono solo admite números y separadores.";
    }
    return nuevos;
  };

  const guardar = () => {
    if (!borrador) return;
    const nuevos = validar(borrador);
    setErrores(nuevos);
    if (Object.keys(nuevos).length > 0) {
      mostrar("Revisa los campos marcados en rojo.", "error");
      return;
    }
    actualizarPerfil(borrador);
    auditar("Actualizó la información de su perfil");
    setBorrador(null);
    setEditando(false);
    mostrar("Perfil actualizado.");
  };

  /* ------------------------------------------------------- Foto de perfil */

  const elegirFoto = (archivo: File | undefined) => {
    if (!archivo) return;
    if (!archivo.type.startsWith("image/")) {
      mostrar("El archivo debe ser una imagen.", "error");
      return;
    }
    if (archivo.size > TAMANO_MAXIMO) {
      mostrar("La imagen no puede pesar más de 1 MB.", "error");
      return;
    }
    const lector = new FileReader();
    lector.onload = () => {
      const dataUrl = String(lector.result);
      if (editando) cambiar("avatar", dataUrl);
      else {
        actualizarPerfil({ avatar: dataUrl });
        auditar("Cambió su foto de perfil");
      }
      mostrar("Foto actualizada.");
    };
    lector.onerror = () => mostrar("No se pudo leer la imagen.", "error");
    lector.readAsDataURL(archivo);
  };

  const quitarFoto = () => {
    if (editando) cambiar("avatar", "");
    else actualizarPerfil({ avatar: "" });
    mostrar("Foto eliminada.");
  };

  /* ----------------------------------------------------------- Contraseña */

  const cambiarClave = () => {
    if (!claveActual) {
      mostrar("Escribe tu contraseña actual.", "error");
      return;
    }
    if (claveNueva.length < 8) {
      mostrar("La contraseña nueva debe tener al menos 8 caracteres.", "error");
      return;
    }
    if (claveNueva === claveActual) {
      mostrar("La contraseña nueva debe ser distinta de la actual.", "error");
      return;
    }
    if (claveNueva !== claveConfirmar) {
      mostrar("Las contraseñas no coinciden.", "error");
      return;
    }
    setClaveActual("");
    setClaveNueva("");
    setClaveConfirmar("");
    auditar("Cambió su contraseña");
    mostrar("Contraseña actualizada.");
  };

  return (
    <div className="perfil-layout">
      {/* =============================================== Columna izquierda */}
      <div className="perfil-col">
        <Card className="perfil-hero">
          <div className="perfil-hero__cover" />

          <div className="perfil-hero__avatar-wrap">
            {datos.avatar ? (
              <img className="perfil-hero__avatar" src={datos.avatar} alt={datos.nombre} />
            ) : (
              <span className="perfil-hero__avatar perfil-hero__avatar--iniciales">
                {iniciales(datos.nombre || "FP")}
              </span>
            )}
            <button
              type="button"
              className="perfil-hero__camera"
              onClick={() => refArchivo.current?.click()}
              aria-label="Cambiar foto de perfil"
            >
              <CameraIcon size={18} />
            </button>
            <input
              ref={refArchivo}
              type="file"
              accept="image/*"
              className="perfil-hero__file"
              onChange={(e) => {
                elegirFoto(e.target.files?.[0]);
                e.target.value = "";
              }}
            />
          </div>

          <h2 className="perfil-hero__name">{datos.nombre || "Sin nombre"}</h2>
          <p className="perfil-hero__mail">{datos.correo}</p>

          <div className="perfil-hero__badges">
            <Badge tono={rol?.tono ?? "grey"}>{rol?.nombre ?? usuario?.rolNombre ?? "Sin rol"}</Badge>
            <Badge tono="green">Cuenta activa</Badge>
          </div>

          {datos.avatar ? (
            <button type="button" className="btn btn--ghost btn--block" onClick={quitarFoto}>
              <TrashIcon size={18} /> Quitar foto
            </button>
          ) : (
            <button
              type="button"
              className="btn btn--ghost btn--block"
              onClick={() => refArchivo.current?.click()}
            >
              <CameraIcon size={18} /> Subir foto
            </button>
          )}
        </Card>

        <Card>
          <h2 className="card__title" style={{ marginBottom: 14 }}>
            Datos de la cuenta
          </h2>
          <ul className="perfil-meta">
            <li className="perfil-meta__row">
              <MailIcon size={19} />
              <div>
                <p className="perfil-meta__label">Correo</p>
                <p className="perfil-meta__value">{datos.correo || "—"}</p>
              </div>
            </li>
            <li className="perfil-meta__row">
              <PhoneIcon size={19} />
              <div>
                <p className="perfil-meta__label">Teléfono</p>
                <p className="perfil-meta__value">{datos.telefono || "Sin registrar"}</p>
              </div>
            </li>
            <li className="perfil-meta__row">
              <MapPinIcon size={19} />
              <div>
                <p className="perfil-meta__label">Sede asignada</p>
                <p className="perfil-meta__value">{datos.sede || "Todas las sedes"}</p>
              </div>
            </li>
            <li className="perfil-meta__row">
              <ShieldIcon size={19} />
              <div>
                <p className="perfil-meta__label">Rol</p>
                <p className="perfil-meta__value">{rol?.nombre ?? usuario?.rolNombre ?? "—"}</p>
              </div>
            </li>
          </ul>
        </Card>

        <Card>
          <h2 className="card__title" style={{ marginBottom: 6 }}>
            Accesos de tu rol
          </h2>
          <p className="perfil-hint">
            {rol?.descripcion || "Módulos habilitados para tu rol en el sistema."}
          </p>
          <div className="perfil-chips">
            {modulosDelRol.length === 0 ? (
              <p className="empty-note">Tu rol todavía no tiene módulos asignados.</p>
            ) : (
              modulosDelRol.map((modulo) => (
                <span key={modulo} className="perfil-chip">
                  {modulo}
                </span>
              ))
            )}
          </div>
        </Card>
      </div>

      {/* ================================================ Columna derecha */}
      <div className="perfil-col">
        <Card>
          <div className="card__head">
            <h2 className="card__title">Información personal</h2>
            {editando ? (
              <div className="perfil-acciones">
                <button type="button" className="btn btn--neutral" onClick={cancelar}>
                  <XIcon size={18} /> Cancelar
                </button>
                <button type="button" className="btn btn--primary" onClick={guardar}>
                  <SaveIcon size={19} /> Guardar cambios
                </button>
              </div>
            ) : (
              <button type="button" className="btn btn--primary" onClick={empezarEdicion}>
                <EditIcon size={19} /> Editar perfil
              </button>
            )}
          </div>

          <div className="settings-grid">
            <TextField
              etiqueta="Nombre completo"
              requerido
              valor={datos.nombre}
              deshabilitado={!editando}
              error={errores.nombre}
              alCambiar={(v) => cambiar("nombre", v)}
            />
            <TextField
              etiqueta="Correo electrónico"
              requerido
              tipo="email"
              valor={datos.correo}
              deshabilitado={!editando}
              error={errores.correo}
              alCambiar={(v) => cambiar("correo", v)}
            />
            <TextField
              etiqueta="Documento"
              placeholder="CC 1.234.567"
              valor={datos.documento}
              deshabilitado={!editando}
              alCambiar={(v) => cambiar("documento", v)}
            />
            <TextField
              etiqueta="Teléfono"
              placeholder="300 000 0000"
              valor={datos.telefono}
              deshabilitado={!editando}
              error={errores.telefono}
              alCambiar={(v) => cambiar("telefono", v)}
            />
            <TextField
              etiqueta="Cargo"
              placeholder="Administrador de sede"
              valor={datos.cargo}
              deshabilitado={!editando}
              alCambiar={(v) => cambiar("cargo", v)}
            />
            <SelectField
              etiqueta="Sede asignada"
              valor={datos.sede}
              deshabilitado={!editando}
              opciones={[
                { valor: "", etiqueta: "Todas las sedes" },
                ...sedes.map((s) => ({ valor: s.nombre, etiqueta: s.nombre })),
              ]}
              alCambiar={(v) => cambiar("sede", v)}
            />
          </div>

          <div style={{ marginTop: 20 }}>
            <TextAreaField
              etiqueta="Sobre mí"
              filas={3}
              placeholder="Una línea sobre tu rol en Familia Puess."
              valor={datos.descripcion}
              deshabilitado={!editando}
              ayuda={editando ? "Opcional. Se muestra en tu ficha interna." : undefined}
              alCambiar={(v) => cambiar("descripcion", v)}
            />
          </div>
        </Card>

        <Card>
          <h2 className="card__title" style={{ marginBottom: 8 }}>
            Preferencias
          </h2>

          <div className="settings-grid" style={{ marginBottom: 6 }}>
            <SelectField
              etiqueta="Zona horaria"
              valor={datos.zonaHoraria}
              deshabilitado={!editando}
              opciones={ZONAS}
              alCambiar={(v) => cambiar("zonaHoraria", v)}
            />
            <SelectField
              etiqueta="Idioma"
              valor={datos.idioma}
              deshabilitado={!editando}
              opciones={IDIOMAS}
              alCambiar={(v) => cambiar("idioma", v)}
            />
          </div>

        </Card>

        <Card>
          <h2 className="card__title" style={{ marginBottom: 18 }}>
            Cambiar contraseña
          </h2>
          <div className="settings-grid">
            <TextField
              etiqueta="Contraseña actual"
              tipo="password"
              valor={claveActual}
              alCambiar={setClaveActual}
            />
            <TextField
              etiqueta="Contraseña nueva"
              tipo="password"
              valor={claveNueva}
              alCambiar={setClaveNueva}
            />
            <TextField
              etiqueta="Confirmar contraseña"
              tipo="password"
              valor={claveConfirmar}
              alCambiar={setClaveConfirmar}
            />
          </div>
          <p className="perfil-hint" style={{ marginTop: 12 }}>
            Usa al menos 8 caracteres, combinando mayúsculas, minúsculas y números.
          </p>
          <div style={{ marginTop: 20, display: "flex", justifyContent: "flex-end" }}>
            <button type="button" className="btn btn--primary" onClick={cambiarClave}>
              <KeyIcon size={19} /> Actualizar contraseña
            </button>
          </div>
        </Card>
      </div>

    </div>
  );
}
