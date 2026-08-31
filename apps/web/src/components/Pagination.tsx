const PAGE_SIZE = 10;

interface PaginationProps {
  page: number;
  total: number;
  onPageChange: (page: number) => void;
}

export function paginate<T>(items: T[], page: number): T[] {
  const start = (page - 1) * PAGE_SIZE;
  return items.slice(start, start + PAGE_SIZE);
}

export function Pagination({ page, total, onPageChange }: PaginationProps) {
  const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const first = total === 0 ? 0 : (page - 1) * PAGE_SIZE + 1;
  const last = Math.min(page * PAGE_SIZE, total);

  return (
    <div className="admin-pagination" aria-label="Paginación">
      <span className="admin-pagination__info">
        Mostrando {first} a {last} de {total} registros
      </span>
      <div className="admin-pagination__controls">
        <button
          type="button"
          className="admin-pagination__btn"
          onClick={() => onPageChange(page - 1)}
          disabled={page === 1}
          aria-label="Página anterior"
        >
          &laquo;
        </button>
        {Array.from({ length: pageCount }, (_, index) => index + 1).map((number) => (
          <button
            key={number}
            type="button"
            className={`admin-pagination__btn ${number === page ? "admin-pagination__btn--active" : ""}`}
            onClick={() => onPageChange(number)}
            aria-label={`Página ${number}`}
            aria-current={number === page ? "page" : undefined}
          >
            {number}
          </button>
        ))}
        <button
          type="button"
          className="admin-pagination__btn"
          onClick={() => onPageChange(page + 1)}
          disabled={page === pageCount}
          aria-label="Página siguiente"
        >
          &raquo;
        </button>
      </div>
    </div>
  );
}

export { PAGE_SIZE };
