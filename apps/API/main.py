from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from apps.API.routers.desktop import router as desktop_router
from shared.exceptions.catalog import EstadoNoEncontradoError
from shared.exceptions.configuration import ConfiguracionNoEncontradaError
from shared.exceptions.device import DispositivoNoAutorizadoError, DispositivoNoEncontradoError

app = FastAPI(title="Familia Puess - Sistema de Control de Asistencia")

app.include_router(desktop_router)


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
