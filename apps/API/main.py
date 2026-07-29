from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.API.routers.auth import router as auth_router
from apps.API.routers.configuracion import router as configuracion_router
from apps.API.routers.desktop import router as desktop_router
from apps.API.routers.empleados import router as empleados_router
from apps.API.routers.registro import router as registro_router
from apps.API.routers.sedes import router as sedes_router
from apps.API.routers.permisos import router as permisos_router
from apps.API.routers.roles import router as roles_router
from apps.API.routers.usuarios import router as usuarios_router
from shared.exceptions.attendance import AsistenciaDuplicadaError
from shared.exceptions.auth import (
    CambioContrasenaRequeridoError,
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
from shared.exceptions.device import DispositivoNoAutorizadoError, DispositivoNoEncontradoError
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
from shared.exceptions.registration import (
    CodigoAlfaInvalidoError,
    DispositivoTokenNoAutorizadoError,
    SedeNoDisponibleError,
    TokenConsumidoError,
    TokenExpiradoError,
    TokenFormatoInvalidoError,
    TokenNoEncontradoError,
)

app = FastAPI(title="Familia Puess - Sistema de Control de Asistencia")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(configuracion_router)
app.include_router(desktop_router)
app.include_router(empleados_router)
app.include_router(registro_router)
app.include_router(sedes_router)
app.include_router(roles_router)
app.include_router(permisos_router)
app.include_router(usuarios_router)


@app.exception_handler(ConflictoConcurrenciaError)
async def handle_conflicto_concurrencia(
    request: Request, exc: ConflictoConcurrenciaError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(EmpleadoNoEncontradoError)
async def handle_empleado_no_encontrado_crud(
    request: Request, exc: EmpleadoNoEncontradoError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(DocumentoDuplicadoError)
async def handle_documento_duplicado(
    request: Request, exc: DocumentoDuplicadoError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(DocumentoFormatoInvalidoError)
@app.exception_handler(NombreInvalidoError)
async def handle_empleado_validacion(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(SedeNoEncontradaError)
async def handle_sede_no_encontrada(
    request: Request, exc: SedeNoEncontradaError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(SedeInactivaError)
async def handle_sede_inactiva(
    request: Request, exc: SedeInactivaError
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(SedeNombreDuplicadoError)
async def handle_sede_nombre_duplicado(
    request: Request, exc: SedeNombreDuplicadoError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(SedeDireccionInvalidaError)
@app.exception_handler(SedeNombreInvalidoError)
async def handle_sede_validacion(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(DispositivoNoEncontradoError)
async def handle_dispositivo_no_encontrado(
    request: Request, exc: DispositivoNoEncontradoError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(DispositivoNoAutorizadoError)
async def handle_dispositivo_no_autorizado(
    request: Request, exc: DispositivoNoAutorizadoError
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(SetupIncompletoError)
async def handle_setup_incompleto(
    request: Request, exc: SetupIncompletoError
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(EstadoNoEncontradoError)
@app.exception_handler(ConfiguracionNoEncontradaError)
async def handle_configuracion_invalida(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Error de configuracion interna"})


@app.exception_handler(TokenNoEncontradoError)
@app.exception_handler(TokenFormatoInvalidoError)
async def handle_token_invalido(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(TokenExpiradoError)
@app.exception_handler(TokenConsumidoError)
async def handle_token_expirado(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=410, content={"detail": str(exc)})


@app.exception_handler(SedeNoDisponibleError)
async def handle_sede_no_disponible(
    request: Request, exc: SedeNoDisponibleError
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(EmpleadoNoRegistradoError)
async def handle_empleado_no_registrado(
    request: Request, exc: EmpleadoNoRegistradoError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(EmpleadoInactivoError)
async def handle_empleado_inactivo(
    request: Request, exc: EmpleadoInactivoError
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(CodigoAlfaInvalidoError)
async def handle_codigo_invalido(
    request: Request, exc: CodigoAlfaInvalidoError
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(DispositivoTokenNoAutorizadoError)
async def handle_dispositivo_token_no_autorizado(
    request: Request, exc: DispositivoTokenNoAutorizadoError
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(AsistenciaDuplicadaError)
async def handle_asistencia_duplicada(
    request: Request, exc: AsistenciaDuplicadaError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(CredencialesInvalidasError)
async def handle_credenciales_invalidas(
    request: Request, exc: CredencialesInvalidasError
) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(UsuarioInactivoError)
async def handle_usuario_inactivo(
    request: Request, exc: UsuarioInactivoError
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(CuentaBloqueadaError)
async def handle_cuenta_bloqueada(
    request: Request, exc: CuentaBloqueadaError
) -> JSONResponse:
    return JSONResponse(status_code=429, content={"detail": str(exc)})


@app.exception_handler(SesionExistenteError)
async def handle_sesion_existente(
    request: Request, exc: SesionExistenteError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(TokenInvalidoError)
async def handle_auth_token_invalido(
    request: Request, exc: TokenInvalidoError
) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(RefreshTokenInvalidoError)
async def handle_refresh_token_invalido(
    request: Request, exc: RefreshTokenInvalidoError
) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(SesionNoEncontradaError)
async def handle_sesion_no_encontrada(
    request: Request, exc: SesionNoEncontradaError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(PermisoInsuficienteError)
async def handle_permiso_insuficiente(
    request: Request, exc: PermisoInsuficienteError
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(CambioContrasenaRequeridoError)
async def handle_cambio_contrasena(
    request: Request, exc: CambioContrasenaRequeridoError
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(RolNoEncontradoError)
async def handle_rol_no_encontrado(
    request: Request, exc: RolNoEncontradoError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(RolCodigoDuplicadoError)
async def handle_rol_codigo_duplicado(
    request: Request, exc: RolCodigoDuplicadoError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(RolProtegidoError)
async def handle_rol_protegido(
    request: Request, exc: RolProtegidoError
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(RolTieneUsuariosError)
async def handle_rol_tiene_usuarios(
    request: Request, exc: RolTieneUsuariosError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(PermisoNoEncontradoError)
async def handle_permiso_no_encontrado(
    request: Request, exc: PermisoNoEncontradoError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(PermisoDuplicadoError)
async def handle_permiso_duplicado(
    request: Request, exc: PermisoDuplicadoError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(ModuloNoEncontradoError)
async def handle_modulo_no_encontrado(
    request: Request, exc: ModuloNoEncontradoError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(UsuarioNoEncontradoError)
async def handle_usuario_no_encontrado(
    request: Request, exc: UsuarioNoEncontradoError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(CorreoDuplicadoError)
async def handle_correo_duplicado(
    request: Request, exc: CorreoDuplicadoError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(UsernameDuplicadoError)
async def handle_username_duplicado(
    request: Request, exc: UsernameDuplicadoError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(UltimoSuperAdminError)
async def handle_ultimo_super_admin(
    request: Request, exc: UltimoSuperAdminError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(AutoDesactivacionError)
async def handle_auto_desactivacion(
    request: Request, exc: AutoDesactivacionError
) -> JSONResponse:
    return JSONResponse(status_code=200, content={"detail": str(exc)})


@app.exception_handler(RolInactivoError)
async def handle_rol_inactivo(
    request: Request, exc: RolInactivoError
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})
