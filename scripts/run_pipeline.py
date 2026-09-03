"""Script to run QA-OS pipelines."""

import asyncio
import sys
from typing import Optional

from src.agents.automation_engineer import AutomationEngineerAgent
from src.agents.bug_investigator import BugInvestigatorAgent
from src.agents.quality_insights import QualityInsightsAgent
from src.agents.regression_planner import RegressionPlannerAgent
from src.agents.requirement_analyst import RequirementAnalystAgent
from src.agents.test_designer import TestDesignerAgent
from src.agents.test_runner import TestRunnerAgent
from src.orchestrator.engine import OrchestrationEngine
from src.orchestrator.pipeline import DEFAULT_PIPELINES
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def main():
    """Run a QA pipeline."""
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <pipeline_name> [data_file]")
        print("\nAvailable pipelines:")
        for name in DEFAULT_PIPELINES:
            pipeline = DEFAULT_PIPELINES[name]
            print(f"  - {name}: {pipeline.description}")
        sys.exit(1)

    pipeline_name = sys.argv[1]

    # Validate pipeline
    if pipeline_name not in DEFAULT_PIPELINES:
        print(f"Error: Unknown pipeline '{pipeline_name}'")
        sys.exit(1)

    # Initialize orchestrator
    logger.info("Initializing orchestration engine")
    orchestrator = OrchestrationEngine()

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
        orchestrator.register_agent(agent)

    # Register pipelines
    for name, pipeline in DEFAULT_PIPELINES.items():
        orchestrator.register_pipeline(name, pipeline.agents)

    # Prepare input data
    input_data = prepare_input_data(pipeline_name)

    # Register event handlers
    def on_pipeline_completed(data):
        logger.info("Pipeline completed", data=data)

    orchestrator.on("pipeline_completed", on_pipeline_completed)

    # Execute pipeline
    logger.info(f"Executing pipeline: {pipeline_name}")
    context = await orchestrator.execute_pipeline(
        pipeline_name,
        input_data,
    )

    # Print results
    print("\n" + "=" * 60)
    print(f"Pipeline Execution: {pipeline_name}")
    print("=" * 60)
    print(f"Execution ID: {context.execution_id}")
    print(f"Duration: {context.duration_seconds:.2f} seconds")
    print(f"Agents executed: {len(context.agent_outputs)}")
    print(f"Errors: {len(context.errors)}")

    print("\nAgent Outputs:")
    for agent_name, output in context.agent_outputs.items():
        print(f"\n  {agent_name}:")
        print(f"    Status: {output.status}")
        print(f"    Time: {output.execution_time_seconds:.2f}s")

    if context.errors:
        print("\nErrors:")
        for error in context.errors:
            print(f"  - {error['agent']}: {error['error']}")

    print("=" * 60 + "\n")


def prepare_input_data(pipeline_name: str) -> dict:
    """
    Prepare initial input data based on pipeline.

    Args:
        pipeline_name: Name of pipeline

    Returns:
        Input data dictionary
    """
    if pipeline_name == "full_qa_pipeline":
        return {
            "document": """
            Feature: User Authentication

            Users should be able to:
            1. Register with email and password
            2. Login with valid credentials
            3. Logout successfully
            4. Reset password
            5. Update profile information

            Acceptance Criteria:
            - Registration requires valid email
            - Password must be at least 8 characters
            - Login fails with invalid credentials
            - Session expires after 30 minutes
            """,
            "scope": "functional",
        }

    elif pipeline_name == "smoke_test_pipeline":
        return {
            "test_suite": {
                "name": "Smoke Tests",
                "tests": ["TC-001", "TC-002", "TC-003"],
            },
            "environment": "dev",
        }

    elif pipeline_name == "regression_pipeline":
        return {
            "changes": [
                "src/auth/login.py",
                "src/auth/session.py",
                "tests/test_auth.py",
            ],
            "test_inventory": [
                {"id": "TC-001", "name": "Login test"},
                {"id": "TC-002", "name": "Logout test"},
                {"id": "TC-003", "name": "Session test"},
            ],
        }

    elif pipeline_name == "quality_report_pipeline":
        return {
            "execution_history": [
                {"pass_rate": 95.0, "coverage": 85.0},
                {"pass_rate": 92.0, "coverage": 83.0},
                {"pass_rate": 90.0, "coverage": 80.0},
            ],
            "metrics": {
                "test_pass_rate": 95.0,
                "code_coverage": 85.0,
                "automation_ratio": 90.0,
                "defect_density": 2.5,
            },
        }

    elif pipeline_name == "bug_analysis_pipeline":
        return {
            "test_case_id": "TC-001",
            "execution_id": "EXEC-001",
            "error_message": "Element not found: #login-button",
            "logs": "Browser logs: element locator failed",
        }

    return {}


if __name__ == "__main__":
    asyncio.run(main())
