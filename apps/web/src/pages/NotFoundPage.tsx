import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import "../styles/not-found.css";

export function NotFoundPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const handleBack = () => {
    navigate(isAuthenticated ? "/dashboard" : "/login", { replace: true });
  };

  return (
    <div className="not-found-page">
      <div className="not-found-card">
        <h1 className="not-found-code">404</h1>
        <p className="not-found-title">Pagina no encontrada</p>
        <p className="not-found-message">
          La pagina que buscas no existe o fue movida.
        </p>
        <button type="button" className="not-found-btn" onClick={handleBack}>
          {isAuthenticated ? "Ir al Dashboard" : "Ir al Login"}
        </button>
      </div>
    </div>
  );
}
