import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthProvider";
import "../styles/not-found.css";

export function NotFoundPage() {
  const navegar = useNavigate();
  const { usuario } = useAuth();
  const autenticado = usuario !== null;

  return (
    <div className="not-found-page">
      <div className="not-found-card">
        <h1 className="not-found-code">404</h1>
        <p className="not-found-title">Pagina no encontrada</p>
        <p className="not-found-message">
          La pagina que buscas no existe o fue movida.
        </p>
        <button
          type="button"
          className="not-found-btn"
          onClick={() => navegar(autenticado ? "/panel" : "/login", { replace: true })}
        >
          {autenticado ? "Ir al panel" : "Ir al login"}
        </button>
      </div>
    </div>
  );
}
