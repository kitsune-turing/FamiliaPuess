from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.database.session import get_session
from apps.API.dependencies.auth import require_permission
from apps.API.schemas.dashboard import DashboardResponse
from apps.API.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get(
    "",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK,
)
async def get_dashboard(
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("DASHBOARD", "leer")),
) -> DashboardResponse:
    return await dashboard_service.get_indicadores(session)
