import { type FormEvent, useCallback, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { login } from "../services/api";
import marcaImg from "../assets/images/marca.png";
import mazorcaImg from "../assets/images/mazorca.png";
import loginBgImg from "../assets/images/login-bg.png";
import userIcon from "../assets/icons/user.png";
import "../styles/login.css";

export function LoginPage() {
  const { login: authLogin, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();
      if (loading) return;

      setError("");
      setLoading(true);

      login({ username, password })
        .then((response) => {
          authLogin(response);
          navigate("/dashboard", { replace: true });
        })
        .catch((err: Error) => {
          setError(err.message);
          setLoading(false);
        });
    },
    [username, password, loading, authLogin, navigate],
  );

  const canSubmit = username.trim().length > 0 && password.length > 0;

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="login-page">
      <div className="login-panel-left">
        <img
          src={loginBgImg}
          alt=""
          className="login-panel-left__bg"
        />
      </div>

      <div className="login-panel-right">
        <img
          src={mazorcaImg}
          alt=""
          className="login-mazorca login-mazorca--top-right"
        />
        <img
          src={mazorcaImg}
          alt=""
          className="login-mazorca login-mazorca--bottom-right"
        />

        <div className="login-card">
          <img src={marcaImg} alt="Familia Puess" className="login-marca" />
          <p className="login-subtitle">Inicio de sesion administrativo</p>

          <form className="login-form" onSubmit={handleSubmit}>
            <div className="login-field">
              <label className="login-field__label" htmlFor="login-username">
                Usuario
              </label>
              <div className="login-field__input-wrapper">
                <img src={userIcon} alt="" className="login-field__icon" />
                <input
                  id="login-username"
                  className="login-field__input"
                  type="text"
                  placeholder="@email.com"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  disabled={loading}
                  autoComplete="username"
                />
              </div>
            </div>

            <div className="login-field">
              <label className="login-field__label" htmlFor="login-password">
                Contrasena
              </label>
              <div className="login-field__input-wrapper">
                <input
                  id="login-password"
                  className="login-field__input"
                  type="password"
                  placeholder="**********"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                  autoComplete="current-password"
                />
              </div>
            </div>

            <div className="login-options">
              <label className="login-remember">
                <input
                  type="checkbox"
                  className="login-remember__checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                  disabled={loading}
                />
                <span className="login-remember__text">Recordarme</span>
              </label>

              <button type="button" className="login-forgot" disabled={loading}>
                ¿Olvidaste tu contrasena?
              </button>
            </div>

            {error && <p className="login-error">{error}</p>}

            <button
              type="submit"
              className="login-submit"
              disabled={!canSubmit || loading}
            >
              {loading ? (
                <div className="login-spinner" />
              ) : (
                <span className="login-submit__text">Ingresar</span>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
