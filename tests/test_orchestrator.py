"""Tests for orchestration engine."""

import pytest

from src.orchestrator.engine import ExecutionContext, OrchestrationEngine
from src.orchestrator.pipeline import DEFAULT_PIPELINES


@pytest.mark.asyncio
class TestOrchestrationEngine:
    """Test Orchestration Engine."""

    def test_agent_registration(self, orchestrator):
        """Test agent registration."""
        agents = orchestrator.get_registered_agents()

        assert len(agents) > 0
        assert "requirement_analyst" in agents
        assert "test_designer" in agents

    def test_pipeline_registration(self, orchestrator):
        """Test pipeline registration."""
        for pipeline_name, pipeline in DEFAULT_PIPELINES.items():
            orchestrator.register_pipeline(pipeline_name, pipeline.agents)

        pipelines = orchestrator.get_registered_pipelines()
        assert "full_qa_pipeline" in pipelines

    def test_invalid_agent_registration(self, orchestrator):
        """Test invalid agent in pipeline."""
        with pytest.raises(ValueError):
            orchestrator.register_pipeline("test_pipeline", ["nonexistent_agent"])

    @pytest.mark.asyncio
    async def test_pipeline_execution(self, orchestrator):
        """Test pipeline execution."""
        # Register pipeline
        orchestrator.register_pipeline(
            "test_pipeline",
            ["requirement_analyst"],
        )

        # Execute
        context = await orchestrator.execute_pipeline(
            "test_pipeline",
            {
                "document": "Test requirement",
                "scope": "functional",
            },
        )

        assert context is not None
        assert context.execution_id is not None
        assert len(context.agent_outputs) > 0

    @pytest.mark.asyncio
    async def test_parallel_execution(self, orchestrator):
        """Test parallel agent execution."""
        context = await orchestrator.execute_parallel(
            ["test_runner"],
            {"test_suite": {"tests": []}},
        )

        assert context is not None
        assert len(context.agent_outputs) > 0


@pytest.mark.asyncio
class TestExecutionContext:
    """Test Execution Context."""

    def test_context_creation(self):
        """Test context creation."""
        context = ExecutionContext()

        assert context.execution_id is not None
        assert context.started_at is not None
        assert len(context.agent_outputs) == 0

    def test_context_status_recording(self):
        """Test status recording."""
        context = ExecutionContext()

        context.record_status("started", {"message": "Starting execution"})

        assert len(context.status_history) == 1
        assert context.status_history[0]["status"] == "started"

    def test_context_error_recording(self):
        """Test error recording."""
        context = ExecutionContext()

        context.record_error("test_agent", "Test error")

        assert context.has_errors
        assert len(context.errors) == 1
