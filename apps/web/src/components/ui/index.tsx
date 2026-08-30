/* ==========================================================================
   Componentes de interfaz compartidos por todas las pantallas del panel.
   ========================================================================== */

import {
  useEffect,
  useId,
  useState,
  type ChangeEvent,
  type ReactNode,
} from "react";
import { useBloquearScroll } from "../../hooks";
import {
  CalendarIcon,
  CheckIcon,
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  SearchIcon,
  XIcon,
} from "./Icons";

/* --------------------------------------------------------------- Tarjeta */

export function Card({
  children,
  className = "",
  pad = true,
}: {
  children: ReactNode;
  className?: string;
  pad?: boolean;
}) {
  return <section className={`card ${pad ? "card--pad" : ""} ${className}`.trim()}>{children}</section>;
}

/* ---------------------------------------------------- Tarjeta de métrica */

export function StatCard({
  icono,
  color,
  etiqueta,
  valor,
  pista,
}: {
  icono: ReactNode;
  color: "pink" | "yellow";
  etiqueta: string;
  valor: string | number;
  pista: string;
}) {
  return (
    <article className="stat-card">
      <div className={`stat-card__icon stat-card__icon--${color}`}>{icono}</div>
      <div className="stat-card__body">
        <p className="stat-card__label">{etiqueta}</p>
        <p className="stat-card__value">{valor}</p>
        <p className="stat-card__hint">{pista}</p>
      </div>
    </article>
  );
}

/* -------------------------------------------------------------- Buscador */

export function SearchInput({
  valor,
  alCambiar,
  placeholder,
  etiquetaAccesible,
}: {
  valor: string;
  alCambiar: (valor: string) => void;
  placeholder: string;
  etiquetaAccesible?: string;
}) {
  return (
    <div className="search">
      <SearchIcon className="search__icon" size={22} />
      <input
        type="search"
        className="input"
        value={valor}
        placeholder={placeholder}
        aria-label={etiquetaAccesible ?? placeholder}
        onChange={(e: ChangeEvent<HTMLInputElement>) => alCambiar(e.target.value)}
      />
    </div>
  );
}

/* ---------------------------------------------------------------- Select */

export interface Opcion {
  valor: string;
  etiqueta: string;
}

export function SelectField({
  etiqueta,
  valor,
  opciones,
  alCambiar,
  className = "",
}: {
  etiqueta?: string;
  valor: string;
  opciones: Opcion[];
  alCambiar: (valor: string) => void;
  className?: string;
}) {
  const id = useId();
  return (
    <div className={`field ${className}`.trim()}>
      {etiqueta ? (
        <label className="field__label" htmlFor={id}>
          {etiqueta}
        </label>
      ) : null}
      <div className="select">
        <select
          id={id}
          className="select__control"
          value={valor}
          onChange={(e) => alCambiar(e.target.value)}
          aria-label={etiqueta}
        >
          {opciones.map((opcion) => (
            <option key={opcion.valor} value={opcion.valor}>
              {opcion.etiqueta}
            </option>
          ))}
        </select>
        <ChevronDownIcon className="select__chevron" size={22} />
      </div>
    </div>
  );
}

/* ----------------------------------------------------------- Campo texto */

export function TextField({
  etiqueta,
  valor,
  alCambiar,
  placeholder,
  tipo = "text",
  error,
  requerido,
}: {
  etiqueta: string;
  valor: string;
  alCambiar: (valor: string) => void;
  placeholder?: string;
  tipo?: string;
  error?: string;
  requerido?: boolean;
}) {
  const id = useId();
  return (
    <div className="field">
      <label className="field__label" htmlFor={id}>
        {etiqueta}
        {requerido ? " *" : ""}
      </label>
      <input
        id={id}
        type={tipo}
        className={`input ${error ? "input--invalid" : ""}`.trim()}
        value={valor}
        placeholder={placeholder}
        aria-invalid={Boolean(error)}
        onChange={(e) => alCambiar(e.target.value)}
      />
      {error ? <span className="field__error">{error}</span> : null}
    </div>
  );
}

/* --------------------------------------------------------- Rango fechas */

export interface RangoFechas {
  desde: string; // yyyy-mm-dd
  hasta: string;
}

