"""Requirement Analyst Agent - Extracts testable requirements from documents."""

import json
from typing import Dict, List, Optional

from src.agents.base import BaseAgent
from src.llm.parsers import JSONParser
from src.models.agent_config import AgentInput, AgentOutput, AgentStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Requirement(dict):
    """Requirement data structure."""

    def __init__(self, req_id: str, title: str, description: str, **kwargs):
        """
        Initialize requirement.

        Args:
            req_id: Requirement ID
            title: Requirement title
            description: Requirement description
            **kwargs: Additional fields
        """
        super().__init__({
            "id": req_id,
            "title": title,
            "description": description,
            **kwargs
        })


class RequirementAnalystAgent(BaseAgent):
    """
    Agent that analyzes requirements documents and extracts testable requirements.

    Capabilities:
    - Parse product requirements documents
    - Extract user stories and acceptance criteria
    - Identify testable scenarios
    - Create requirement-to-test mappings
    - Identify testing gaps
    """

    def __init__(self, **kwargs):
        """Initialize Requirement Analyst Agent."""
        super().__init__(name="requirement_analyst", **kwargs)

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """
        Analyze requirements document and extract testable requirements.

        Expected input data:
        {
            "document": "Product requirements or specification text",
            "scope": "Testing scope (functional, security, performance, etc.)"
        }

        Args:
            input_data: Input containing document and scope

        Returns:
            Agent output with extracted requirements

        """
        try:
            document = input_data.data.get("document", "")
            scope = input_data.data.get("scope", "functional")

            if not document:
                raise ValueError("Document content is required")

            logger.info(
                "Analyzing requirements",
                agent=self.name,
                doc_length=len(document),
                scope=scope,
            )

            # Generate prompt
            prompt = await self.generate_prompt(
                "requirement_analyst",
                document=document[:5000],  # Limit document size
                scope=scope,
            )

            # Call LLM
            response = await self.call_llm(prompt)

            # Parse response
            parser = JSONParser()
            result = await parser.parse(response)

            # Validate and structure result
            requirements = self._structure_requirements(
                result.get("requirements", [])
            )

            # Generate test mapping
            test_mapping = self._generate_test_mapping(requirements)

            # Identify gaps
            gaps = result.get("gaps", [])

            logger.info(
                "Requirements analysis complete",
                agent=self.name,
                requirement_count=len(requirements),
                gaps=len(gaps),
            )

            return AgentOutput(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                data={
                    "requirements": requirements,
                    "test_mapping": test_mapping,
                    "gaps": gaps,
                    "summary": result.get("summary", ""),
                    "scope": scope,
                },
                execution_time_seconds=0,  # Will be set by executor
            )

        except Exception as e:
            logger.error(
                "Requirement analysis failed",
                agent=self.name,
                error=str(e),
            )
            raise

    async def validate_input(self, input_data: AgentInput) -> None:
        """
        Validate requirement analyst input.

        Args:
            input_data: Input to validate

        Raises:
            ValueError: If validation fails
        """
        await super().validate_input(input_data)

        if "document" not in input_data.data:
            raise ValueError("'document' field is required in input")

        document = input_data.data["document"]
        if not isinstance(document, str) or len(document.strip()) == 0:
            raise ValueError("Document must be non-empty string")

        logger.debug("Requirement analyst input validation passed")

    async def validate_output(self, output: AgentOutput) -> None:
        """
        Validate requirement analyst output.

        Args:
            output: Output to validate

        Raises:
            ValueError: If validation fails
        """
        await super().validate_output(output)

        if output.status == AgentStatus.COMPLETED:
            requirements = output.data.get("requirements", [])
            if not isinstance(requirements, list):
                raise ValueError("Requirements must be a list")

            # Validate each requirement has required fields
            for req in requirements:
                if not all(k in req for k in ["id", "title", "description"]):
                    raise ValueError(
                        f"Requirement missing required fields: {req}"
                    )

        logger.debug("Requirement analyst output validation passed")

    def _structure_requirements(self, raw_requirements: List[Dict]) -> List[Dict]:
        """
        Structure and validate requirements.

        Args:
            raw_requirements: Raw requirement data from LLM

        Returns:
            Structured requirements
        """
        structured = []

        for i, req in enumerate(raw_requirements, 1):
            structured_req = {
                "id": req.get("id", f"REQ-{i:04d}"),
                "title": req.get("title", ""),
                "description": req.get("description", ""),
                "acceptance_criteria": req.get("acceptance_criteria", []),
                "test_scenarios": req.get("test_scenarios", []),
                "risk_level": req.get("risk_level", "medium"),
                "priority": req.get("priority", "medium"),
                "related_requirements": req.get("related_requirements", []),
            }

            # Ensure lists are actually lists
            for key in ["acceptance_criteria", "test_scenarios", "related_requirements"]:
                if not isinstance(structured_req[key], list):
                    structured_req[key] = [structured_req[key]]

            structured.append(structured_req)

        return structured

    def _generate_test_mapping(
        self, requirements: List[Dict]
    ) -> Dict[str, List[str]]:
        """
        Generate requirement to test scenario mapping.

        Args:
            requirements: Structured requirements

        Returns:
            Mapping of requirement IDs to test scenarios
        """
        mapping = {}

        for req in requirements:
            req_id = req["id"]
            scenarios = req.get("test_scenarios", [])
            mapping[req_id] = scenarios

        return mapping

    async def analyze_risk(self, requirements: List[Dict]) -> Dict:
        """
        Analyze risk for requirements.

        Args:
            requirements: Requirements to analyze

        Returns:
            Risk analysis results
        """
        logger.info("Analyzing requirement risks")

        risk_summary = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        for req in requirements:
            risk_level = req.get("risk_level", "medium").lower()
            if risk_level in risk_summary:
                risk_summary[risk_level] += 1

        risk_summary["total"] = len(requirements)

        return risk_summary

    async def identify_gaps(
        self, requirements: List[Dict]
    ) -> List[str]:
        """
        Identify testing gaps.

        Args:
            requirements: Requirements to analyze

        Returns:
            List of identified gaps
        """
        gaps = []

        for req in requirements:
            scenarios = req.get("test_scenarios", [])
            if not scenarios or len(scenarios) < 2:
                gaps.append(
                    f"REQ-{req['id']}: Insufficient test scenarios "
                    f"({len(scenarios)} defined, recommend 3+)"
                )

        return gaps
