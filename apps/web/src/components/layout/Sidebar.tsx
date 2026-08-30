import type { JSX } from "react";
import { NavLink } from "react-router-dom";
import logo from "../../assets/images/logo-familiapues.png";
import marcas from "../../assets/images/marcas.png";
import {
  CatalogIcon,
  ChartIcon,
  ClipboardIcon,
  ClockIcon,
  HomeIcon,
  LockIcon,
  MapPinIcon,
  MonitorIcon,
  ParameterIcon,
  SettingsIcon,
  ShieldIcon,
  UsersIcon,
  type IconProps,
} from "../ui/Icons";

interface Enlace {
  to: string;
  etiqueta: string;
  Icono: (props: IconProps) => JSX.Element;
  exacto?: boolean;
}

/** Bloque principal del menú. */
const MENU_PRINCIPAL: Enlace[] = [
  { to: "/panel", etiqueta: "Dashboard", Icono: HomeIcon, exacto: true },
  { to: "/panel/registros", etiqueta: "Registros de entrada", Icono: ClockIcon },
  { to: "/panel/trabajadores", etiqueta: "Trabajadores", Icono: UsersIcon },
  { to: "/panel/dispositivos", etiqueta: "Dispositivos", Icono: MonitorIcon },
  { to: "/panel/sedes", etiqueta: "Sedes", Icono: MapPinIcon },
  { to: "/panel/reportes", etiqueta: "Reportes", Icono: ChartIcon },
  { to: "/panel/usuarios", etiqueta: "Usuarios", Icono: ShieldIcon },
  { to: "/panel/configuracion", etiqueta: "Configuración", Icono: SettingsIcon },
  { to: "/panel/seguridad", etiqueta: "Seguridad", Icono: LockIcon },
  { to: "/panel/auditoria", etiqueta: "Auditoría", Icono: ClipboardIcon },
];

/** Bloque de administración: solo lo ve el súper administrador. */
const MENU_ADMINISTRACION: Enlace[] = [
  { to: "/panel/catalogos", etiqueta: "Catálogos", Icono: CatalogIcon },
  { to: "/panel/parametros", etiqueta: "Parámetros", Icono: ParameterIcon },
];

function Enlaces({ enlaces, alCerrar }: { enlaces: Enlace[]; alCerrar: () => void }) {
  return (
    <>
      {enlaces.map(({ to, etiqueta, Icono, exacto }) => (
        <NavLink
          key={to}
          to={to}
          end={Boolean(exacto)}
          onClick={alCerrar}
          className={({ isActive }) => `sidebar__link ${isActive ? "sidebar__link--active" : ""}`.trim()}
        >
          <Icono size={22} />
          <span>{etiqueta}</span>
        </NavLink>
      ))}
    </>
  );
}

export function Sidebar({
  abierto,
  alCerrar,
  mostrarAdministracion,
}: {
  abierto: boolean;
  alCerrar: () => void;
  mostrarAdministracion: boolean;
}) {
  return (
    <>
      {abierto ? (
        <button type="button" className="sidebar__scrim" aria-label="Cerrar menú" onClick={alCerrar} />
      ) : null}

      <aside className={`sidebar ${abierto ? "sidebar--open" : ""}`.trim()}>
        <div className="sidebar__brand">
          <img className="sidebar__logo" src={logo} alt="Familia Pues" />
          <p className="sidebar__tagline">Sistema de control de asistencia</p>
        </div>

        <nav className="sidebar__nav" aria-label="Navegación principal">
          <p className="sidebar__section-label">Menú principal</p>
          <Enlaces enlaces={MENU_PRINCIPAL} alCerrar={alCerrar} />

          {mostrarAdministracion ? (
            <>
              <p className="sidebar__section-label sidebar__section-label--admin">Administración</p>
              <Enlaces enlaces={MENU_ADMINISTRACION} alCerrar={alCerrar} />
            </>
          ) : null}
        </nav>

        <div className="sidebar__footer">
          <p className="sidebar__footer-label">Nuestras marcas</p>
          <img className="sidebar__brands" src={marcas} alt="Arepa Puess, Helado Puess y Empanada Puess" />
        </div>
      </aside>
    </>
  );
}
