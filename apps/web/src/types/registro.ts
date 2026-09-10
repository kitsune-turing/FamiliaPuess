export interface TokenValidarResponse {
  token: string;
  sede_nombre: string;
}

export interface RegistroRequest {
  token: string;
  documento: string;
  codigo_alfa: string;
}

export interface RegistroResponse {
  mensaje: string;
  empleado_nombre: string;
  sede_nombre: string;
  registrado_en: string;
}

export interface ApiError {
  detail: string;
}
