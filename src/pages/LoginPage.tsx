import { useEffect, useState, type FormEvent } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import panelLateral from "../assets/images/login-bg.png";
import mazorca from "../assets/images/mazorca-deco.png";
import logo from "../assets/images/logo-familiapues.png";
import { Checkbox } from "../components/ui";
import { EyeIcon, EyeOffIcon, LockIcon, UserIcon } from "../components/ui/Icons";
import { useAuth } from "../context/AuthProvider";
import { leerUsuarioRecordado } from "../services/adminApi";
import "../styles/pages.css";

export function LoginPage() {
  const { usuario, entrar } = useAuth();
  const navegar = useNavigate();
  const ubicacion = useLocation();

  const [correo, setCorreo] = useState("");
  const [clave, setClave] = useState("");
  const [recordar, setRecordar] = useState(false);
  const [verClave, setVerClave] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    const recordado = leerUsuarioRecordado();
    if (recordado) {
      setCorreo(recordado);
      setRecordar(true);
    }
  }, []);

  if (usuario) {
    const destino = (ubicacion.state as { desde?: string } | null)?.desde ?? "/panel";
    return <Navigate to={destino} replace />;
  }

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault();
    setError(null);

    if (!correo.trim()) {
      setError("Escribe tu usuario para continuar.");
      return;
    }
    if (!clave) {
      setError("Escribe tu contraseña para continuar.");
      return;
    }

    setEnviando(true);
    try {
      await entrar(correo, clave, recordar);
      navegar("/panel", { replace: true });
    } catch (excepcion) {
      setError(excepcion instanceof Error ? excepcion.message : "No fue posible iniciar sesión.");
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div className="login">
      <div
        className="login__aside"
        style={{ backgroundImage: `url(${panelLateral})` }}
        role="img"
        aria-label="Familia Pues"
      />

      <div className="login__panel">
        <img className="login__corn login__corn--top" src={mazorca} alt="" />
        <img className="login__corn login__corn--bottom" src={mazorca} alt="" />

        <div className="login__card">
          <img className="login__logo" src={logo} alt="Familia Pues" />
          <h1 className="login__heading">Inicio de sesión administrativo</h1>

          <form className="login__form" onSubmit={enviar} noValidate>
            <div>
              <label className="login__field-label" htmlFor="login-usuario">
                Usuario
              </label>
              <div className="login__input-wrap">
                <UserIcon size={24} className="login__input-icon" />
                <input
                  id="login-usuario"
                  type="text"
                  className="login__input"
                  placeholder="usuario"
                  autoComplete="username"
                  value={correo}
                  onChange={(e) => setCorreo(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="login__field-label" htmlFor="login-clave">
                Contraseña
              </label>
              <div className="login__input-wrap">
                <LockIcon size={24} className="login__input-icon" />
                <input
                  id="login-clave"
                  type={verClave ? "text" : "password"}
                  className="login__input"
                  placeholder="**********"
                  autoComplete="current-password"
                  value={clave}
                  onChange={(e) => setClave(e.target.value)}
                />
                <button
                  type="button"
                  className="login__toggle-pw"
                  onClick={() => setVerClave((v) => !v)}
                  aria-label={verClave ? "Ocultar contraseña" : "Mostrar contraseña"}
                >
                  {verClave ? <EyeOffIcon size={20} /> : <EyeIcon size={20} />}
                </button>
              </div>
            </div>

            <div className="login__row">
              <Checkbox marcado={recordar} alCambiar={setRecordar}>
                Recordarme
              </Checkbox>
            </div>

            {error ? (
              <p className="login__alert" role="alert">
                {error}
              </p>
            ) : null}

            <button type="submit" className="login__submit" disabled={enviando}>
              {enviando ? <span className="spinner" /> : null}
              {enviando ? "Ingresando…" : "Ingresar"}
            </button>
          </form>

        </div>
      </div>
    </div>
  );
}
