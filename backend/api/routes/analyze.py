from fastapi import APIRouter
from models.schemas import AnalysisRequest, AnalysisResponse, AuditQuery, AuditResponse
from services.gap_analyzer import GapAnalyzer

router = APIRouter()
gap_analyzer = GapAnalyzer()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_compliance(request: AnalysisRequest):
    result = gap_analyzer.analyze(
        regulation_id=request.regulation_id,
        policy_id=request.policy_id,
        query=request.query,
    )
    return result


@router.post("/audit-query", response_model=AuditResponse)
async def audit_query(request: AuditQuery):
    result = gap_analyzer.query_knowledge_base(request.question)
    return result
