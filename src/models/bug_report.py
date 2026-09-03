"""Bug report data models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Bug severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class BugPriority(str, Enum):
    """Bug priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class BugStatus(str, Enum):
    """Bug status."""

    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"


class RootCauseType(str, Enum):
    """Root cause classification."""

    APPLICATION_BUG = "application_bug"
    TEST_ISSUE = "test_issue"
    ENVIRONMENT_ISSUE = "environment_issue"
    DATA_ISSUE = "data_issue"
    CONFIGURATION_ISSUE = "configuration_issue"
    UNKNOWN = "unknown"


class RootCauseAnalysis(BaseModel):
    """Root cause analysis for a bug."""

    cause_type: RootCauseType = Field(..., description="Type of root cause")
    description: str = Field(..., description="Detailed cause description")
    affected_component: Optional[str] = Field(
        None, description="Component affected"
    )
    affected_code: Optional[List[str]] = Field(
        None, description="Code locations affected"
    )
    confidence_score: float = Field(
        ..., ge=0, le=100, description="Confidence in root cause (0-100)"
    )
    evidence: List[str] = Field(
        default_factory=list, description="Evidence supporting cause"
    )
    suggested_fix: Optional[str] = Field(
        None, description="Suggested fix or workaround"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "cause_type": "application_bug",
                "description": "Login endpoint not checking password correctly",
                "affected_component": "AuthService",
                "confidence_score": 95.0,
                "evidence": [
                    "Error occurs with empty password",
                    "Logs show invalid credential check",
                ],
                "suggested_fix": "Add password validation before database query",
            }
        }


class BugReport(BaseModel):
    """Detailed bug report generated from test failure."""

    id: Optional[str] = Field(None, description="Bug report ID")
    title: str = Field(..., description="Bug title")
    description: str = Field(..., description="Detailed bug description")

    # Severity and Priority
    severity: Severity = Field(..., description="Bug severity")
    priority: BugPriority = Field(..., description="Bug priority")
    status: BugStatus = Field(
        BugStatus.OPEN, description="Bug status"
    )

    # Test failure information
    test_case_id: str = Field(
        ..., description="ID of test that found the bug"
    )
    execution_id: str = Field(
        ..., description="ID of execution where bug was found"
    )
    error_message: str = Field(
        ..., description="Original error message"
    )

    # Reproduction
    reproduction_steps: List[str] = Field(
        ..., description="Steps to reproduce the bug"
    )
    expected_behavior: str = Field(
        ..., description="Expected behavior"
    )
    actual_behavior: str = Field(
        ..., description="Actual observed behavior"
    )

    # Root cause analysis
    root_cause_analysis: Optional[RootCauseAnalysis] = Field(
        None, description="Root cause analysis"
    )

    # Impact
    affected_features: List[str] = Field(
        default_factory=list, description="Features affected"
    )
    affected_users: Optional[str] = Field(
        None, description="Description of affected users"
    )
    business_impact: Optional[str] = Field(
        None, description="Business impact assessment"
    )

    # Additional information
    environment: Optional[str] = Field(
        None, description="Environment where bug occurred"
    )
    browser: Optional[str] = Field(None, description="Browser used")
    os: Optional[str] = Field(None, description="Operating system")
    artifacts: Optional[List[str]] = Field(
        None, description="Artifact paths (screenshots, logs)"
    )

    # Integration
    jira_issue_id: Optional[str] = Field(
        None, description="JIRA issue ID if created"
    )
    github_issue_id: Optional[str] = Field(
        None, description="GitHub issue ID if created"
    )
    related_bug_ids: List[str] = Field(
        default_factory=list, description="Related bug IDs"
    )

    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    created_by: Optional[str] = Field(None, description="Created by agent")
    updated_at: Optional[datetime] = Field(
        None, description="Last update timestamp"
    )
    tags: List[str] = Field(default_factory=list, description="Tags")

    # Resolution
    resolved_at: Optional[datetime] = Field(
        None, description="Resolution timestamp"
    )
    resolution_notes: Optional[str] = Field(
        None, description="Notes on resolution"
    )
    resolved_by: Optional[str] = Field(None, description="Resolved by")
    resolution_version: Optional[str] = Field(
        None, description="Version where bug was fixed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Login fails with special characters in password",
                "description": "User cannot login when password contains special characters",
                "severity": "high",
                "priority": "high",
                "status": "open",
                "test_case_id": "TC-001",
                "execution_id": "EXEC-001",
                "error_message": "Invalid credentials",
                "reproduction_steps": [
                    "Go to login page",
                    "Enter email: test@example.com",
                    "Enter password: Pass@123!",
                    "Click login button",
                ],
                "expected_behavior": "User should be logged in",
                "actual_behavior": "Error message: Invalid credentials",
                "affected_features": ["Authentication"],
                "tags": ["urgent"],
            }
        }
