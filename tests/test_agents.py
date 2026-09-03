"""Tests for QA agents."""

import pytest

from src.agents.requirement_analyst import RequirementAnalystAgent
from src.agents.test_designer import TestDesignerAgent
from src.models.agent_config import AgentInput, AgentStatus


@pytest.mark.asyncio
class TestRequirementAnalyst:
    """Test Requirement Analyst Agent."""

    @pytest.mark.asyncio
    async def test_process_requirements(self, requirement_analyst, sample_requirement_input):
        """Test requirement analysis."""
        output = await requirement_analyst.process(sample_requirement_input)

        assert output.agent_name == "requirement_analyst"
        assert output.status == AgentStatus.COMPLETED
        assert "requirements" in output.data
        assert isinstance(output.data["requirements"], list)

    @pytest.mark.asyncio
    async def test_input_validation(self, requirement_analyst):
        """Test input validation."""
        invalid_input = AgentInput(data={})

        with pytest.raises(ValueError):
            await requirement_analyst.validate_input(invalid_input)

    @pytest.mark.asyncio
    async def test_agent_execution(self, requirement_analyst, sample_requirement_input):
        """Test full agent execution."""
        output = await requirement_analyst.execute(sample_requirement_input.data)

        assert output.agent_name == "requirement_analyst"
        assert output.execution_time_seconds > 0


@pytest.mark.asyncio
class TestTestDesigner:
    """Test Test Designer Agent."""

    @pytest.mark.asyncio
    async def test_design_test_cases(self, test_designer):
        """Test test case design."""
        input_data = AgentInput(
            data={
                "requirements": [
                    {
                        "id": "REQ-001",
                        "title": "User Login",
                        "description": "Users should be able to login",
                    }
                ],
                "test_type": "functional",
            }
        )

        output = await test_designer.process(input_data)

        assert output.agent_name == "test_designer"
        assert output.status == AgentStatus.COMPLETED
        assert "test_cases" in output.data

    @pytest.mark.asyncio
    async def test_input_validation(self, test_designer):
        """Test input validation."""
        invalid_input = AgentInput(data={"requirements": []})

        with pytest.raises(ValueError):
            await test_designer.validate_input(invalid_input)


@pytest.mark.asyncio
class TestAgentEvents:
    """Test agent event system."""

    @pytest.mark.asyncio
    async def test_event_handlers(self, requirement_analyst, sample_requirement_input):
        """Test event handling."""
        events = []

        def on_complete(data):
            events.append(("completed", data))

        requirement_analyst.on("completed", on_complete)

        output = await requirement_analyst.execute(sample_requirement_input.data)

        assert len(events) > 0
        assert events[0][0] == "completed"
