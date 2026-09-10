import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthProvider";
import { useDatos } from "../../context/DataProvider";
import { NOTIFICACIONES } from "../../data/initial";
import { useClickFuera } from "../../hooks";
import { iniciales } from "../../lib/format";
import {
  BellIcon,
  ChevronDownIcon,
  LockIcon,
  LogOutIcon,
  MapPinIcon,
  MenuIcon,
  SettingsIcon,
  UserIcon,
} from "../ui/Icons";

interface Props {
  titulo: string;
  subtitulo: string;
  alAbrirMenu: () => void;
}

export function Topbar({ titulo, subtitulo, alAbrirMenu }: Props) {
  const { usuario, perfil, salir, sedeActiva, cambiarSede } = useAuth();
  const { sedes } = useDatos();
  const navegar = useNavigate();

  const [sedeAbierta, setSedeAbierta] = useState(false);
  const [notifAbiertas, setNotifAbiertas] = useState(false);
  const [menuAbierto, setMenuAbierto] = useState(false);

  const cerrarSede = useCallback(() => setSedeAbierta(false), []);
  const cerrarNotif = useCallback(() => setNotifAbiertas(false), []);
  const cerrarMenu = useCallback(() => setMenuAbierto(false), []);

  const refSede = useClickFuera<HTMLDivElement>(sedeAbierta, cerrarSede);
  const refNotif = useClickFuera<HTMLDivElement>(notifAbiertas, cerrarNotif);
  const refMenu = useClickFuera<HTMLDivElement>(menuAbierto, cerrarMenu);

  const nombre = usuario?.nombre ?? "Invitado";

  return (
    <header className="topbar">
      <div className="topbar__titles">
        <button type="button" className="topbar__menu-btn" onClick={alAbrirMenu} aria-label="Abrir menú">
          <MenuIcon size={22} />
        </button>
        <h1 className="topbar__title">{titulo}</h1>
        <p className="topbar__subtitle">{subtitulo}</p>
      </div>

      <div className="topbar__actions">
        {/* Selector de sede */}
        <div className="sede-select" ref={refSede}>
          <button
            type="button"
            className="sede-select__trigger"
            onClick={() => setSedeAbierta((v) => !v)}
            aria-expanded={sedeAbierta}
            aria-haspopup="listbox"
          >
            <MapPinIcon size={22} className="sede-select__pin" />
            <span>{sedeActiva}</span>
            <ChevronDownIcon
              size={20}
              className={`sede-select__chevron ${sedeAbierta ? "sede-select__chevron--open" : ""}`.trim()}
            />
          </button>

          {sedeAbierta ? (
            <div className="dropdown" role="listbox" style={{ maxHeight: 320, overflowY: "auto" }}>
              <button
                type="button"
                role="option"
                aria-selected={sedeActiva === "Todas las sedes"}
                className={`dropdown__item ${sedeActiva === "Todas las sedes" ? "dropdown__item--active" : ""}`.trim()}
                onClick={() => {
                  cambiarSede("Todas las sedes");
                  cerrarSede();
                }}
              >
                Todas las sedes
              </button>
              <div className="dropdown__divider" />
              {sedes.map((sede) => (
                <button
                  key={sede.id}
                  type="button"
                  role="option"
                  aria-selected={sedeActiva === sede.nombre}
                  className={`dropdown__item ${sedeActiva === sede.nombre ? "dropdown__item--active" : ""}`.trim()}
                  onClick={() => {
                    cambiarSede(sede.nombre);
                    cerrarSede();
                  }}
                >
                  {sede.nombre}
                </button>
              ))}
            </div>
          ) : null}
        </div>

        {/* Notificaciones */}
        <div style={{ position: "relative" }} ref={refNotif}>
          <button
            type="button"
            className="topbar__bell"
            onClick={() => setNotifAbiertas((v) => !v)}
            aria-expanded={notifAbiertas}
            aria-label={`Notificaciones (${NOTIFICACIONES.length} sin leer)`}
          >
            <BellIcon size={26} />
            {NOTIFICACIONES.length > 0 ? <span className="topbar__bell-dot" /> : null}
          </button>

          {notifAbiertas ? (
            <div className="dropdown notif-panel">
              <p className="notif-panel__head">Notificaciones</p>
              <div className="notif-panel__list">
                {NOTIFICACIONES.length === 0 ? (
                  <p className="empty-note" style={{ padding: "18px 16px" }}>
                    No tienes notificaciones.
                  </p>
                ) : (
                  NOTIFICACIONES.map((notificacion) => (
                    <div key={notificacion.id} className="notif-panel__item">
                      <span className="notif-panel__dot" />
                      <div>
                        <p className="notif-panel__text">{notificacion.texto}</p>
                        <p className="notif-panel__time">{notificacion.tiempo}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          ) : null}
        </div>

        {/* Menú de usuario */}
        <div className="user-menu" ref={refMenu}>
          <button
            type="button"
            className="user-menu__trigger"
            onClick={() => setMenuAbierto((v) => !v)}
            aria-expanded={menuAbierto}
            aria-haspopup="menu"
          >
            {perfil?.avatar ? (
              <img className="user-menu__avatar user-menu__avatar--img" src={perfil.avatar} alt="" />
            ) : (
              <span className="user-menu__avatar">{iniciales(nombre)}</span>
            )}
            <span className="user-menu__name">{nombre}</span>
            <ChevronDownIcon size={20} />
          </button>

          {menuAbierto ? (
            <div className="dropdown" role="menu">
              <div style={{ padding: "10px 12px 8px" }}>
                <p style={{ fontSize: 14, fontWeight: 600, color: "var(--fp-text)" }}>{nombre}</p>
                <p style={{ fontSize: 12.5, color: "var(--fp-text-muted)" }}>{usuario?.rolNombre}</p>
              </div>
              <div className="dropdown__divider" />
              <button
                type="button"
                role="menuitem"
                className="dropdown__item"
                onClick={() => {
                  cerrarMenu();
                  navegar("/panel/perfil");
                }}
              >
                <UserIcon size={18} /> Mi perfil
              </button>
              <button
                type="button"
                role="menuitem"
                className="dropdown__item"
                onClick={() => {
                  cerrarMenu();
                  navegar("/panel/configuracion");
                }}
              >
                <SettingsIcon size={18} /> Configuración
              </button>
              <button
                type="button"
                role="menuitem"
                className="dropdown__item"
                onClick={() => {
                  cerrarMenu();
                  navegar("/panel/seguridad");
                }}
              >
                <LockIcon size={18} /> Seguridad
              </button>
              <div className="dropdown__divider" />
              <button
                type="button"
                role="menuitem"
                className="dropdown__item dropdown__item--danger"
                onClick={() => {
                  cerrarMenu();
                  salir();
                  navegar("/login", { replace: true });
                }}
              >
                <LogOutIcon size={18} /> Cerrar sesión
              </button>
            </div>
          ) : null}
        </div>
      </div>
    </header>
  );
}
