"""Quality metrics and reporting models."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QualityMetrics(BaseModel):
    """Quality metrics snapshot."""

    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Metrics timestamp"
    )

    # Test metrics
    test_pass_rate: float = Field(
        ..., ge=0, le=100, description="Test pass rate percentage"
    )
    test_fail_rate: float = Field(
        ..., ge=0, le=100, description="Test fail rate percentage"
    )
    test_skip_rate: float = Field(
        ..., ge=0, le=100, description="Test skip rate percentage"
    )
    test_execution_count: int = Field(
        ..., description="Total tests executed"
    )

    # Coverage metrics
    code_coverage: float = Field(
        ..., ge=0, le=100, description="Code coverage percentage"
    )
    line_coverage: float = Field(
        ..., ge=0, le=100, description="Line coverage percentage"
    )
    branch_coverage: float = Field(
        ..., ge=0, le=100, description="Branch coverage percentage"
    )

    # Quality metrics
    defect_density: float = Field(
        ..., description="Defects per thousand lines of code"
    )
    test_case_coverage: float = Field(
        ..., ge=0, le=100, description="Test case coverage of requirements"
    )
    automation_ratio: float = Field(
        ..., ge=0, le=100, description="Ratio of automated vs manual tests"
    )

    # Performance metrics
    average_test_duration: float = Field(
        ..., description="Average test execution time in seconds"
    )
    test_cycle_time: float = Field(
        ..., description="Total test cycle time in hours"
    )
    p50_test_duration: float = Field(
        ..., description="50th percentile test duration"
    )
    p95_test_duration: float = Field(
        ..., description="95th percentile test duration"
    )

    # Failure metrics
    failure_rate: float = Field(
        ..., ge=0, le=100, description="Test failure rate"
    )
    flaky_test_count: int = Field(
        ..., description="Number of flaky tests"
    )
    flaky_test_ratio: float = Field(
        ..., ge=0, le=100, description="Ratio of flaky tests"
    )

    # Trend data
    previous_metrics: Optional["QualityMetrics"] = Field(
        None, description="Previous metrics for comparison"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "test_pass_rate": 95.0,
                "test_fail_rate": 5.0,
                "test_skip_rate": 0.0,
                "test_execution_count": 100,
                "code_coverage": 85.5,
                "line_coverage": 87.0,
                "branch_coverage": 82.0,
                "defect_density": 2.5,
                "test_case_coverage": 92.0,
                "automation_ratio": 85.0,
                "average_test_duration": 45.0,
                "test_cycle_time": 2.5,
                "p50_test_duration": 40.0,
                "p95_test_duration": 120.0,
                "failure_rate": 5.0,
                "flaky_test_count": 2,
                "flaky_test_ratio": 2.0,
            }
        }


QualityMetrics.model_rebuild()


class Trend(BaseModel):
    """Trend analysis for a metric."""

    metric_name: str = Field(..., description="Name of metric")
    current_value: float = Field(..., description="Current value")
    previous_value: Optional[float] = Field(None, description="Previous value")
    change_percentage: Optional[float] = Field(
        None, description="Percentage change"
    )
    trend_direction: str = Field(
        ..., description="Direction: up, down, or stable"
    )
    period_days: int = Field(..., description="Period in days")
    analysis: str = Field(..., description="Trend analysis text")

    class Config:
        json_schema_extra = {
            "example": {
                "metric_name": "Test Pass Rate",
                "current_value": 95.0,
                "previous_value": 92.0,
                "change_percentage": 3.3,
                "trend_direction": "up",
                "period_days": 7,
                "analysis": "Pass rate has improved by 3.3% over the last 7 days",
            }
        }


class Recommendation(BaseModel):
    """Quality improvement recommendation."""

    priority: str = Field(..., description="Priority: high, medium, low")
    category: str = Field(
        ..., description="Category: coverage, performance, flakiness, etc."
    )
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed description")
    expected_impact: str = Field(..., description="Expected impact")
    effort: str = Field(..., description="Effort: high, medium, low")
    action_items: List[str] = Field(
        default_factory=list, description="Action items"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "priority": "high",
                "category": "coverage",
                "title": "Increase test coverage for critical path",
                "description": "Critical authentication module has only 65% coverage",
                "expected_impact": "Reduce production bugs by 40%",
                "effort": "medium",
                "action_items": [
                    "Write 10 additional test cases",
                    "Add edge case testing",
                ],
            }
        }


class QualityReport(BaseModel):
    """Comprehensive quality report."""

    id: Optional[str] = Field(None, description="Report ID")
    project_id: Optional[str] = Field(None, description="Project ID")
    report_date: datetime = Field(
        default_factory=datetime.utcnow, description="Report date"
    )
    report_period: str = Field(
        ..., description="Report period (daily, weekly, monthly)"
    )

    # Current metrics
    metrics: QualityMetrics = Field(..., description="Quality metrics")

    # Trends
    trends: List[Trend] = Field(
        default_factory=list, description="Metric trends"
    )

    # Recommendations
    recommendations: List[Recommendation] = Field(
        default_factory=list, description="Improvement recommendations"
    )

    # Summary
    overall_health_score: float = Field(
        ..., ge=0, le=100, description="Overall quality health (0-100)"
    )
    summary: str = Field(..., description="Executive summary")

    # Quality gates
    quality_gates: Dict[str, bool] = Field(
        default_factory=dict, description="Quality gate status"
    )
    all_gates_passed: bool = Field(
        ..., description="Whether all quality gates passed"
    )

    # Metadata
    generated_by: Optional[str] = Field(
        None, description="Generated by agent"
    )
    tags: List[str] = Field(default_factory=list, description="Tags")
    custom_data: Dict[str, Any] = Field(
        default_factory=dict, description="Custom data"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "report_date": "2024-01-01T00:00:00Z",
                "report_period": "weekly",
                "metrics": {
                    "test_pass_rate": 95.0,
                    "test_fail_rate": 5.0,
                    "test_skip_rate": 0.0,
                    "test_execution_count": 100,
                    "code_coverage": 85.5,
                    "line_coverage": 87.0,
                    "branch_coverage": 82.0,
                    "defect_density": 2.5,
                    "test_case_coverage": 92.0,
                    "automation_ratio": 85.0,
                    "average_test_duration": 45.0,
                    "test_cycle_time": 2.5,
                    "p50_test_duration": 40.0,
                    "p95_test_duration": 120.0,
                    "failure_rate": 5.0,
                    "flaky_test_count": 2,
                    "flaky_test_ratio": 2.0,
                },
                "overall_health_score": 85.0,
                "summary": "Quality is stable with good coverage metrics",
                "all_gates_passed": True,
            }
        }
