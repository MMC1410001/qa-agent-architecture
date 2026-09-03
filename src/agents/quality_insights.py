"""Quality Insights Agent - Generates quality metrics and insights."""

from src.agents.base import BaseAgent
from src.llm.parsers import JSONParser
from src.models.agent_config import AgentInput, AgentOutput, AgentStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)


class QualityInsightsAgent(BaseAgent):
    """
    Agent that generates quality metrics and insights.

    Capabilities:
    - Analyze test execution history
    - Calculate quality metrics
    - Identify trends
    - Generate recommendations
    - Create quality reports
    """

    def __init__(self, **kwargs):
        """Initialize Quality Insights Agent."""
        super().__init__(name="quality_insights", **kwargs)

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """
        Generate quality insights and metrics.

        Expected input data:
        {
            "execution_history": [...],
            "metrics": {...},
            "period_days": 7
        }

        Args:
            input_data: Execution history and metrics

        Returns:
            Agent output with quality insights
        """
        try:
            execution_history = input_data.data.get("execution_history", [])
            metrics = input_data.data.get("metrics", {})
            period_days = input_data.data.get("period_days", 7)

            if not execution_history or not metrics:
                raise ValueError("Execution history and metrics are required")

            logger.info(
                "Generating quality insights",
                agent=self.name,
                executions=len(execution_history),
                period=period_days,
            )

            # Generate prompt
            import json
            history_str = json.dumps(execution_history[:5], indent=2)  # Limit
            metrics_str = json.dumps(metrics, indent=2)

            prompt = await self.generate_prompt(
                "quality_insights",
                history=history_str,
                metrics=metrics_str,
                period=str(period_days),
            )

            # Call LLM
            response = await self.call_llm(prompt)

            # Parse response
            parser = JSONParser()
            result = await parser.parse(response)

            logger.info(
                "Quality insights generated",
                agent=self.name,
                health_score=result.get("dashboard", {}).get("overall_health"),
            )

            return AgentOutput(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                data={
                    "dashboard": result.get("dashboard", {}),
                    "trends": result.get("trends", []),
                    "recommendations": result.get("recommendations", []),
                    "quality_gates": result.get("quality_gates", {}),
                    "summary": result.get("summary", ""),
                },
                execution_time_seconds=0,
            )

        except Exception as e:
            logger.error(
                "Quality insights generation failed",
                agent=self.name,
                error=str(e),
            )
            raise

    async def validate_input(self, input_data: AgentInput) -> None:
        """Validate quality insights input."""
        await super().validate_input(input_data)

        required = ["execution_history", "metrics"]
        for field in required:
            if field not in input_data.data:
                raise ValueError(f"'{field}' is required")

        logger.debug("Quality insights input validation passed")

    def _calculate_health_score(self, metrics: dict) -> float:
        """
        Calculate overall quality health score.

        Args:
            metrics: Quality metrics

        Returns:
            Health score (0-100)
        """
        weights = {
            "test_pass_rate": 0.35,
            "code_coverage": 0.25,
            "automation_ratio": 0.20,
            "defect_density": -0.20,  # Negative weight - lower is better
        }

        score = 0
        for key, weight in weights.items():
            value = metrics.get(key, 50)
            if weight < 0:
                # For defect density, invert the score
                value = max(0, 100 - value)
            score += (value * weight)

        return max(0, min(100, score))
