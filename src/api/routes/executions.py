"""Test Executions API routes."""

from typing import List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


class ExecutionCreate(BaseModel):
    """Create execution request."""

    test_suite_id: str
    environment: str = "dev"


class ExecutionResponse(BaseModel):
    """Execution response."""

    execution_id: str
    test_suite_id: str
    status: str
    total_tests: int
    passed: int
    failed: int


# In-memory storage for demo
executions_db = {}


@router.post("", response_model=ExecutionResponse)
async def create_execution(execution: ExecutionCreate) -> ExecutionResponse:
    """
    Create a new test execution.

    Args:
        execution: Execution data

    Returns:
        Created execution
    """
    import uuid
    from datetime import datetime

    exec_id = f"EXEC-{str(uuid.uuid4())[:8].upper()}"
    executions_db[exec_id] = {
        "execution_id": exec_id,
        "test_suite_id": execution.test_suite_id,
        "status": "running",
        "environment": execution.environment,
        "total_tests": 10,
        "passed": 0,
        "failed": 0,
        "started_at": datetime.utcnow().isoformat(),
    }
    return ExecutionResponse(**executions_db[exec_id])


@router.get("", response_model=List[ExecutionResponse])
async def list_executions(
    skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)
) -> List[ExecutionResponse]:
    """
    List executions.

    Args:
        skip: Number to skip
        limit: Maximum to return

    Returns:
        List of executions
    """
    items = list(executions_db.values())
    return items[skip : skip + limit]


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(execution_id: str) -> ExecutionResponse:
    """
    Get execution by ID.

    Args:
        execution_id: Execution ID

    Returns:
        Execution details

    Raises:
        HTTPException: If execution not found
    """
    if execution_id not in executions_db:
        raise HTTPException(status_code=404, detail="Execution not found")
    return ExecutionResponse(**executions_db[execution_id])
