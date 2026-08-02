from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
from shared.exceptions.device import (
    DispositivoNoAutorizadoError,
    DispositivoNoEncontradoError,
    DispositivoNoEncontradoPorIdError,
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

app = FastAPI(title="Familia Puess - Sistema de Control de Asistencia")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auditoria_router)
app.include_router(auth_router)
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


@app.exception_handler(DispositivoNoEncontradoPorIdError)
async def handle_dispositivo_no_encontrado_por_id(
    request: Request, exc: DispositivoNoEncontradoPorIdError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(IdentificadorDuplicadoError)
async def handle_identificador_duplicado(
    request: Request, exc: IdentificadorDuplicadoError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(IdentificadorFormatoInvalidoError)
async def handle_identificador_formato_invalido(
    request: Request, exc: IdentificadorFormatoInvalidoError
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(SedeYaTieneDispositivoError)
async def handle_sede_ya_tiene_dispositivo(
    request: Request, exc: SedeYaTieneDispositivoError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


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


@app.exception_handler(HorarioNoEncontradoError)
async def handle_horario_no_encontrado(
    request: Request, exc: HorarioNoEncontradoError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(HorarioSolapamientoError)
async def handle_horario_solapamiento(
    request: Request, exc: HorarioSolapamientoError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(HorarioInmutableError)
async def handle_horario_inmutable(
    request: Request, exc: HorarioInmutableError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(HorarioVigenciaInvalidaError)
@app.exception_handler(HorarioToleranciaInvalidaError)
async def handle_horario_validacion(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(NovedadNoEncontradaError)
async def handle_novedad_no_encontrada(
    request: Request, exc: NovedadNoEncontradaError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(TipoNovedadNoEncontradoError)
async def handle_tipo_novedad_no_encontrado(
    request: Request, exc: TipoNovedadNoEncontradoError
) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Error de configuracion interna"})


@app.exception_handler(SedesSinHorarioError)
async def handle_sedes_sin_horario(
    request: Request, exc: SedesSinHorarioError
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(ReporteNoEncontradoError)
async def handle_reporte_no_encontrado(
    request: Request, exc: ReporteNoEncontradoError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(RangoFechasInvalidoError)
async def handle_rango_fechas_invalido(
    request: Request, exc: RangoFechasInvalidoError
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(ReporteDuplicadoError)
async def handle_reporte_duplicado(
    request: Request, exc: ReporteDuplicadoError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(ReporteGeneracionError)
async def handle_reporte_generacion(
    request: Request, exc: ReporteGeneracionError
) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(ReporteSinDatosError)
async def handle_reporte_sin_datos(
    request: Request, exc: ReporteSinDatosError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})
