from __future__ import annotations


from modules.dashboard.schemas.dashboard_schema import (
    DashboardStatsResponse,
)
from modules.dashboard.services import dashboard_service


async def get_stats(
    user_id: str = "",
) -> DashboardStatsResponse:
    data = await dashboard_service.get_dashboard_stats(user_id=user_id)
    return DashboardStatsResponse(**data)
