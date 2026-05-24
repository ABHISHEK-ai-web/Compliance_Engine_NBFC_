from fastapi import APIRouter, Query

from models.schemas import RBISyncResponse, RBISyncStatus
from services.regulation_sync import RegulationSyncService

router = APIRouter()
sync_service = RegulationSyncService()


@router.get("/sync-regulations/status", response_model=RBISyncStatus)
async def get_sync_status():
    """Last RBI sync time and indexed regulation count."""
    return sync_service.get_status()


@router.post("/sync-regulations", response_model=RBISyncResponse)
async def sync_regulations(
    max_items: int = Query(None, ge=1, le=50),
    force: bool = Query(False, description="Re-ingest URLs already synced"),
):
    """
    Fetch recent RBI releases from official RSS feeds and index into regulations.
    Run Analyze afterward to compare your policies against the updated knowledge base.
    """
    result = sync_service.sync(max_items=max_items, force=force)
    return RBISyncResponse(**result)
