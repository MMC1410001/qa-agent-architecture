"""Reports API routes."""

from typing import List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


class QualityReportResponse(BaseModel):
    """Quality report response."""

    report_id: str
    project_id: str
    period: str
    overall_health: float
    test_pass_rate: float
    code_coverage: float


# In-memory storage for demo
reports_db = {}


@router.get("", response_model=List[QualityReportResponse])
async def list_reports(
    project_id: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
) -> List[QualityReportResponse]:
    """
    List quality reports.

    Args:
        project_id: Optional project filter
        skip: Number to skip
        limit: Maximum to return

    Returns:
        List of reports
    """
    items = list(reports_db.values())
    if project_id:
        items = [r for r in items if r.get("project_id") == project_id]
    return items[skip : skip + limit]


@router.get("/{report_id}", response_model=QualityReportResponse)
async def get_report(report_id: str) -> QualityReportResponse:
    """
    Get report by ID.

    Args:
        report_id: Report ID

    Returns:
        Report details

    Raises:
        HTTPException: If report not found
    """
    if report_id not in reports_db:
        raise HTTPException(status_code=404, detail="Report not found")
    return QualityReportResponse(**reports_db[report_id])


@router.get("/project/{project_id}/latest", response_model=QualityReportResponse)
async def get_latest_report(project_id: str) -> QualityReportResponse:
    """
    Get latest quality report for project.

    Args:
        project_id: Project ID

    Returns:
        Latest report

    Raises:
        HTTPException: If no reports found
    """
    project_reports = [
        r for r in reports_db.values() if r.get("project_id") == project_id
    ]

    if not project_reports:
        raise HTTPException(status_code=404, detail="No reports found for project")

    return QualityReportResponse(**project_reports[-1])
