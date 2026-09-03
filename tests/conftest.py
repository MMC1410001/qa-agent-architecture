"""Pytest configuration and fixtures."""

import pytest

from src.agents.automation_engineer import AutomationEngineerAgent
from src.agents.bug_investigator import BugInvestigatorAgent
from src.agents.quality_insights import QualityInsightsAgent
from src.agents.regression_planner import RegressionPlannerAgent
from src.agents.requirement_analyst import RequirementAnalystAgent
from src.agents.test_designer import TestDesignerAgent
from src.agents.test_runner import TestRunnerAgent
from src.models.agent_config import AgentInput
from src.orchestrator.engine import OrchestrationEngine


@pytest.fixture
def orchestrator():
    """Provide orchestration engine."""
    engine = OrchestrationEngine()

    # Register agents
    agents = [
        RequirementAnalystAgent(),
        TestDesignerAgent(),
        AutomationEngineerAgent(),
        TestRunnerAgent(),
        BugInvestigatorAgent(),
        RegressionPlannerAgent(),
        QualityInsightsAgent(),
    ]

    for agent in agents:
        engine.register_agent(agent)

    return engine


@pytest.fixture
def requirement_analyst():
    """Provide requirement analyst agent."""
    return RequirementAnalystAgent()


@pytest.fixture
def test_designer():
    """Provide test designer agent."""
    return TestDesignerAgent()


@pytest.fixture
def test_runner():
    """Provide test runner agent."""
    return TestRunnerAgent()


@pytest.fixture
def sample_requirement_input():
    """Provide sample requirement input."""
    return AgentInput(
        data={
            "document": "User Login Feature: Allow users to authenticate with email and password",
            "scope": "functional",
        }
    )


@pytest.fixture
def sample_test_cases():
    """Provide sample test cases."""
    return [
        {
            "id": "TC-001",
            "title": "Login with valid credentials",
            "description": "User logs in successfully",
            "steps": [
                {
                    "step_number": 1,
                    "action": "Enter email",
                    "expected_result": "Email accepted",
                },
            ],
        },
        {
            "id": "TC-002",
            "title": "Login with invalid password",
            "description": "User gets error message",
            "steps": [
                {
                    "step_number": 1,
                    "action": "Enter invalid password",
                    "expected_result": "Error shown",
                },
            ],
        },
    ]
