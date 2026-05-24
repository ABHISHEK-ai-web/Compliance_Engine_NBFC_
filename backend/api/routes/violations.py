from fastapi import APIRouter, Query
from models.schemas import Violation, Severity
from services.gap_analyzer import GapAnalyzer

router = APIRouter()
gap_analyzer = GapAnalyzer()


@router.get("/violations", response_model=list[Violation])
async def get_violations(
    severity: Severity | None = Query(None),
    department: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    violations = gap_analyzer.get_violations(
        severity=severity,
        department=department,
        limit=limit,
    )
    return violations
