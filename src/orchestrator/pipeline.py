"""Pipeline definitions for QA workflows."""

from typing import List


class Pipeline:
    """Pipeline definition."""

    def __init__(self, name: str, agents: List[str], description: str = ""):
        """
        Initialize pipeline.

        Args:
            name: Pipeline name
            agents: List of agent names in execution order
            description: Optional description
        """
        self.name = name
        self.agents = agents
        self.description = description

    def __repr__(self) -> str:
        """String representation."""
        return f"Pipeline(name={self.name}, agents={len(self.agents)})"


# Predefined pipelines
FULL_QA_PIPELINE = Pipeline(
    name="full_qa_pipeline",
    agents=[
        "requirement_analyst",
        "test_designer",
        "automation_engineer",
        "test_runner",
        "bug_investigator",
        "regression_planner",
        "quality_insights",
    ],
    description="Complete end-to-end QA process from requirements to insights",
)

SMOKE_TEST_PIPELINE = Pipeline(
    name="smoke_test_pipeline",
    agents=[
        "test_runner",
        "bug_investigator",
    ],
    description="Quick sanity check with core tests",
)

REGRESSION_PIPELINE = Pipeline(
    name="regression_pipeline",
    agents=[
        "regression_planner",
        "test_runner",
        "bug_investigator",
        "quality_insights",
    ],
    description="Risk-based regression testing for code changes",
)

QUALITY_REPORT_PIPELINE = Pipeline(
    name="quality_report_pipeline",
    agents=[
        "test_runner",
        "quality_insights",
    ],
    description="Generate quality metrics and insights",
)

BUG_ANALYSIS_PIPELINE = Pipeline(
    name="bug_analysis_pipeline",
    agents=[
        "bug_investigator",
    ],
    description="Analyze and report on test failures",
)

# Registry of predefined pipelines
DEFAULT_PIPELINES = {
    "full_qa_pipeline": FULL_QA_PIPELINE,
    "smoke_test_pipeline": SMOKE_TEST_PIPELINE,
    "regression_pipeline": REGRESSION_PIPELINE,
    "quality_report_pipeline": QUALITY_REPORT_PIPELINE,
    "bug_analysis_pipeline": BUG_ANALYSIS_PIPELINE,
}


def get_pipeline(name: str) -> Pipeline:
    """
    Get a predefined pipeline.

    Args:
        name: Pipeline name

    Returns:
        Pipeline instance

    Raises:
        ValueError: If pipeline not found
    """
    if name not in DEFAULT_PIPELINES:
        raise ValueError(
            f"Unknown pipeline: {name}. Available: {list(DEFAULT_PIPELINES.keys())}"
        )
    return DEFAULT_PIPELINES[name]


def list_pipelines() -> List[str]:
    """
    List available pipelines.

    Returns:
        List of pipeline names
    """
    return list(DEFAULT_PIPELINES.keys())
