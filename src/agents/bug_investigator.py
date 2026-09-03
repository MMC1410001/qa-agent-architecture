"""Bug Investigator Agent - Analyzes test failures and generates bug reports."""

from src.agents.base import BaseAgent
from src.llm.parsers import JSONParser
from src.models.agent_config import AgentInput, AgentOutput, AgentStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BugInvestigatorAgent(BaseAgent):
    """
    Agent that investigates test failures and generates bug reports.

    Capabilities:
    - Analyze test failures
    - Perform root cause analysis
    - Generate detailed bug reports
    - Assess severity and impact
    - Suggest fixes
    """

    def __init__(self, **kwargs):
        """Initialize Bug Investigator Agent."""
        super().__init__(name="bug_investigator", **kwargs)

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """
        Investigate test failure and generate bug report.

        Expected input data:
        {
            "test_case_id": "TC-XXX",
            "execution_id": "EXEC-XXX",
            "error_message": "...",
            "logs": "...",
            "artifacts": ["..."]
        }

        Args:
            input_data: Failure information

        Returns:
            Agent output with bug report
        """
        try:
            test_case_id = input_data.data.get("test_case_id", "")
            error_message = input_data.data.get("error_message", "")

            if not test_case_id or not error_message:
                raise ValueError("Test case ID and error message are required")

            logger.info(
                "Investigating test failure",
                agent=self.name,
                test_case=test_case_id,
            )

            # Generate prompt
            prompt = await self.generate_prompt(
                "bug_investigator",
                test_case_id=test_case_id,
                execution_id=input_data.data.get("execution_id", ""),
                error_message=error_message,
                logs=input_data.data.get("logs", "")[:2000],
                artifacts=str(input_data.data.get("artifacts", [])),
            )

            # Call LLM
            response = await self.call_llm(prompt)

            # Parse response
            parser = JSONParser()
            result = await parser.parse(response)

            logger.info(
                "Bug investigation complete",
                agent=self.name,
                severity=result.get("bug_report", {}).get("severity"),
            )

            return AgentOutput(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                data={
                    "bug_report": result.get("bug_report", {}),
                    "root_cause_confirmed": False,
                    "test_case_id": test_case_id,
                },
                execution_time_seconds=0,
            )

        except Exception as e:
            logger.error(
                "Bug investigation failed",
                agent=self.name,
                error=str(e),
            )
            raise

    async def validate_input(self, input_data: AgentInput) -> None:
        """Validate bug investigator input."""
        await super().validate_input(input_data)

        required = ["test_case_id", "error_message"]
        for field in required:
            if field not in input_data.data:
                raise ValueError(f"'{field}' is required")

        logger.debug("Bug investigator input validation passed")
