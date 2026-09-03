"""Prompt template management for QA agents."""

from string import Template
from typing import Any, Dict, Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)


class PromptTemplate:
    """Template for LLM prompts with variable substitution."""

    def __init__(self, name: str, template: str, description: str = ""):
        """
        Initialize prompt template.

        Args:
            name: Template name
            template: Template string with $variable placeholders
            description: Optional description
        """
        self.name = name
        self.template = Template(template)
        self.description = description

    def render(self, **kwargs) -> str:
        """
        Render template with provided variables.

        Args:
            **kwargs: Variables to substitute in template

        Returns:
            Rendered template string
        """
        try:
            return self.template.substitute(kwargs)
        except KeyError as e:
            logger.error(
                "Missing template variable",
                variable=str(e),
                template=self.name,
            )
            raise

    def __repr__(self) -> str:
        """String representation."""
        return f"PromptTemplate(name={self.name})"


class PromptLibrary:
    """Library of prompt templates for agents."""

    def __init__(self):
        """Initialize prompt library with built-in templates."""
        self.templates: Dict[str, PromptTemplate] = {}
        self._register_default_templates()

    def _register_default_templates(self) -> None:
        """Register default prompts for agents."""

        # Requirement Analyst Prompts
        self.register(
            "requirement_analyst",
            """You are an expert QA Requirements Analyst. Analyze the provided requirements document
and extract testable requirements, user stories, and test scenarios.

Requirements Document:
$document

Testing Scope: $scope

For each requirement, identify:
1. Clear, testable acceptance criteria
2. Functional areas to test
3. Test scenarios (positive, negative, edge cases)
4. Risk level and priority
5. Dependencies and relationships

Output your analysis as JSON with this structure:
{
  "requirements": [
    {
      "id": "REQ-XXX",
      "title": "...",
      "description": "...",
      "acceptance_criteria": ["..."],
      "test_scenarios": ["..."],
      "risk_level": "high|medium|low",
      "priority": "critical|high|medium|low"
    }
  ],
  "test_mapping": {
    "REQ-XXX": ["TEST-SCENARIO-1", "TEST-SCENARIO-2"]
  },
  "gaps": ["..."],
  "summary": "..."
}""",
            "Analyze requirements and extract testable test cases",
        )

        # Test Designer Prompts
        self.register(
            "test_designer",
            """You are an expert QA Test Designer specializing in comprehensive test case design.
Create detailed test cases from the provided requirements using multiple testing techniques.

Requirements to Design Tests For:
$requirements

Target Test Type: $test_type

Use these design techniques:
- Boundary Value Analysis: Test at boundaries and limits
- Equivalence Partitioning: Group similar test inputs
- State Transition Testing: Test state changes
- Decision Table Testing: Cover all conditions
- Use Cases: Happy path and alternative flows

Include:
- Positive test cases (valid inputs, expected behavior)
- Negative test cases (invalid inputs, error handling)
- Edge cases (boundary conditions, limits)

Output as JSON with structure:
{
  "test_cases": [
    {
      "id": "TC-XXX",
      "title": "...",
      "description": "...",
      "preconditions": ["..."],
      "steps": [
        {
          "step_number": 1,
          "action": "...",
          "expected_result": "..."
        }
      ],
      "postconditions": ["..."],
      "priority": "critical|high|medium|low",
      "test_type": "$test_type",
      "test_data": {...}
    }
  ],
  "coverage_analysis": {
    "total_test_cases": 0,
    "coverage_percentage": 0,
    "gaps": ["..."]
  }
}""",
            "Design comprehensive test cases with coverage analysis",
        )

        # Automation Engineer Prompts
        self.register(
            "automation_engineer",
            """You are an expert Automation Engineer. Convert the provided test cases into
clean, maintainable automation code using the specified framework.

Test Cases to Automate:
$test_cases

Target Framework: $framework

Requirements:
1. Generate clean, production-ready code
2. Follow Page Object Model pattern
3. Include proper waits and synchronization
4. Add comprehensive error handling
5. Use clear variable and function names
6. Include comments and docstrings
7. Create reusable fixtures and utilities

Output should include:
1. Automation script with test methods
2. Page Object Models for UI elements
3. Test fixtures and utilities
4. Configuration and constants
5. Instructions for running tests

Format output with clear sections and syntax highlighting.""",
            "Generate automation scripts and page objects",
        )

        # Bug Investigator Prompts
        self.register(
            "bug_investigator",
            """You are an expert QA Bug Investigator. Analyze the provided test failure data
and create a comprehensive bug report with root cause analysis.

Test Failure Information:
Test Case: $test_case_id
Execution: $execution_id
Error Message: $error_message
Logs:
$logs

Artifacts (screenshots, traces):
$artifacts

Determine:
1. Root cause (app bug, test issue, environment issue, data issue)
2. Impact assessment (severity, affected features)
3. Steps to reproduce with precision
4. Actual vs expected behavior
5. Confidence level in root cause analysis

Output as JSON:
{
  "bug_report": {
    "title": "...",
    "description": "...",
    "root_cause": "...",
    "root_cause_type": "application_bug|test_issue|environment_issue|data_issue|unknown",
    "severity": "critical|high|medium|low",
    "priority": "critical|high|medium|low",
    "reproduction_steps": ["..."],
    "expected_behavior": "...",
    "actual_behavior": "...",
    "affected_features": ["..."],
    "environment": "...",
    "suggested_fix": "..."
  }
}""",
            "Analyze failures and generate detailed bug reports",
        )

        # Regression Planner Prompts
        self.register(
            "regression_planner",
            """You are an expert Regression Test Planner. Analyze the code changes and create
an optimized regression test plan using risk-based selection.

Changed Files and Modifications:
$changes

Available Test Cases:
$test_inventory

Analyze:
1. Impact of changes on existing functionality
2. Risk areas requiring thorough testing
3. Test coverage for changed code
4. Dependencies and related areas

Select and prioritize tests by:
1. Risk level (high risk areas = more tests)
2. Code coverage impact
3. Historical failure rate
4. Test execution time

Goal: Balance coverage and execution time.

Output as JSON:
{
  "regression_plan": {
    "total_available": 0,
    "selected": 0,
    "reduction_percentage": 0,
    "estimated_time_hours": 0,
    "test_groups": [
      {
        "name": "...",
        "priority": "critical|high|medium|low",
        "risk_level": "high|medium|low",
        "test_ids": ["TC-001", "TC-002"],
        "estimated_time_minutes": 0
      }
    ],
    "summary": "..."
  }
}""",
            "Plan optimized regression test suites",
        )

        # Quality Insights Prompts
        self.register(
            "quality_insights",
            """You are a Quality Analytics Expert. Analyze the provided test execution history
and metrics to generate quality insights, trends, and recommendations.

Execution History (last $period days):
$history

Current Metrics:
$metrics

Generate:
1. Quality health assessment (0-100 score)
2. Metric trends (improving, stable, declining)
3. Patterns in failures and successes
4. Specific improvement recommendations
5. Quality gate status

Output as JSON:
{
  "dashboard": {
    "overall_health": 0,
    "health_trend": "up|down|stable",
    "key_metrics": {
      "test_pass_rate": 0,
      "test_coverage": 0,
      "defect_density": 0,
      "automation_ratio": 0,
      "flaky_test_ratio": 0
    }
  },
  "trends": [
    {
      "metric": "...",
      "trend": "up|down|stable",
      "change_percent": 0,
      "analysis": "..."
    }
  ],
  "recommendations": [
    {
      "priority": "high|medium|low",
      "category": "coverage|performance|flakiness|automation",
      "title": "...",
      "description": "...",
      "expected_impact": "...",
      "effort": "high|medium|low"
    }
  ],
  "quality_gates": {
    "min_coverage_80": true,
    "min_pass_rate_95": true,
    "max_flaky_ratio_5": false
  },
  "summary": "..."
}""",
            "Generate quality metrics and insights",
        )

    def register(
        self,
        name: str,
        template: str,
        description: str = "",
    ) -> None:
        """
        Register a prompt template.

        Args:
            name: Template name
            template: Template string
            description: Optional description
        """
        self.templates[name] = PromptTemplate(name, template, description)
        logger.info("Prompt template registered", name=name)

    def get(self, name: str) -> PromptTemplate:
        """
        Get a registered prompt template.

        Args:
            name: Template name

        Returns:
            Prompt template

        Raises:
            ValueError: If template not found
        """
        if name not in self.templates:
            raise ValueError(f"Prompt template not found: {name}")
        return self.templates[name]

    def render(self, name: str, **kwargs) -> str:
        """
        Render a prompt template with variables.

        Args:
            name: Template name
            **kwargs: Variables to substitute

        Returns:
            Rendered prompt
        """
        template = self.get(name)
        return template.render(**kwargs)

    def list_templates(self) -> Dict[str, str]:
        """
        List all registered templates.

        Returns:
            Dictionary of template names and descriptions
        """
        return {
            name: template.description
            for name, template in self.templates.items()
        }


# Global prompt library instance
_prompt_library: Optional[PromptLibrary] = None


def get_prompt_library() -> PromptLibrary:
    """
    Get the global prompt library instance.

    Returns:
        Prompt library instance
    """
    global _prompt_library
    if _prompt_library is None:
        _prompt_library = PromptLibrary()
    return _prompt_library
