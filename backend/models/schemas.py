from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DocumentType(str, Enum):
    REGULATION = "regulation"
    POLICY = "policy"
    AUDIT_REPORT = "audit_report"


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    document_type: DocumentType
    chunks_created: int
    status: str
    message: str


class Violation(BaseModel):
    violation_id: str
    violation_detected: str
    affected_department: str
    severity: Severity
    regulation_reference: str
    missing_requirement: str
    explanation: str
    recommendation: str
    confidence_score: float
    detected_at: datetime = datetime.now()


class AnalysisRequest(BaseModel):
    regulation_id: Optional[str] = None
    policy_id: Optional[str] = None
    query: Optional[str] = None


class AnalysisResponse(BaseModel):
    analysis_id: str
    violations: list[Violation]
    compliance_score: float
    summary: str
    total_violations: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    regulatory_checks_passed: int = 0
    regulatory_checks_total: int = 10


class DashboardMetrics(BaseModel):
    overall_compliance_score: float
    total_documents: int
    total_regulations: int
    total_policies: int
    total_violations: int
    regulatory_checks_passed: int
    regulatory_checks_total: int
    risk_distribution: dict[str, int]
    department_risks: dict[str, float]
    recent_violations: list[Violation]
    violation_trends: list[dict]


class AuditQuery(BaseModel):
    question: str


class AuditResponse(BaseModel):
    answer: str
    sources: list[dict]
    confidence: float


class RBISyncStatus(BaseModel):
    last_sync_at: str | None
    total_synced_urls: int
    regulations_indexed: int
    feeds: list[str]
    last_run: dict | None = None


class RBISyncResponse(BaseModel):
    status: str
    last_sync_at: str | None = None
    fetched: int
    new: int
    skipped: int
    failed: int
    items: list[dict]
