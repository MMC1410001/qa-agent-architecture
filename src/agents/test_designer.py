"""Test Designer Agent - Creates comprehensive test cases from requirements."""

import json
from typing import Dict, List, Optional

from src.agents.base import BaseAgent
from src.llm.parsers import JSONParser
from src.models.agent_config import AgentInput, AgentOutput, AgentStatus
from src.models.test_case import TestPriority, TestType
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TestDesignerAgent(BaseAgent):
    """
    Agent that designs comprehensive test cases from requirements.

    Capabilities:
    - Generate test cases from requirements
    - Apply testing techniques (boundary value analysis, equivalence partitioning)
    - Create positive, negative, and edge case tests
    - Analyze test coverage
    - Identify testing gaps
    """

    def __init__(self, **kwargs):
        """Initialize Test Designer Agent."""
        super().__init__(name="test_designer", **kwargs)

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """
        Design comprehensive test cases from requirements.

        Expected input data:
        {
            "requirements": [
                {
                    "id": "REQ-001",
                    "title": "...",
                    "description": "...",
                    "acceptance_criteria": ["..."],
                    "test_scenarios": ["..."]
                }
            ],
            "test_type": "functional|integration|e2e|api|security|performance",
            "include_techniques": ["boundary_value", "equivalence_partitioning", ...]
        }

        Args:
            input_data: Input containing requirements and test type

        Returns:
            Agent output with designed test cases
        """
        try:
            requirements = input_data.data.get("requirements", [])
            test_type = input_data.data.get("test_type", "functional")

            if not requirements:
                raise ValueError("Requirements are required")

            logger.info(
                "Designing test cases",
                agent=self.name,
                requirement_count=len(requirements),
                test_type=test_type,
            )

            # Generate prompt
            req_summary = json.dumps(requirements, indent=2)[:4000]
            prompt = await self.generate_prompt(
                "test_designer",
                requirements=req_summary,
                test_type=test_type,
            )

            # Call LLM
            response = await self.call_llm(prompt)

            # Parse response
            parser = JSONParser()
            result = await parser.parse(response)

            # Structure test cases
            test_cases = self._structure_test_cases(
                result.get("test_cases", []), test_type
            )

            # Analyze coverage
            coverage = self._analyze_coverage(test_cases, requirements)

            logger.info(
                "Test case design complete",
                agent=self.name,
                test_case_count=len(test_cases),
                coverage=coverage.get("coverage_percentage"),
            )

            return AgentOutput(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                data={
                    "test_cases": test_cases,
                    "coverage_analysis": coverage,
                    "test_type": test_type,
                    "requirement_coverage": self._map_requirements_to_tests(
                        test_cases, requirements
                    ),
                },
                execution_time_seconds=0,
            )

        except Exception as e:
            logger.error(
                "Test case design failed",
                agent=self.name,
                error=str(e),
            )
            raise

    async def validate_input(self, input_data: AgentInput) -> None:
        """
        Validate test designer input.

        Args:
            input_data: Input to validate

        Raises:
            ValueError: If validation fails
        """
        await super().validate_input(input_data)

        if "requirements" not in input_data.data:
            raise ValueError("'requirements' field is required")

        requirements = input_data.data["requirements"]
        if not isinstance(requirements, list) or len(requirements) == 0:
            raise ValueError("Requirements must be non-empty list")

        # Validate each requirement
        for req in requirements:
            if not isinstance(req, dict):
                raise ValueError("Each requirement must be a dictionary")
            if "id" not in req or "description" not in req:
                raise ValueError(
                    "Each requirement must have 'id' and 'description'"
                )

        logger.debug("Test designer input validation passed")

    async def validate_output(self, output: AgentOutput) -> None:
        """
        Validate test designer output.

        Args:
            output: Output to validate

        Raises:
            ValueError: If validation fails
        """
        await super().validate_output(output)

        if output.status == AgentStatus.COMPLETED:
            test_cases = output.data.get("test_cases", [])
            if not isinstance(test_cases, list):
                raise ValueError("Test cases must be a list")

            # Validate each test case has required fields
            for tc in test_cases:
                required = ["id", "title", "description", "steps"]
                if not all(k in tc for k in required):
                    raise ValueError(
                        f"Test case missing required fields: {required}"
                    )

        logger.debug("Test designer output validation passed")

    def _structure_test_cases(
        self, raw_test_cases: List[Dict], test_type: str
    ) -> List[Dict]:
        """
        Structure and validate test cases.

        Args:
            raw_test_cases: Raw test case data from LLM
            test_type: Type of test

        Returns:
            Structured test cases
        """
        structured = []

        for i, tc in enumerate(raw_test_cases, 1):
            structured_tc = {
                "id": tc.get("id", f"TC-{i:04d}"),
                "title": tc.get("title", ""),
                "description": tc.get("description", ""),
                "test_type": test_type,
                "priority": tc.get("priority", "medium"),
                "preconditions": tc.get("preconditions", []),
                "steps": self._structure_steps(tc.get("steps", [])),
                "postconditions": tc.get("postconditions", []),
                "test_data": tc.get("test_data", {}),
                "requirement_ids": tc.get("requirement_ids", []),
                "expected_coverage": tc.get("expected_coverage", []),
            }

            # Ensure lists are actually lists
            for key in ["preconditions", "postconditions", "requirement_ids", "expected_coverage"]:
                if not isinstance(structured_tc[key], list):
                    structured_tc[key] = [structured_tc[key]]

            structured.append(structured_tc)

        return structured

    def _structure_steps(self, raw_steps: List) -> List[Dict]:
        """
        Structure test steps.

        Args:
            raw_steps: Raw step data

        Returns:
            Structured steps
        """
        structured_steps = []

        for i, step in enumerate(raw_steps, 1):
            if isinstance(step, dict):
                structured_steps.append({
                    "step_number": step.get("step_number", i),
                    "action": step.get("action", ""),
                    "expected_result": step.get("expected_result", ""),
                    "test_data": step.get("test_data"),
                })
            else:
                # Handle string steps
                structured_steps.append({
                    "step_number": i,
                    "action": str(step),
                    "expected_result": "",
                })

        return structured_steps

    def _analyze_coverage(
        self, test_cases: List[Dict], requirements: List[Dict]
    ) -> Dict:
        """
        Analyze test coverage.

        Args:
            test_cases: Designed test cases
            requirements: Requirements

        Returns:
            Coverage analysis
        """
        covered_reqs = set()

        for tc in test_cases:
            for req_id in tc.get("requirement_ids", []):
                covered_reqs.add(req_id)

        total_reqs = len(requirements)
        covered_count = len(covered_reqs)
        coverage_percentage = (covered_count / total_reqs * 100) if total_reqs > 0 else 0

        gaps = []
        for req in requirements:
            if req["id"] not in covered_reqs:
                gaps.append(f"REQ-{req['id']}: No test cases designed")

        return {
            "total_requirements": total_reqs,
            "covered_requirements": covered_count,
            "coverage_percentage": round(coverage_percentage, 2),
            "gaps": gaps,
            "test_case_count": len(test_cases),
        }

    def _map_requirements_to_tests(
        self, test_cases: List[Dict], requirements: List[Dict]
    ) -> Dict[str, List[str]]:
        """
        Map requirements to test cases.

        Args:
            test_cases: Test cases
            requirements: Requirements

        Returns:
            Mapping of requirement IDs to test case IDs
        """
        mapping = {}

        for req in requirements:
            req_id = req["id"]
            related_tests = [
                tc["id"] for tc in test_cases
                if req_id in tc.get("requirement_ids", [])
            ]
            mapping[req_id] = related_tests

        return mapping

    async def calculate_test_effort(
        self, test_cases: List[Dict]
    ) -> Dict:
        """
        Calculate testing effort.

        Args:
            test_cases: Test cases to analyze

        Returns:
            Effort estimation
        """
        total_steps = sum(len(tc.get("steps", [])) for tc in test_cases)
        avg_steps = total_steps / len(test_cases) if test_cases else 0

        # Estimate: ~5 minutes per step
        estimated_hours = (total_steps * 5) / 60

        return {
            "total_test_cases": len(test_cases),
            "total_steps": total_steps,
            "average_steps_per_test": round(avg_steps, 2),
            "estimated_execution_hours": round(estimated_hours, 2),
        }
