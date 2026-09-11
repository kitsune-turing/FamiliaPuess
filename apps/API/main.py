import logging
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from apps.API.core.config import get_settings
from apps.API.core.security_headers import SecurityHeadersMiddleware

from apps.API.routers.auditoria import router as auditoria_router
from apps.API.routers.auth import router as auth_router
from apps.API.routers.configuracion import router as configuracion_router
from apps.API.routers.dashboard import router as dashboard_router
from apps.API.routers.dispositivos import router as dispositivos_router
from apps.API.routers.desktop import router as desktop_router
from apps.API.routers.empleados import router as empleados_router
from apps.API.routers.horarios import router as horarios_router
from apps.API.routers.novedades import router as novedades_router
from apps.API.routers.registro import router as registro_router
from apps.API.routers.reportes import router as reportes_router
from apps.API.routers.sedes import router as sedes_router
from apps.API.routers.permisos import router as permisos_router
from apps.API.routers.roles import router as roles_router
from apps.API.routers.catalogos import router as catalogos_router
from apps.API.routers.usuarios import router as usuarios_router
from shared.exceptions.attendance import AsistenciaDuplicadaError
from shared.exceptions.auth import (
    CambioContrasenaRequeridoError,
    ContrasenaIgualError,
    CredencialesInvalidasError,
    CuentaBloqueadaError,
    PermisoInsuficienteError,
    RefreshTokenInvalidoError,
    SesionExistenteError,
    SesionNoEncontradaError,
    TokenInvalidoError,
    UsuarioInactivoError,
)
from shared.exceptions.catalog import EstadoNoEncontradoError
from shared.exceptions.permisos import (
    ModuloNoEncontradoError,
    PermisoDuplicadoError,
    PermisoNoEncontradoError,
)
from shared.exceptions.roles import (
    RolCodigoDuplicadoError,
    RolNoEncontradoError,
    RolProtegidoError,
    RolTieneUsuariosError,
)
from shared.exceptions.usuarios import (
    AutoDesactivacionError,
    CorreoDuplicadoError,
    RolInactivoError,
    UltimoSuperAdminError,
    UsernameDuplicadoError,
    UsuarioNoEncontradoError,
)
from shared.exceptions.concurrencia import ConflictoConcurrenciaError
from shared.exceptions.configuration import ConfiguracionNoEncontradaError, SetupIncompletoError
from shared.exceptions.device import (
    DispositivoNoAutorizadoError,
    DispositivoNoEncontradoError,
    DispositivoNoEncontradoPorIdError,
    FueraDeHorarioError,
    IdentificadorDuplicadoError,
    IdentificadorFormatoInvalidoError,
    SedeYaTieneDispositivoError,
)
from shared.exceptions.empleados import (
    DocumentoDuplicadoError,
    DocumentoFormatoInvalidoError,
    EmpleadoNoEncontradoError,
    NombreInvalidoError,
)
from shared.exceptions.sedes import (
    SedeDireccionInvalidaError,
    SedeInactivaError,
    SedeNoEncontradaError,
    SedeNombreDuplicadoError,
    SedeNombreInvalidoError,
)
from shared.exceptions.employee import EmpleadoInactivoError, EmpleadoNoRegistradoError
from shared.exceptions.horarios import (
    HorarioInmutableError,
    HorarioNoEncontradoError,
    HorarioSolapamientoError,
    HorarioToleranciaInvalidaError,
    HorarioVigenciaInvalidaError,
)
from shared.exceptions.novedades import (
    NovedadNoEncontradaError,
    SedesSinHorarioError,
    TipoNovedadNoEncontradoError,
)
from shared.exceptions.reportes import (
    RangoFechasInvalidoError,
    ReporteDuplicadoError,
    ReporteGeneracionError,
    ReporteNoEncontradoError,
    ReporteSinDatosError,
)
from shared.exceptions.registration import (
    CodigoAlfaInvalidoError,
    DispositivoTokenNoAutorizadoError,
    SedeNoDisponibleError,
    TokenConsumidoError,
    TokenExpiradoError,
    TokenFormatoInvalidoError,
    TokenNoEncontradoError,
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Familia Puess - Sistema de Control de Asistencia")


@app.on_event("startup")
async def _seed_superadmin() -> None:
    """Ensure superadmin exists with a known password for development."""
    from sqlalchemy import text
    from apps.API.database.session import _session_factory
    from apps.API.security.password import hash_password

    try:
        async with _session_factory() as session:
            pw_hash = hash_password("Admin123!")
            for uname in ("superadmin", "admin"):
                row = (await session.execute(text("SELECT id FROM usuario WHERE username = :u"), {"u": uname})).first()
                if row:
                    await session.execute(
                        text("UPDATE usuario SET password_hash = :h, debe_cambiar_pw = false WHERE username = :u"),
                        {"h": pw_hash, "u": uname},
                    )
            await session.commit()
            logger.info("dev passwords reset (Admin123!)")
    except Exception:
        logger.warning("Could not seed superadmin — database tables may not exist yet. Run the database.sql script first.")


@app.on_event("startup")
async def _validate_settings() -> None:
    settings = get_settings()
    _INSECURE_SECRETS = {
        "",
        "CHANGE-ME-IN-PRODUCTION",
        "docker-dev-secret-change-in-production",
        "secret",
        "changeme",
    }
    if settings.jwt_secret_key in _INSECURE_SECRETS:
        logger.critical("JWT_SECRET_KEY is missing or uses a known insecure value. Aborting.")
        sys.exit(1)
    if len(settings.jwt_secret_key) < 32:
        logger.critical("JWT_SECRET_KEY must be at least 32 characters. Aborting.")
        sys.exit(1)
    if "postgres:postgres@" in settings.database_url:
        logger.warning("DATABASE_URL is using default credentials. Change for production.")


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=500)

