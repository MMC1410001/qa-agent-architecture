"""Test case data models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TestType(str, Enum):
    """Test types supported by QA-OS."""

    FUNCTIONAL = "functional"
    INTEGRATION = "integration"
    UNIT = "unit"
    E2E = "e2e"
    API = "api"
    SECURITY = "security"
    PERFORMANCE = "performance"
    USABILITY = "usability"
    SMOKE = "smoke"
    REGRESSION = "regression"


class TestPriority(str, Enum):
    """Test priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestStatus(str, Enum):
    """Test execution status."""

    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class TestStep(BaseModel):
    """Individual test step."""

    step_number: int = Field(..., description="Sequence number of the step")
    action: str = Field(..., description="Action to perform")
    expected_result: str = Field(..., description="Expected result after action")
    test_data: Optional[str] = Field(None, description="Test data for this step")
    screenshot_on_failure: bool = Field(
        True, description="Capture screenshot if step fails"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "step_number": 1,
                "action": "Click on login button",
                "expected_result": "Login form should be displayed",
                "test_data": None,
                "screenshot_on_failure": True,
            }
        }


class TestCase(BaseModel):
    """Complete test case definition."""

    id: Optional[str] = Field(None, description="Unique test case ID")
    title: str = Field(..., description="Test case title")
    description: str = Field(..., description="Detailed description")
    test_type: TestType = Field(
        TestType.FUNCTIONAL, description="Type of test"
    )
    priority: TestPriority = Field(
        TestPriority.MEDIUM, description="Test priority"
    )
    status: TestStatus = Field(
        TestStatus.CREATED, description="Current status"
    )

    preconditions: List[str] = Field(
        default_factory=list, description="Preconditions required"
    )
    steps: List[TestStep] = Field(..., description="Test execution steps")
    postconditions: List[str] = Field(
        default_factory=list, description="Postconditions after execution"
    )

    # Relationship fields
    requirement_ids: List[str] = Field(
        default_factory=list, description="Related requirement IDs"
    )
    test_suite_id: Optional[str] = Field(
        None, description="Parent test suite ID"
    )
    component: Optional[str] = Field(None, description="Component under test")
    feature: Optional[str] = Field(None, description="Feature under test")

    # Automation fields
    automation_script: Optional[str] = Field(
        None, description="Generated automation code"
    )
    automation_framework: Optional[str] = Field(
        None, description="Target automation framework"
    )
    page_objects: Optional[List[str]] = Field(
        None, description="Associated page objects"
    )

    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    created_by: Optional[str] = Field(None, description="Created by agent")
    tags: List[str] = Field(
        default_factory=list, description="Tags for categorization"
    )
    estimated_duration_minutes: int = Field(
        5, description="Estimated execution time"
    )

    # Coverage metrics
    code_coverage_lines: Optional[List[str]] = Field(
        None, description="Lines of code covered"
    )
    code_coverage_branches: Optional[List[str]] = Field(
        None, description="Branches covered"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "User login with valid credentials",
                "description": "Verify that a user can log in with valid email and password",
                "test_type": "functional",
                "priority": "critical",
                "status": "created",
                "preconditions": [
                    "Application is loaded",
                    "User account exists with valid credentials",
                ],
                "steps": [
                    {
                        "step_number": 1,
                        "action": "Click on login button",
                        "expected_result": "Login form is displayed",
                    },
                    {
                        "step_number": 2,
                        "action": "Enter email: test@example.com",
                        "expected_result": "Email is entered in the field",
                    },
                ],
                "postconditions": ["User is logged in"],
                "tags": ["smoke", "critical"],
            }
        }
