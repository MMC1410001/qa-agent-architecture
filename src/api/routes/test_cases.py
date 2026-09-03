"""Test Cases API routes."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


class TestCaseCreate(BaseModel):
    """Create test case request."""

    title: str
    description: str
    test_type: str = "functional"
    priority: str = "medium"


class TestCaseResponse(BaseModel):
    """Test case response."""

    id: str
    title: str
    description: str
    test_type: str
    priority: str


# In-memory storage for demo
test_cases_db = {}


@router.post("", response_model=TestCaseResponse)
async def create_test_case(test_case: TestCaseCreate) -> TestCaseResponse:
    """
    Create a new test case.

    Args:
        test_case: Test case data

    Returns:
        Created test case
    """
    import uuid

    test_id = f"TC-{str(uuid.uuid4())[:8].upper()}"
    test_cases_db[test_id] = {
        "id": test_id,
        "title": test_case.title,
        "description": test_case.description,
        "test_type": test_case.test_type,
        "priority": test_case.priority,
    }
    return TestCaseResponse(**test_cases_db[test_id])


@router.get("", response_model=List[TestCaseResponse])
async def list_test_cases(
    skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)
) -> List[TestCaseResponse]:
    """
    List all test cases.

    Args:
        skip: Number of test cases to skip
        limit: Maximum number of test cases to return

    Returns:
        List of test cases
    """
    items = list(test_cases_db.values())
    return items[skip : skip + limit]


@router.get("/{test_case_id}", response_model=TestCaseResponse)
async def get_test_case(test_case_id: str) -> TestCaseResponse:
    """
    Get test case by ID.

    Args:
        test_case_id: Test case ID

    Returns:
        Test case details

    Raises:
        HTTPException: If test case not found
    """
    if test_case_id not in test_cases_db:
        raise HTTPException(status_code=404, detail="Test case not found")
    return TestCaseResponse(**test_cases_db[test_case_id])


@router.delete("/{test_case_id}")
async def delete_test_case(test_case_id: str):
    """
    Delete test case.

    Args:
        test_case_id: Test case ID

    Raises:
        HTTPException: If test case not found
    """
    if test_case_id not in test_cases_db:
        raise HTTPException(status_code=404, detail="Test case not found")

    del test_cases_db[test_case_id]
    return {"deleted": True}
