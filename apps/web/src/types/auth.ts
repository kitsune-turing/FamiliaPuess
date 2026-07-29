export interface LoginRequest {
  username: string;
  password: string;
}

export interface PermisoResponse {
  modulo_codigo: string;
  modulo_nombre: string;
  puede_leer: boolean;
  puede_escribir: boolean;
  puede_eliminar: boolean;
  puede_administrar: boolean;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  usuario_id: number;
  nombre: string;
  username: string;
  rol_codigo: string;
  rol_nombre: string;
  debe_cambiar_pw: boolean;
  permisos: PermisoResponse[];
}

export interface AuthUser {
  usuario_id: number;
  nombre: string;
  username: string;
  rol_codigo: string;
  rol_nombre: string;
  permisos: PermisoResponse[];
}