export function DateRangeField({
  etiqueta,
  rango,
  alCambiar,
}: {
  etiqueta?: string;
  rango: RangoFechas;
  alCambiar: (rango: RangoFechas) => void;
}) {
  const [abierto, setAbierto] = useState(false);

  const formatear = (iso: string) => {
    const [anio = "", mes = "", dia = ""] = iso.split("-");
    return `${dia}/${mes}/${anio}`;
  };

  return (
    <div className="field">
      {etiqueta ? <span className="field__label">{etiqueta}</span> : null}
      <div className="daterange">
        <button
          type="button"
          className="daterange__control"
          onClick={() => setAbierto((v) => !v)}
          aria-expanded={abierto}
          aria-haspopup="dialog"
        >
          <span>
            {formatear(rango.desde)} - {formatear(rango.hasta)}
          </span>
          <CalendarIcon size={22} />
        </button>

        {abierto ? (
          <>
            <button
              type="button"
              className="sidebar__scrim"
              style={{ background: "transparent", display: "block", zIndex: 55 }}
              aria-label="Cerrar selector de fechas"
              onClick={() => setAbierto(false)}
            />
            <div className="daterange__popover" role="dialog" aria-label="Rango de fechas">
              <div className="daterange__row">
                <div className="field">
                  <span className="field__label">Desde</span>
                  <input
                    type="date"
                    className="input"
                    value={rango.desde}
                    max={rango.hasta}
                    onChange={(e) => alCambiar({ ...rango, desde: e.target.value })}
                  />
                </div>
                <div className="field">
                  <span className="field__label">Hasta</span>
                  <input
                    type="date"
                    className="input"
                    value={rango.hasta}
                    min={rango.desde}
                    onChange={(e) => alCambiar({ ...rango, hasta: e.target.value })}
                  />
                </div>
              </div>
              <button type="button" className="btn btn--primary btn--block" onClick={() => setAbierto(false)}>
                Aplicar rango
              </button>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}

/* -------------------------------------------------------------- Checkbox */

export function Checkbox({
  marcado,
  alCambiar,
  children,
}: {
  marcado: boolean;
  alCambiar: (marcado: boolean) => void;
  children: ReactNode;
}) {
  return (
    <label className="checkbox">
      <input type="checkbox" checked={marcado} onChange={(e) => alCambiar(e.target.checked)} />
      <span className="checkbox__box">{marcado ? <CheckIcon size={16} /> : null}</span>
      <span>{children}</span>
    </label>
  );
}

/* ----------------------------------------------------------- Interruptor */

export function Switch({
  marcado,
  alCambiar,
  etiqueta,
}: {
  marcado: boolean;
  alCambiar: (marcado: boolean) => void;
  etiqueta: string;
}) {
  return (
    <label className="switch">
      <input
        type="checkbox"
        checked={marcado}
        onChange={(e) => alCambiar(e.target.checked)}
        aria-label={etiqueta}
      />
      <span className="switch__track">
        <span className="switch__thumb" />
      </span>
    </label>
  );
}

/* ---------------------------------------------------------------- Badges */

export function Badge({
  tono,
  children,
}: {
  tono: "green" | "pink" | "orange" | "purple" | "yellow" | "grey";
  children: ReactNode;
}) {
  return <span className={`badge badge--${tono}`}>{children}</span>;
}

export function BadgeOutline({
  tono,
  children,
}: {
  tono: "green" | "pink" | "yellow" | "neutral";
  children: ReactNode;
}) {
  return <span className={`badge-outline badge-outline--${tono}`}>{children}</span>;
}

/* ------------------------------------------------------------ Paginación */

export function Pagination({
  pagina,
  totalPaginas,
  info,
  irA,
}: {
  pagina: number;
  totalPaginas: number;
  info: string;
  irA: (pagina: number) => void;
}) {
  // Sin resultados no hay nada que paginar: solo se informa el estado.
  if (totalPaginas <= 1) {
    return (
      <nav className="pagination" aria-label="Paginación">
        <p className="pagination__info">{info}</p>
      </nav>
    );
  }

  const paginas: (number | "…")[] = [];
  const maximo = 5;

  if (totalPaginas <= maximo) {
    for (let i = 1; i <= totalPaginas; i += 1) paginas.push(i);
  } else if (pagina <= 3) {
    paginas.push(1, 2, 3, 4, "…", totalPaginas);
  } else if (pagina >= totalPaginas - 2) {
    paginas.push(1, "…", totalPaginas - 3, totalPaginas - 2, totalPaginas - 1, totalPaginas);
  } else {
    paginas.push(1, "…", pagina - 1, pagina, pagina + 1, "…", totalPaginas);
  }

  return (
    <nav className="pagination" aria-label="Paginación">
      <p className="pagination__info">{info}</p>
      <div className="pagination__pages">
        <button
          type="button"
          className="pagination__btn pagination__btn--arrow"
          onClick={() => irA(pagina - 1)}
          disabled={pagina <= 1}
          aria-label="Página anterior"
        >
          <ChevronLeftIcon size={16} />
        </button>

        {paginas.map((valor, indice) =>
          valor === "…" ? (
            <span key={`gap-${indice}`} className="pagination__ellipsis">
              …
            </span>
          ) : (
            <button
              key={valor}
              type="button"
              className={`pagination__btn ${valor === pagina ? "pagination__btn--active" : ""}`.trim()}
              onClick={() => irA(valor)}
              aria-current={valor === pagina ? "page" : undefined}
            >
              {valor}
            </button>
          ),
        )}

        <button
          type="button"
          className="pagination__btn pagination__btn--arrow"
          onClick={() => irA(pagina + 1)}
          disabled={pagina >= totalPaginas}
          aria-label="Página siguiente"
        >
          <ChevronRightIcon size={16} />
        </button>
      </div>
    </nav>
  );
}

/* ----------------------------------------------------------------- Modal */

export function Modal({
  abierto,
  titulo,
  subtitulo,
  ancho,
  alCerrar,
  children,
  pie,
}: {
  abierto: boolean;
  titulo: string;
  subtitulo?: string;
  ancho?: "normal" | "ancho";
  alCerrar: () => void;
  children: ReactNode;
  pie?: ReactNode;
}) {
  useBloquearScroll(abierto);

  useEffect(() => {
    if (!abierto) return;
    const enTecla = (e: KeyboardEvent) => {
      if (e.key === "Escape") alCerrar();
    };
    document.addEventListener("keydown", enTecla);
    return () => document.removeEventListener("keydown", enTecla);
  }, [abierto, alCerrar]);

  if (!abierto) return null;

  return (
    <div
      className="modal-scrim"
      role="presentation"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) alCerrar();
      }}
    >
      <div
        className={`modal ${ancho === "ancho" ? "modal--wide" : ""}`.trim()}
        role="dialog"
        aria-modal="true"
        aria-label={titulo}
      >
        <header className="modal__head">
          <div>
            <h2 className="modal__title">{titulo}</h2>
            {subtitulo ? <p className="modal__subtitle">{subtitulo}</p> : null}
          </div>
          <button type="button" className="modal__close" onClick={alCerrar} aria-label="Cerrar">
            <XIcon size={20} />
          </button>
        </header>
        <div className="modal__body">{children}</div>
        {pie ? <footer className="modal__foot">{pie}</footer> : null}
      </div>
    </div>
  );
}

/* -------------------------------------------------- Diálogo confirmación */

export function ConfirmDialog({
  abierto,
  titulo,
  mensaje,
  textoConfirmar = "Eliminar",
  alConfirmar,
  alCerrar,
}: {
  abierto: boolean;
  titulo: string;
  mensaje: string;
  textoConfirmar?: string;
  alConfirmar: () => void;
  alCerrar: () => void;
}) {
  return (
    <Modal
      abierto={abierto}
      titulo={titulo}
      alCerrar={alCerrar}
      pie={
        <>
          <button type="button" className="btn btn--neutral" onClick={alCerrar}>
            Cancelar
          </button>
          <button type="button" className="btn btn--danger" onClick={alConfirmar}>
            {textoConfirmar}
          </button>
        </>
      }
    >
      <p style={{ fontSize: 15, color: "var(--fp-text-body)", lineHeight: 1.6 }}>{mensaje}</p>
    </Modal>
  );
}

/* ---------------------------------------------------------- Tabla vacía */

export function EmptyRow({ columnas, mensaje }: { columnas: number; mensaje: string }) {
  return (
    <tr>
      <td className="table__empty" colSpan={columnas}>
        {mensaje}
      </td>
    </tr>
  );
}
