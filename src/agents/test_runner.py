"""Test Runner Agent - Executes tests and manages results."""

from datetime import datetime
from typing import List

from src.agents.base import BaseAgent
from src.models.agent_config import AgentInput, AgentOutput, AgentStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TestRunnerAgent(BaseAgent):
    """
    Agent that executes tests and manages test execution.

    Capabilities:
    - Execute test suites
    - Manage parallel execution
    - Collect execution results
    - Generate reports
    - Handle test environments
    """

    def __init__(self, **kwargs):
        """Initialize Test Runner Agent."""
        super().__init__(name="test_runner", **kwargs)

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """
        Execute test suite.

        Expected input data:
        {
            "test_suite": {...},
            "environment": "dev|staging|prod",
            "parallel": true,
            "max_workers": 5
        }

        Args:
            input_data: Test suite and execution config

        Returns:
            Agent output with execution results
        """
        try:
            test_suite = input_data.data.get("test_suite")
            environment = input_data.data.get("environment", "dev")

            if not test_suite:
                raise ValueError("Test suite is required")

            logger.info(
                "Starting test execution",
                agent=self.name,
                environment=environment,
            )

            # Simulate test execution (in real implementation, would run actual tests)
            results = {
                "total_tests": 10,
                "passed": 9,
                "failed": 1,
                "skipped": 0,
                "start_time": datetime.utcnow().isoformat(),
                "end_time": datetime.utcnow().isoformat(),
                "duration_seconds": 125.5,
                "environment": environment,
                "details": [
                    {
                        "test_id": "TC-001",
                        "status": "passed",
                        "duration": 5.2,
                    },
                    {
                        "test_id": "TC-002",
                        "status": "failed",
                        "duration": 3.8,
                        "error": "Element not found",
                    },
                ],
            }

            logger.info(
                "Test execution complete",
                agent=self.name,
                passed=results["passed"],
                failed=results["failed"],
            )

            return AgentOutput(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                data=results,
                execution_time_seconds=0,
            )

        except Exception as e:
            logger.error(
                "Test execution failed",
                agent=self.name,
                error=str(e),
            )
            raise

    async def validate_input(self, input_data: AgentInput) -> None:
        """Validate test runner input."""
        await super().validate_input(input_data)

        if "test_suite" not in input_data.data:
            raise ValueError("'test_suite' field is required")

        environment = input_data.data.get("environment", "")
        valid_envs = ["dev", "staging", "prod", ""]
        if environment and environment not in valid_envs:
            raise ValueError(f"Invalid environment: {environment}")

        logger.debug("Test runner input validation passed")
