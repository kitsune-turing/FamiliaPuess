import { useEffect, useMemo, useRef, useState, type RefObject } from "react";

/**
 * Pagina una lista ya filtrada y devuelve el segmento visible.
 * Se reinicia a la página 1 cuando cambia el tamaño del conjunto filtrado.
 */
export function usePaginacion<T>(items: T[], porPagina: number) {
  const [pagina, setPagina] = useState(1);
  const totalPaginas = Math.max(1, Math.ceil(items.length / porPagina));

  useEffect(() => {
    setPagina(1);
  }, [items.length]);

  const paginaSegura = Math.min(pagina, totalPaginas);
  const inicio = (paginaSegura - 1) * porPagina;
  const visibles = useMemo(
    () => items.slice(inicio, inicio + porPagina),
    [items, inicio, porPagina],
  );

  return {
    visibles,
    pagina: paginaSegura,
    totalPaginas,
    total: items.length,
    desde: items.length === 0 ? 0 : inicio + 1,
    hasta: Math.min(inicio + porPagina, items.length),
    irA: setPagina,
  };
}

/** Ejecuta `alCerrar` cuando se hace clic fuera del elemento o se pulsa Escape. */
export function useClickFuera<T extends HTMLElement>(
  activo: boolean,
  alCerrar: () => void,
): RefObject<T | null> {
  const ref = useRef<T | null>(null);

  useEffect(() => {
    if (!activo) return;

    const enClick = (evento: MouseEvent) => {
      if (ref.current && !ref.current.contains(evento.target as Node)) alCerrar();
    };
    const enTecla = (evento: KeyboardEvent) => {
      if (evento.key === "Escape") alCerrar();
    };

    document.addEventListener("mousedown", enClick);
    document.addEventListener("keydown", enTecla);
    return () => {
      document.removeEventListener("mousedown", enClick);
      document.removeEventListener("keydown", enTecla);
    };
  }, [activo, alCerrar]);

  return ref;
}

/** Bloquea el scroll del body mientras un modal está abierto. */
export function useBloquearScroll(activo: boolean): void {
  useEffect(() => {
    if (!activo) return;
    const previo = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = previo;
    };
  }, [activo]);
}
