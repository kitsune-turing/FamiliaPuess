/* ==========================================================================
   Componentes de interfaz compartidos por todas las pantallas del panel.
   ========================================================================== */

import {
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
  type ChangeEvent,
  type KeyboardEvent as KeyboardEventReact,
  type ReactNode,
} from "react";
import { createPortal } from "react-dom";
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

/**
 * Desplegable propio en lugar del `<select>` nativo.
 *
 * El navegador no permite dar color al resaltado de un `<option>`, así que la
 * lista se dibuja aquí para que la opción activa use el rosa de la marca. La
 * interfaz pública del componente no cambia: sigue recibiendo `valor`,
 * `opciones` y `alCambiar`.
 */
export function SelectField({
  etiqueta,
  valor,
  opciones,
  alCambiar,
  className = "",
  deshabilitado = false,
}: {
  etiqueta?: string;
  valor: string;
  opciones: Opcion[];
  alCambiar: (valor: string) => void;
  className?: string;
  deshabilitado?: boolean;
}) {
  const id = useId();
  const [abierto, setAbierto] = useState(false);
  const [resaltado, setResaltado] = useState(0);
  const [posicion, setPosicion] = useState({ top: 0, left: 0, width: 0, alto: 0 });

  const contenedorRef = useRef<HTMLDivElement | null>(null);
  const botonRef = useRef<HTMLButtonElement | null>(null);
  const listaRef = useRef<HTMLUListElement | null>(null);

  const indiceActual = opciones.findIndex((o) => o.valor === valor);
  const seleccionada = indiceActual >= 0 ? opciones[indiceActual] : undefined;

  // Al abrir, el foco de teclado arranca sobre la opción ya seleccionada.
  useEffect(() => {
    if (abierto) setResaltado(indiceActual >= 0 ? indiceActual : 0);
  }, [abierto, indiceActual]);

  /**
   * La lista se dibuja en un portal sobre `body` para que no la recorten los
   * modales ni las tablas con scroll. Por eso hay que calcular su posición a
   * mano y volver a hacerlo si la página se desplaza o cambia de tamaño.
   */
  useLayoutEffect(() => {
    if (!abierto) return;

    const calcular = () => {
      const caja = botonRef.current?.getBoundingClientRect();
      if (!caja) return;

      const alto = Math.min(264, opciones.length * 42 + 12);
      const espacioAbajo = window.innerHeight - caja.bottom;
      const haciaArriba = espacioAbajo < alto + 12 && caja.top > espacioAbajo;

      setPosicion({
        top: haciaArriba ? Math.max(8, caja.top - alto - 6) : caja.bottom + 6,
        left: caja.left,
        width: caja.width,
        alto,
      });
    };

    calcular();
    window.addEventListener("scroll", calcular, true);
    window.addEventListener("resize", calcular);
    return () => {
      window.removeEventListener("scroll", calcular, true);
      window.removeEventListener("resize", calcular);
    };
  }, [abierto, opciones.length]);

  // Cierre al hacer clic fuera del control o de la lista, y con Escape.
  useEffect(() => {
    if (!abierto) return;

    const enClick = (evento: MouseEvent) => {
      const destino = evento.target as Node;
      if (contenedorRef.current?.contains(destino)) return;
      if (listaRef.current?.contains(destino)) return;
      setAbierto(false);
    };
    const enTecla = (evento: KeyboardEvent) => {
      if (evento.key === "Escape") setAbierto(false);
    };

    document.addEventListener("mousedown", enClick);
    document.addEventListener("keydown", enTecla);
    return () => {
      document.removeEventListener("mousedown", enClick);
      document.removeEventListener("keydown", enTecla);
    };
  }, [abierto]);

  // Mantiene visible la opción resaltada cuando la lista tiene scroll.
  useEffect(() => {
    if (!abierto) return;
    const nodo = listaRef.current?.children[resaltado] as HTMLElement | undefined;
    nodo?.scrollIntoView({ block: "nearest" });
  }, [abierto, resaltado]);

  const elegir = (indice: number) => {
    const opcion = opciones[indice];
    if (!opcion) return;
    alCambiar(opcion.valor);
    setAbierto(false);
  };

  const enTecla = (evento: KeyboardEventReact<HTMLButtonElement>) => {
    if (deshabilitado) return;

    if (!abierto) {
      if (evento.key === "Enter" || evento.key === " " || evento.key === "ArrowDown") {
        evento.preventDefault();
        setAbierto(true);
      }
      return;
    }

    switch (evento.key) {
      case "ArrowDown":
        evento.preventDefault();
        setResaltado((r) => Math.min(r + 1, opciones.length - 1));
        break;
      case "ArrowUp":
        evento.preventDefault();
        setResaltado((r) => Math.max(r - 1, 0));
        break;
      case "Home":
        evento.preventDefault();
        setResaltado(0);
        break;
      case "End":
        evento.preventDefault();
        setResaltado(opciones.length - 1);
        break;
      case "Enter":
      case " ":
        evento.preventDefault();
        elegir(resaltado);
        break;
      case "Tab":
        setAbierto(false);
        break;
      default:
        break;
    }
  };

  return (
    <div className={`field ${className}`.trim()}>
      {etiqueta ? (
        <label className="field__label" htmlFor={id}>
          {etiqueta}
        </label>
      ) : null}
      <div className="select" ref={contenedorRef}>
        <button
          id={id}
          ref={botonRef}
          type="button"
          className="select__control"
          disabled={deshabilitado}
          aria-haspopup="listbox"
          aria-expanded={abierto}
          aria-label={etiqueta}
          onClick={() => setAbierto((a) => !a)}
          onKeyDown={enTecla}
        >
          <span className={seleccionada ? "" : "select__placeholder"}>
            {seleccionada?.etiqueta ?? "Seleccionar"}
          </span>
        </button>
        <ChevronDownIcon
          className={`select__chevron ${abierto ? "select__chevron--open" : ""}`.trim()}
          size={22}
        />

        {abierto
          ? createPortal(
              <ul
                className="select__menu select__menu--fija"
                role="listbox"
                ref={listaRef}
                tabIndex={-1}
                style={{
                  top: posicion.top,
                  left: posicion.left,
                  width: posicion.width,
                  maxHeight: posicion.alto,
                }}
              >
                {opciones.map((opcion, indice) => (
                  <li
                    key={opcion.valor}
                    role="option"
                    aria-selected={opcion.valor === valor}
                    className={[
                      "select__option",
                      opcion.valor === valor ? "select__option--activa" : "",
                      indice === resaltado ? "select__option--resaltada" : "",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                    onMouseEnter={() => setResaltado(indice)}
                    onClick={() => elegir(indice)}
                  >
                    <span>{opcion.etiqueta}</span>
                    {opcion.valor === valor ? <CheckIcon size={18} /> : null}
                  </li>
                ))}
              </ul>,
              document.body,
            )
          : null}
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
  deshabilitado = false,
  ayuda,
}: {
  etiqueta: string;
  valor: string;
  alCambiar: (valor: string) => void;
  placeholder?: string;
  tipo?: string;
  error?: string;
  requerido?: boolean;
  deshabilitado?: boolean;
  ayuda?: string;
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
        disabled={deshabilitado}
        aria-invalid={Boolean(error)}
        onChange={(e) => alCambiar(e.target.value)}
        {...(tipo === "time" ? { lang: "en-GB" } : {})}
      />
      {error ? <span className="field__error">{error}</span> : null}
      {!error && ayuda ? <span className="field__hint">{ayuda}</span> : null}
    </div>
  );
}

/* ------------------------------------------------------ Campo multilínea */

export function TextAreaField({
  etiqueta,
  valor,
  alCambiar,
  placeholder,
  filas = 3,
  error,
  requerido,
  deshabilitado = false,
  ayuda,
}: {
  etiqueta: string;
  valor: string;
  alCambiar: (valor: string) => void;
  placeholder?: string;
  filas?: number;
  error?: string;
  requerido?: boolean;
  deshabilitado?: boolean;
  ayuda?: string;
}) {
  const id = useId();
  return (
    <div className="field">
      <label className="field__label" htmlFor={id}>
        {etiqueta}
        {requerido ? " *" : ""}
      </label>
      <textarea
        id={id}
        rows={filas}
        className={`textarea ${error ? "input--invalid" : ""}`.trim()}
        value={valor}
        placeholder={placeholder}
        disabled={deshabilitado}
        aria-invalid={Boolean(error)}
        onChange={(e) => alCambiar(e.target.value)}
      />
      {error ? <span className="field__error">{error}</span> : null}
      {!error && ayuda ? <span className="field__hint">{ayuda}</span> : null}
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
  const botonRef = useRef<HTMLButtonElement | null>(null);
  const [pos, setPos] = useState({ top: 0, left: 0 });

  const formatear = (iso: string) => {
    const [anio = "", mes = "", dia = ""] = iso.split("-");
    return `${dia}/${mes}/${anio}`;
  };

  useLayoutEffect(() => {
    if (!abierto) return;
    const calcular = () => {
      const caja = botonRef.current?.getBoundingClientRect();
      if (!caja) return;
      const espacioAbajo = window.innerHeight - caja.bottom;
      const alto = 160;
      const haciaArriba = espacioAbajo < alto + 12 && caja.top > espacioAbajo;
      setPos({
        top: haciaArriba ? Math.max(8, caja.top - alto - 6) : caja.bottom + 6,
        left: Math.min(caja.left, window.innerWidth - 320),
      });
    };
    calcular();
    window.addEventListener("scroll", calcular, true);
    window.addEventListener("resize", calcular);
    return () => {
      window.removeEventListener("scroll", calcular, true);
      window.removeEventListener("resize", calcular);
    };
  }, [abierto]);

  useEffect(() => {
    if (!abierto) return;
    const enClick = (e: MouseEvent) => {
      const t = e.target as Node;
      if (botonRef.current?.contains(t)) return;
      const popover = document.querySelector(".daterange__popover--fija");
      if (popover?.contains(t)) return;
      setAbierto(false);
    };
    const enTecla = (e: KeyboardEvent) => {
      if (e.key === "Escape") setAbierto(false);
    };
    document.addEventListener("mousedown", enClick);
    document.addEventListener("keydown", enTecla);
    return () => {
      document.removeEventListener("mousedown", enClick);
      document.removeEventListener("keydown", enTecla);
    };
  }, [abierto]);

  return (
    <div className="field">
      {etiqueta ? <span className="field__label">{etiqueta}</span> : null}
      <div className="daterange">
        <button
          type="button"
          ref={botonRef}
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

        {abierto
          ? createPortal(
              <div
                className="daterange__popover daterange__popover--fija"
                role="dialog"
                aria-label="Rango de fechas"
                style={{ top: pos.top, left: pos.left }}
              >
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
              </div>,
              document.body,
            )
          : null}
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
  alConfirmar: () => void | Promise<void>;
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
