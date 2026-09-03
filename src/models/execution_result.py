"""Test execution result models."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TestResultStatus(str, Enum):
    """Test result status."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestResult(BaseModel):
    """Result of a single test execution."""

    test_case_id: str = Field(..., description="ID of test case executed")
    status: TestResultStatus = Field(..., description="Test result status")
    duration_seconds: float = Field(..., description="Execution duration")
    started_at: datetime = Field(..., description="Execution start time")
    ended_at: datetime = Field(..., description="Execution end time")

    # Error details
    error_message: Optional[str] = Field(
        None, description="Error message if test failed"
    )
    error_type: Optional[str] = Field(
        None, description="Type of error (assertion, timeout, exception)"
    )
    error_stacktrace: Optional[str] = Field(
        None, description="Full stacktrace if error occurred"
    )

    # Step details
    failed_step_number: Optional[int] = Field(
        None, description="Step number where failure occurred"
    )
    failed_step_description: Optional[str] = Field(
        None, description="Description of failed step"
    )

    # Artifacts
    screenshot_path: Optional[str] = Field(
        None, description="Path to failure screenshot"
    )
    video_path: Optional[str] = Field(
        None, description="Path to execution video"
    )
    logs: Optional[str] = Field(None, description="Execution logs")
    browser_logs: Optional[List[str]] = Field(
        None, description="Browser console logs"
    )

    # Metadata
    browser: Optional[str] = Field(None, description="Browser used (if UI test)")
    environment: Optional[str] = Field(None, description="Test environment")
    tags: List[str] = Field(default_factory=list, description="Result tags")

    # Performance metrics
    metrics: Optional[Dict[str, Any]] = Field(
        None, description="Custom metrics from test"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "test_case_id": "TC-001",
                "status": "passed",
                "duration_seconds": 12.5,
                "started_at": "2024-01-01T10:00:00Z",
                "ended_at": "2024-01-01T10:00:12.5Z",
            }
        }


class ExecutionResult(BaseModel):
    """Overall test execution results."""

    id: Optional[str] = Field(None, description="Execution result ID")
    test_suite_id: str = Field(..., description="ID of executed test suite")
    execution_id: str = Field(..., description="Unique execution ID")

    # Summary statistics
    total_tests: int = Field(..., description="Total tests executed")
    passed_tests: int = Field(default=0, description="Number of passed tests")
    failed_tests: int = Field(default=0, description="Number of failed tests")
    skipped_tests: int = Field(default=0, description="Number of skipped tests")
    error_tests: int = Field(default=0, description="Number of tests with errors")

    # Metrics
    pass_rate: float = Field(..., description="Pass rate percentage")
    failure_rate: float = Field(..., description="Failure rate percentage")
    total_duration_seconds: float = Field(
        ..., description="Total execution duration"
    )

    # Individual results
    test_results: List[TestResult] = Field(
        ..., description="Results for each test"
    )

    # Timing
    started_at: datetime = Field(..., description="Execution start time")
    ended_at: datetime = Field(..., description="Execution end time")

    # Environment and configuration
    environment: Optional[str] = Field(
        None, description="Test environment"
    )
    browser: Optional[str] = Field(None, description="Browser used")
    platform: Optional[str] = Field(None, description="Platform (OS)")
    parallel_execution: bool = Field(
        False, description="Whether tests ran in parallel"
    )
    max_parallel_threads: Optional[int] = Field(
        None, description="Max parallel threads used"
    )

    # Metadata
    created_by: Optional[str] = Field(None, description="Created by agent")
    tags: List[str] = Field(default_factory=list, description="Result tags")
    artifacts_path: Optional[str] = Field(
        None, description="Path to artifacts directory"
    )

    # Quality gates
    quality_gate_passed: bool = Field(
        False, description="Whether quality gates passed"
    )
    quality_gate_details: Optional[Dict[str, Any]] = Field(
        None, description="Quality gate check details"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "test_suite_id": "SUITE-001",
                "execution_id": "EXEC-20240101-001",
                "total_tests": 10,
                "passed_tests": 9,
                "failed_tests": 1,
                "pass_rate": 90.0,
                "started_at": "2024-01-01T10:00:00Z",
                "ended_at": "2024-01-01T10:15:00Z",
                "total_duration_seconds": 900.0,
                "test_results": [],
            }
        }

    @property
    def overall_status(self) -> str:
        """Get overall execution status."""
        if self.failed_tests > 0 or self.error_tests > 0:
            return "failed"
        elif self.passed_tests == self.total_tests:
            return "passed"
        else:
            return "partial"

    @property
    def has_failures(self) -> bool:
        """Check if execution has failures."""
        return self.failed_tests > 0 or self.error_tests > 0
