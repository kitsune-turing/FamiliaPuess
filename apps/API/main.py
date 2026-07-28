from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.API.routers.desktop import router as desktop_router
from apps.API.routers.registro import router as registro_router
from shared.exceptions.attendance import AsistenciaDuplicadaError
from shared.exceptions.catalog import EstadoNoEncontradoError
from shared.exceptions.configuration import ConfiguracionNoEncontradaError
from shared.exceptions.device import DispositivoNoAutorizadoError, DispositivoNoEncontradoError
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

app.include_router(desktop_router)
app.include_router(registro_router)


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
