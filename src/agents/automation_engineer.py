"""Automation Engineer Agent - Generates automation scripts from test cases."""

from src.agents.base import BaseAgent
from src.llm.parsers import JSONParser
from src.models.agent_config import AgentInput, AgentOutput, AgentStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AutomationEngineerAgent(BaseAgent):
    """
    Agent that converts test cases into automation code.

    Capabilities:
    - Generate automation scripts from test cases
    - Create page object models
    - Generate test fixtures and utilities
    - Support multiple frameworks (Playwright, Selenium, API)
    - Apply best practices (DRY, POM, clear naming)
    """

    def __init__(self, **kwargs):
        """Initialize Automation Engineer Agent."""
        super().__init__(name="automation_engineer", **kwargs)

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """
        Generate automation code from test cases.

        Expected input data:
        {
            "test_cases": [...],
            "framework": "playwright|selenium|api",
            "language": "python|javascript|java",
            "page_objects": true
        }

        Args:
            input_data: Test cases and framework info

        Returns:
            Agent output with automation code
        """
        try:
            test_cases = input_data.data.get("test_cases", [])
            framework = input_data.data.get("framework", "playwright")

            if not test_cases:
                raise ValueError("Test cases are required")

            logger.info(
                "Generating automation code",
                agent=self.name,
                test_count=len(test_cases),
                framework=framework,
            )

            # Generate prompt
            import json
            tc_summary = json.dumps(test_cases[:3], indent=2)  # Limit to first 3
            prompt = await self.generate_prompt(
                "automation_engineer",
                test_cases=tc_summary,
                framework=framework,
            )

            # Call LLM
            response = await self.call_llm(prompt)

            logger.info(
                "Automation code generation complete",
                agent=self.name,
                code_length=len(response),
            )

            return AgentOutput(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                data={
                    "automation_code": response,
                    "framework": framework,
                    "test_cases_count": len(test_cases),
                    "includes_page_objects": "page_objects" in response.lower(),
                    "includes_fixtures": "fixture" in response.lower(),
                },
                execution_time_seconds=0,
            )

        except Exception as e:
            logger.error(
                "Automation code generation failed",
                agent=self.name,
                error=str(e),
            )
            raise

    async def validate_input(self, input_data: AgentInput) -> None:
        """Validate automation engineer input."""
        await super().validate_input(input_data)

        if "test_cases" not in input_data.data:
            raise ValueError("'test_cases' field is required")

        framework = input_data.data.get("framework", "")
        supported = ["playwright", "selenium", "api", "rest", "graphql"]
        if framework and framework not in supported:
            raise ValueError(f"Framework must be one of {supported}")

        logger.debug("Automation engineer input validation passed")
