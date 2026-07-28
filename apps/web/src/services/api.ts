import type {
  ApiError,
  RegistroRequest,
  RegistroResponse,
  TokenValidarResponse,
} from "../types/registro";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as ApiError | null;
    throw new Error(body?.detail ?? "Error inesperado del servidor");
  }
  return response.json() as Promise<T>;
}

export async function validarToken(
  token: string,
): Promise<TokenValidarResponse> {
  const response = await fetch(`${API_BASE}/registro/validar/${encodeURIComponent(token)}`);
  return handleResponse<TokenValidarResponse>(response);
}

export async function registrarAsistencia(
  payload: RegistroRequest,
): Promise<RegistroResponse> {
  const response = await fetch(`${API_BASE}/registro/registrar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<RegistroResponse>(response);
}