_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auditoria_router)
app.include_router(auth_router)
app.include_router(catalogos_router)
app.include_router(configuracion_router)
app.include_router(dashboard_router)
app.include_router(desktop_router)
app.include_router(dispositivos_router)
app.include_router(empleados_router)
app.include_router(horarios_router)
app.include_router(novedades_router)
app.include_router(registro_router)
app.include_router(reportes_router)
app.include_router(sedes_router)
app.include_router(roles_router)
app.include_router(permisos_router)
app.include_router(usuarios_router)

# ── Exception handlers ──────────────────────────────────────────────────
# Each tuple: (status_code, exception_class, optional fixed message).
# When message is None, str(exc) is used.

_EXCEPTION_MAP: list[tuple[int, type[Exception], str | None]] = [
    # Concurrencia
    (409, ConflictoConcurrenciaError, "El recurso fue modificado por otro usuario"),
    # Empleados
    (404, EmpleadoNoEncontradoError, None),
    (409, DocumentoDuplicadoError, None),
    (422, DocumentoFormatoInvalidoError, None),
    (422, NombreInvalidoError, None),
    # Sedes
    (404, SedeNoEncontradaError, None),
    (422, SedeInactivaError, None),
    (409, SedeNombreDuplicadoError, None),
    (422, SedeDireccionInvalidaError, None),
    (422, SedeNombreInvalidoError, None),
    # Dispositivos
    (404, DispositivoNoEncontradoError, None),
    (403, DispositivoNoAutorizadoError, None),
    (404, DispositivoNoEncontradoPorIdError, None),
    (409, IdentificadorDuplicadoError, None),
    (422, IdentificadorFormatoInvalidoError, None),
    (409, SedeYaTieneDispositivoError, None),
    (403, FueraDeHorarioError, None),
    # Configuración
    (422, SetupIncompletoError, None),
    (500, EstadoNoEncontradoError, "Error de configuracion interna"),
    (500, ConfiguracionNoEncontradaError, "Error de configuracion interna"),
    # Tokens / registro
    (404, TokenNoEncontradoError, None),
    (404, TokenFormatoInvalidoError, None),
    (410, TokenExpiradoError, None),
    (410, TokenConsumidoError, None),
    (403, SedeNoDisponibleError, None),
    (404, EmpleadoNoRegistradoError, None),
    (403, EmpleadoInactivoError, None),
    (422, CodigoAlfaInvalidoError, None),
    (403, DispositivoTokenNoAutorizadoError, None),
    (409, AsistenciaDuplicadaError, None),
    # Auth
    (401, CredencialesInvalidasError, None),
    (403, UsuarioInactivoError, None),
    (429, CuentaBloqueadaError, None),
    (409, SesionExistenteError, None),
    (401, TokenInvalidoError, None),
    (401, RefreshTokenInvalidoError, None),
    (404, SesionNoEncontradaError, None),
    (403, PermisoInsuficienteError, None),
    (403, CambioContrasenaRequeridoError, None),
    (400, ContrasenaIgualError, None),
    # Roles
    (404, RolNoEncontradoError, None),
    (409, RolCodigoDuplicadoError, None),
    (403, RolProtegidoError, None),
    (409, RolTieneUsuariosError, None),
    # Permisos
    (404, PermisoNoEncontradoError, None),
    (409, PermisoDuplicadoError, None),
    (404, ModuloNoEncontradoError, None),
    # Usuarios
    (404, UsuarioNoEncontradoError, None),
    (409, CorreoDuplicadoError, None),
    (409, UsernameDuplicadoError, None),
    (409, UltimoSuperAdminError, None),
    (200, AutoDesactivacionError, None),
    (422, RolInactivoError, None),
    # Horarios
    (404, HorarioNoEncontradoError, None),
    (409, HorarioSolapamientoError, None),
    (409, HorarioInmutableError, None),
    (422, HorarioVigenciaInvalidaError, None),
    (422, HorarioToleranciaInvalidaError, None),
    # Novedades
    (404, NovedadNoEncontradaError, None),
    (500, TipoNovedadNoEncontradoError, "Error de configuracion interna"),
    (422, SedesSinHorarioError, None),
    # Reportes
    (404, ReporteNoEncontradoError, None),
    (422, RangoFechasInvalidoError, None),
    (409, ReporteDuplicadoError, None),
    (500, ReporteGeneracionError, "Error interno al generar el reporte"),
    (404, ReporteSinDatosError, None),
]

for _status, _exc_cls, _fixed_msg in _EXCEPTION_MAP:

    def _make_handler(
        status: int, fixed_msg: str | None
    ):
        async def _handler(request: Request, exc: Exception) -> JSONResponse:
            return JSONResponse(
                status_code=status,
                content={"detail": fixed_msg or str(exc)},
            )
        return _handler

    app.add_exception_handler(_exc_cls, _make_handler(_status, _fixed_msg))
