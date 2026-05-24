from fastapi import APIRouter
from models.schemas import DashboardMetrics
from services.gap_analyzer import GapAnalyzer

router = APIRouter()
gap_analyzer = GapAnalyzer()


@router.get("/dashboard-metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics():
    return gap_analyzer.get_dashboard_metrics()
