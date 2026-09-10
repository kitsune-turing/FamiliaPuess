import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  actualizarUsuarioSesion,
  borrarPerfil,
  borrarSesion,
  cerrarSesionEnApi,
  guardarPerfil,
  guardarSesion,
  hayApi,
  iniciarSesion as iniciarSesionApi,
  leerPerfil,
  leerSesion,
  obtenerSesionActual,
  registrarManejadorSesionExpirada,
} from "../services/adminApi";
import type { Perfil, UsuarioSesion } from "../types/admin";

interface AuthContextValue {
  usuario: UsuarioSesion | null;
  cargando: boolean;
  entrar: (usuario: string, clave: string, recordar: boolean) => Promise<void>;
  salir: () => void;
  sedeActiva: string;
  cambiarSede: (sede: string) => void;

  /** Datos editables de la persona que tiene la sesión abierta. */
  perfil: Perfil | null;
  actualizarPerfil: (cambios: Partial<Perfil>) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const CLAVE_SEDE = "fp_sede_activa";

/**
 * Comprueba la caducidad del JWT antes de confiar en la sesión guardada.
 * Evita mostrar por un instante una sesión muerta y ahorra una llamada
 * inútil a `/auth/me`. Un token mal formado se trata como expirado.
 */
function tokenExpirado(token: string): boolean {
  // Los tokens de demostración no son JWT: se dan por válidos.
  if (token.startsWith("demo-")) return false;

  try {
    const cuerpo = token.split(".")[1];
    if (!cuerpo) return true;
    const datos = JSON.parse(atob(cuerpo)) as { exp?: number };
    if (!datos.exp) return true;
    return Date.now() >= datos.exp * 1000;
  } catch {
    return true;
  }
}

/**
 * Construye el perfil a partir de la sesión y le superpone lo que la persona
 * haya editado antes. Cuando exista `GET /usuarios/me` bastará con reemplazar
 * esta función por la respuesta de la API.
 */
function construirPerfil(usuario: UsuarioSesion): Perfil {
  const base: Perfil = {
    nombre: usuario.nombre,
    correo: usuario.username,
    documento: "",
    telefono: "",
    cargo: usuario.rolNombre,
    sede: "",
    zonaHoraria: "America/Bogota",
    idioma: "es-CO",
    avatar: "",
    descripcion: "",
    notificarCorreo: true,
    resumenDiario: false,
  };
  return { ...base, ...(leerPerfil() ?? {}) };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<UsuarioSesion | null>(null);
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [cargando, setCargando] = useState(true);
  const [sedeActiva, setSedeActiva] = useState(
    () => window.localStorage.getItem(CLAVE_SEDE) ?? "Todas las sedes",
  );

  useEffect(() => {
    const sesion = leerSesion();
    if (!sesion) {
      setCargando(false);
      return;
    }

    // Token vencido: se limpia sin molestar al servidor.
    if (tokenExpirado(sesion.token)) {
      borrarSesion();
      borrarPerfil();
      setCargando(false);
      return;
    }

    // Se muestra la sesión guardada de inmediato para no parpadear...
    setUsuario(sesion.usuario);
    setPerfil(construirPerfil(sesion.usuario));

    // ...y en paralelo se revalida contra la API, si está configurada.
    if (!hayApi()) {
      setCargando(false);
      return;
    }

    let vigente = true;
    obtenerSesionActual()
      .then((actual) => {
        if (!vigente) return;
        setUsuario(actual);
        setPerfil(construirPerfil(actual));
        actualizarUsuarioSesion(actual);
      })
      .catch(() => {
        // Token inválido: `registrarManejadorSesionExpirada` ya cerró la sesión.
      })
      .finally(() => {
        if (vigente) setCargando(false);
      });

    return () => {
      vigente = false;
    };
  }, []);

  const entrar = useCallback(async (nombreUsuario: string, clave: string, recordar: boolean) => {
    const resultado = await iniciarSesionApi(nombreUsuario, clave);
    guardarSesion(resultado.usuario, resultado.token, recordar, resultado.refresh);
    setUsuario(resultado.usuario);
    setPerfil(construirPerfil(resultado.usuario));
  }, []);

  /** Limpia el estado local. No llama a la API (se usa al expirar la sesión). */
  const limpiarSesion = useCallback(() => {
    borrarSesion();
    borrarPerfil();
    setUsuario(null);
    setPerfil(null);
  }, []);

  const salir = useCallback(() => {
    void cerrarSesionEnApi();
    limpiarSesion();
  }, [limpiarSesion]);

  // Si la API responde 401 y el refresh falla, la sesión se cierra sola.
  useEffect(() => {
    registrarManejadorSesionExpirada(limpiarSesion);
  }, [limpiarSesion]);

  const cambiarSede = useCallback((sede: string) => {
    setSedeActiva(sede);
    window.localStorage.setItem(CLAVE_SEDE, sede);
  }, []);

  /** Guarda los cambios del perfil y mantiene la barra superior sincronizada. */
  const actualizarPerfil = useCallback((cambios: Partial<Perfil>) => {
    setPerfil((previo) => {
      if (!previo) return previo;
      const siguiente = { ...previo, ...cambios };
      guardarPerfil(siguiente);
      return siguiente;
    });

    setUsuario((previo) => {
      if (!previo) return previo;
      const siguiente: UsuarioSesion = {
        ...previo,
        nombre: cambios.nombre?.trim() || previo.nombre,
        username: cambios.correo?.trim() || previo.username,
      };
      actualizarUsuarioSesion(siguiente);
      return siguiente;
    });
  }, []);

  const valor = useMemo(
    () => ({
      usuario,
      cargando,
      entrar,
      salir,
      sedeActiva,
      cambiarSede,
      perfil,
      actualizarPerfil,
    }),
    [usuario, cargando, entrar, salir, sedeActiva, cambiarSede, perfil, actualizarPerfil],
  );

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return ctx;
}
