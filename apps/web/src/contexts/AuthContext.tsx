import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { setSessionExpiredHandler } from "../services/api";
import type { AuthUser, LoginResponse } from "../types/auth";

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  login: (response: LoginResponse) => void;
  logout: () => void;
  isAuthenticated: boolean;
  /** Sede seleccionada en la barra superior; filtra las pantallas del panel. */
  sedeActiva: string;
  cambiarSede: (sede: string) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const STORAGE_KEY_TOKEN = "fp_access_token";
const STORAGE_KEY_REFRESH = "fp_refresh_token";
const STORAGE_KEY_USER = "fp_user";
const STORAGE_KEY_SEDE = "fp_sede_activa";

function isTokenExpired(token: string): boolean {
  try {
    // Un JWT mal formado no tiene segunda parte: se trata como expirado.
    const payloadSegment = token.split(".")[1];
    if (!payloadSegment) return true;
    const payload = JSON.parse(atob(payloadSegment)) as { exp?: number };
    if (!payload.exp) return true;
    return Date.now() >= payload.exp * 1000;
  } catch {
    return true;
  }
}

function loadStoredAuth(): { user: AuthUser | null; token: string | null } {
  try {
    const token = localStorage.getItem(STORAGE_KEY_TOKEN);
    const raw = localStorage.getItem(STORAGE_KEY_USER);

    if (!token || !raw || isTokenExpired(token)) {
      localStorage.removeItem(STORAGE_KEY_TOKEN);
      localStorage.removeItem(STORAGE_KEY_REFRESH);
      localStorage.removeItem(STORAGE_KEY_USER);
      return { user: null, token: null };
    }

    return { user: JSON.parse(raw) as AuthUser, token };
  } catch {
    return { user: null, token: null };
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [{ user, token }, setAuth] = useState(loadStoredAuth);
  const [sedeActiva, setSedeActiva] = useState(
    () => localStorage.getItem(STORAGE_KEY_SEDE) ?? "Todas las sedes",
  );

  const cambiarSede = useCallback((sede: string) => {
    setSedeActiva(sede);
    localStorage.setItem(STORAGE_KEY_SEDE, sede);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY_TOKEN);
    localStorage.removeItem(STORAGE_KEY_REFRESH);
    localStorage.removeItem(STORAGE_KEY_USER);
    setAuth({ user: null, token: null });
  }, []);

  useEffect(() => {
    setSessionExpiredHandler(logout);
  }, [logout]);

  const login = useCallback((response: LoginResponse) => {
    const authUser: AuthUser = {
      usuario_id: response.usuario_id,
      nombre: response.nombre,
      username: response.username,
      rol_codigo: response.rol_codigo,
      rol_nombre: response.rol_nombre,
      permisos: response.permisos,
    };

    localStorage.setItem(STORAGE_KEY_TOKEN, response.access_token);
    localStorage.setItem(STORAGE_KEY_REFRESH, response.refresh_token);
    localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(authUser));

    setAuth({ user: authUser, token: response.access_token });
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      login,
      logout,
      isAuthenticated: user !== null && token !== null,
      sedeActiva,
      cambiarSede,
    }),
    [user, token, login, logout, sedeActiva, cambiarSede],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
