"""Regression Planner Agent - Plans optimized regression test suites."""

from src.agents.base import BaseAgent
from src.llm.parsers import JSONParser
from src.models.agent_config import AgentInput, AgentOutput, AgentStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RegressionPlannerAgent(BaseAgent):
    """
    Agent that plans optimized regression test suites.

    Capabilities:
    - Analyze code changes
    - Perform impact analysis
    - Risk-based test selection
    - Optimize test execution time
    - Recommend test prioritization
    """

    def __init__(self, **kwargs):
        """Initialize Regression Planner Agent."""
        super().__init__(name="regression_planner", **kwargs)

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """
        Plan regression test suite.

        Expected input data:
        {
            "changes": ["file1.py", "file2.py", ...],
            "test_inventory": [...],
            "optimization_strategy": "risk-based|coverage|time"
        }

        Args:
            input_data: Code changes and test inventory

        Returns:
            Agent output with regression plan
        """
        try:
            changes = input_data.data.get("changes", [])
            test_inventory = input_data.data.get("test_inventory", [])

            if not changes or not test_inventory:
                raise ValueError("Changes and test inventory are required")

            logger.info(
                "Planning regression test suite",
                agent=self.name,
                changes=len(changes),
                available_tests=len(test_inventory),
            )

            # Generate prompt
            import json
            changes_str = json.dumps(changes[:10], indent=2)  # Limit
            inventory_str = json.dumps(test_inventory[:10], indent=2)

            prompt = await self.generate_prompt(
                "regression_planner",
                changes=changes_str,
                test_inventory=inventory_str,
                period="7",
            )

            # Call LLM
            response = await self.call_llm(prompt)

            # Parse response
            parser = JSONParser()
            result = await parser.parse(response)

            plan = result.get("regression_plan", {})

            logger.info(
                "Regression plan created",
                agent=self.name,
                selected_tests=plan.get("selected", 0),
                reduction=plan.get("reduction_percentage", 0),
            )

            return AgentOutput(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                data={
                    "regression_plan": plan,
                    "change_analysis": self._analyze_changes(changes),
                    "estimated_time_hours": plan.get("estimated_time_hours", 0),
                },
                execution_time_seconds=0,
            )

        except Exception as e:
            logger.error(
                "Regression planning failed",
                agent=self.name,
                error=str(e),
            )
            raise

    async def validate_input(self, input_data: AgentInput) -> None:
        """Validate regression planner input."""
        await super().validate_input(input_data)

        required = ["changes", "test_inventory"]
        for field in required:
            if field not in input_data.data:
                raise ValueError(f"'{field}' is required")

        logger.debug("Regression planner input validation passed")

    def _analyze_changes(self, changes: list) -> dict:
        """
        Analyze code changes.

        Args:
            changes: List of changed files

        Returns:
            Change analysis
        """
        analysis = {
            "total_files": len(changes),
            "impact_areas": [],
            "risk_level": "medium",
        }

        # Categorize changes
        for change in changes:
            if "auth" in change.lower():
                analysis["impact_areas"].append("Authentication")
                analysis["risk_level"] = "high"
            elif "payment" in change.lower():
                analysis["impact_areas"].append("Payment")
                analysis["risk_level"] = "critical"
            elif "api" in change.lower():
                analysis["impact_areas"].append("API")

        return analysis
