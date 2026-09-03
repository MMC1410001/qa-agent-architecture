"""Test suite data models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SuiteStatus(str, Enum):
    """Test suite status."""

    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    DEPRECATED = "deprecated"


class TestSuite(BaseModel):
    """Test suite grouping multiple test cases."""

    id: Optional[str] = Field(None, description="Unique suite ID")
    name: str = Field(..., description="Suite name")
    description: str = Field(..., description="Suite description")
    status: SuiteStatus = Field(SuiteStatus.CREATED, description="Suite status")

    # Test organization
    test_case_ids: List[str] = Field(
        default_factory=list, description="IDs of test cases in suite"
    )
    feature: Optional[str] = Field(None, description="Feature covered by suite")
    component: Optional[str] = Field(None, description="Component covered")

    # Scheduling
    schedule: Optional[str] = Field(
        None, description="Cron expression for scheduled runs"
    )
    enabled: bool = Field(True, description="Whether suite is enabled")

    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    created_by: Optional[str] = Field(None, description="Created by")

    # Tags and categories
    tags: List[str] = Field(
        default_factory=list, description="Suite tags"
    )
    suite_type: Optional[str] = Field(
        None, description="Type: smoke, regression, critical, etc."
    )

    # Metadata
    project_id: Optional[str] = Field(None, description="Parent project ID")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Authentication Suite",
                "description": "All authentication-related tests",
                "status": "active",
                "test_case_ids": ["TC-001", "TC-002", "TC-003"],
                "feature": "Authentication",
                "tags": ["critical", "smoke"],
                "suite_type": "smoke",
            }
        }
