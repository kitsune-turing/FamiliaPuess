const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export interface TokenValidarResponse {
  token: string;
  sede_nombre: string;
  expira_en: string;
}

export interface RegistroRequest {
  token: string;
  documento: string;
  codigo_alfa: string;
}

export interface RegistroResponse {
  empleado_nombre: string;
  sede_nombre: string;
  registrado_en: string;
}

export async function validarToken(token: string): Promise<TokenValidarResponse> {
  const respuesta = await fetch(
    `${API_BASE}/registro/validar/${encodeURIComponent(token)}`,
  );
  if (!respuesta.ok) {
    const cuerpo = (await respuesta.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(cuerpo?.detail ?? "El codigo QR no es valido o ya expiro.");
  }
  return (await respuesta.json()) as TokenValidarResponse;
}

export async function registrarAsistencia(
  datos: RegistroRequest,
): Promise<RegistroResponse> {
  const respuesta = await fetch(`${API_BASE}/registro/registrar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
  if (!respuesta.ok) {
    const cuerpo = (await respuesta.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(cuerpo?.detail ?? "No se pudo registrar la asistencia.");
  }
  return (await respuesta.json()) as RegistroResponse;
}
