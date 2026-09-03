"""Orchestration engine for managing agent workflows."""

import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.agents.base import BaseAgent
from src.models.agent_config import AgentOutput, AgentStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExecutionContext:
    """Context for a workflow execution."""

    def __init__(self, execution_id: str = None):
        """
        Initialize execution context.

        Args:
            execution_id: Unique execution ID
        """
        self.execution_id = execution_id or f"EXEC-{uuid.uuid4().hex[:12].upper()}"
        self.started_at = datetime.utcnow()
        self.agent_outputs: Dict[str, AgentOutput] = {}
        self.status_history: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []

    def add_agent_output(self, agent_name: str, output: AgentOutput) -> None:
        """
        Record agent output.

        Args:
            agent_name: Name of agent
            output: Agent output
        """
        self.agent_outputs[agent_name] = output

    def get_agent_output(self, agent_name: str) -> Optional[AgentOutput]:
        """
        Get agent output.

        Args:
            agent_name: Name of agent

        Returns:
            Agent output or None if not found
        """
        return self.agent_outputs.get(agent_name)

    def record_status(self, status: str, details: Dict = None) -> None:
        """
        Record status update.

        Args:
            status: Status message
            details: Optional status details
        """
        self.status_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
            "details": details or {},
        })

    def record_error(self, agent_name: str, error: str) -> None:
        """
        Record error.

        Args:
            agent_name: Name of agent
            error: Error message
        """
        self.errors.append({
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent_name,
            "error": error,
        })

    @property
    def duration_seconds(self) -> float:
        """Get execution duration."""
        return (datetime.utcnow() - self.started_at).total_seconds()

    @property
    def has_errors(self) -> bool:
        """Check if execution has errors."""
        return len(self.errors) > 0


class OrchestrationEngine:
    """
    Event-driven orchestration engine for QA agents.

    Manages:
    - Agent workflow execution
    - Dependency resolution
    - Parallel/sequential execution
    - Status tracking
    - Event emission
    """

    def __init__(self):
        """Initialize orchestration engine."""
        self.agents: Dict[str, BaseAgent] = {}
        self.pipelines: Dict[str, List[str]] = {}
        self._event_handlers: Dict[str, List] = {}

        logger.info("Orchestration engine initialized")

    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent.

        Args:
            agent: Agent to register
        """
        self.agents[agent.name] = agent

        # Subscribe to agent events
        agent.on("completed", self._handle_agent_completed)
        agent.on("failed", self._handle_agent_failed)

        logger.info("Agent registered", agent=agent.name)

    def register_pipeline(self, name: str, agents: List[str]) -> None:
        """
        Register a pipeline.

        Args:
            name: Pipeline name
            agents: List of agent names in sequence
        """
        # Validate agents exist
        for agent_name in agents:
            if agent_name not in self.agents:
                raise ValueError(f"Agent not found: {agent_name}")

        self.pipelines[name] = agents
        logger.info("Pipeline registered", pipeline=name, agents=len(agents))

    async def execute_pipeline(
        self,
        pipeline_name: str,
        initial_data: Dict[str, Any],
        context: Optional[ExecutionContext] = None,
    ) -> ExecutionContext:
        """
        Execute a pipeline.

        Args:
            pipeline_name: Name of pipeline to execute
            initial_data: Initial data to pass to first agent
            context: Optional existing context

        Returns:
            Execution context with results

        Raises:
            ValueError: If pipeline not found
        """
        if pipeline_name not in self.pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_name}")

        context = context or ExecutionContext()
        agent_sequence = self.pipelines[pipeline_name]

        logger.info(
            "Pipeline execution started",
            pipeline=pipeline_name,
            execution_id=context.execution_id,
        )

        current_data = initial_data

        for i, agent_name in enumerate(agent_sequence):
            context.record_status(f"Executing agent {i+1}/{len(agent_sequence)}: {agent_name}")

            try:
                agent = self.agents[agent_name]

                logger.debug(
                    "Executing agent in pipeline",
                    agent=agent_name,
                    step=i + 1,
                    total=len(agent_sequence),
                )

                # Execute agent
                output = await agent.execute(current_data)

                # Record output
                context.add_agent_output(agent_name, output)

                # Check if successful
                if output.status == AgentStatus.FAILED:
                    context.record_error(agent_name, output.error or "Unknown error")
                    logger.warning(
                        "Agent failed in pipeline",
                        agent=agent_name,
                        error=output.error,
                    )
                    # Optionally continue or stop based on configuration
                    # For now, stop on first failure
                    break

                # Prepare data for next agent
                current_data = output.data

            except Exception as e:
                logger.error(
                    "Agent execution failed",
                    agent=agent_name,
                    error=str(e),
                )
                context.record_error(agent_name, str(e))
                break

        logger.info(
            "Pipeline execution completed",
            pipeline=pipeline_name,
            execution_id=context.execution_id,
            duration=context.duration_seconds,
            errors=len(context.errors),
        )

        await self._emit_event("pipeline_completed", {
            "execution_id": context.execution_id,
            "pipeline": pipeline_name,
            "duration": context.duration_seconds,
            "has_errors": context.has_errors,
        })

        return context

    async def execute_parallel(
        self,
        agent_names: List[str],
        input_data: Dict[str, Any],
        context: Optional[ExecutionContext] = None,
    ) -> ExecutionContext:
        """
        Execute multiple agents in parallel.

        Args:
            agent_names: List of agent names to execute
            input_data: Input data for agents
            context: Optional existing context

        Returns:
            Execution context with results
        """
        context = context or ExecutionContext()

        logger.info(
            "Parallel execution started",
            agents=len(agent_names),
            execution_id=context.execution_id,
        )

        # Create tasks for all agents
        tasks = []
        for agent_name in agent_names:
            if agent_name not in self.agents:
                raise ValueError(f"Agent not found: {agent_name}")

            agent = self.agents[agent_name]
            task = asyncio.create_task(agent.execute(input_data))
            tasks.append((agent_name, task))

        # Wait for all to complete
        for agent_name, task in tasks:
            try:
                output = await task
                context.add_agent_output(agent_name, output)

                if output.status == AgentStatus.FAILED:
                    context.record_error(agent_name, output.error)

            except Exception as e:
                logger.error(
                    "Parallel agent execution failed",
                    agent=agent_name,
                    error=str(e),
                )
                context.record_error(agent_name, str(e))

        logger.info(
            "Parallel execution completed",
            agents=len(agent_names),
            duration=context.duration_seconds,
        )

        return context

    def on(self, event_type: str, handler) -> None:
        """
        Register event handler.

        Args:
            event_type: Type of event
            handler: Handler callable
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    async def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit event to handlers."""
        handlers = self._event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                logger.error(
                    "Event handler failed",
                    event_type=event_type,
                    error=str(e),
                )

    async def _handle_agent_completed(self, data: Dict[str, Any]) -> None:
        """Handle agent completion."""
        logger.debug("Agent completed", data=data)

    async def _handle_agent_failed(self, data: Dict[str, Any]) -> None:
        """Handle agent failure."""
        logger.warning("Agent failed", data=data)

    def get_registered_agents(self) -> List[str]:
        """Get list of registered agents."""
        return list(self.agents.keys())

    def get_registered_pipelines(self) -> Dict[str, List[str]]:
        """Get registered pipelines."""
        return self.pipelines.copy()
