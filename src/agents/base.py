"""Base agent class for QA-OS."""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config import settings
from src.llm.provider import LLMProvider, get_llm_provider
from src.models.agent_config import AgentConfig, AgentInput, AgentOutput, AgentStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all QA agents.

    Provides common functionality for:
    - LLM integration
    - Input/output validation
    - Retry logic and error handling
    - Event emission
    - Logging and monitoring
    """

    def __init__(
        self,
        name: str,
        config: Optional[AgentConfig] = None,
        llm_provider: Optional[LLMProvider] = None,
    ):
        """
        Initialize base agent.

        Args:
            name: Agent name
            config: Optional agent configuration
            llm_provider: Optional LLM provider (defaults to configured provider)
        """
        self.name = name
        self.config = config or AgentConfig(name=name, description=f"{name} agent")
        self.llm = llm_provider or get_llm_provider()

        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = {
            "started": [],
            "completed": [],
            "failed": [],
            "event": [],
        }

        logger.info("Agent initialized", agent=self.name)

    @abstractmethod
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """
        Process input and generate output.

        Args:
            input_data: Input data for agent

        Returns:
            Agent output with results

        Must be implemented by subclasses.
        """
        pass

    async def execute(self, input_data: Dict[str, Any]) -> AgentOutput:
        """
        Execute agent with input data.

        This is the main entry point that handles:
        - Input validation
        - Execution with retry logic
        - Output validation
        - Event emission
        - Error handling

        Args:
            input_data: Input dictionary

        Returns:
            Agent output

        """
        start_time = time.time()
        agent_input = AgentInput(data=input_data)

        logger.info(
            "Agent execution started",
            agent=self.name,
            input_keys=list(input_data.keys()),
        )

        # Emit started event
        await self._emit_event("started", {"agent": self.name})

        try:
            # Validate input
            await self.validate_input(agent_input)

            # Process with retry logic
            output = await self._execute_with_retry(agent_input)

            # Validate output
            await self.validate_output(output)

            # Calculate execution time
            execution_time = time.time() - start_time

            logger.info(
                "Agent execution completed",
                agent=self.name,
                status=output.status,
                time_seconds=execution_time,
            )

            # Emit completed event
            await self._emit_event(
                "completed",
                {
                    "agent": self.name,
                    "status": output.status,
                    "time": execution_time,
                },
            )

            return output

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                "Agent execution failed",
                agent=self.name,
                error=str(e),
                time_seconds=execution_time,
            )

            # Emit failed event
            await self._emit_event(
                "failed",
                {
                    "agent": self.name,
                    "error": str(e),
                    "time": execution_time,
                },
            )

            # Return error output
            return AgentOutput(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                data={},
                error=str(e),
                error_type=type(e).__name__,
                execution_time_seconds=execution_time,
            )

    async def _execute_with_retry(self, input_data: AgentInput) -> AgentOutput:
        """
        Execute agent with retry logic.

        Args:
            input_data: Input data

        Returns:
            Agent output

        """
        max_retries = self.config.retry_attempts
        retry_delay = self.config.retry_delay

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential(multiplier=1, min=retry_delay, max=retry_delay * 4),
            retry=retry_if_exception_type(Exception),
            reraise=True,
        ):
            with attempt:
                logger.debug(
                    "Executing agent",
                    agent=self.name,
                    attempt=attempt.retry_state.attempt_number,
                )
                return await self.process(input_data)

    async def validate_input(self, input_data: AgentInput) -> None:
        """
        Validate input data.

        Override in subclasses for custom validation.

        Args:
            input_data: Input to validate

        Raises:
            ValueError: If validation fails
        """
        if not input_data.data:
            raise ValueError("Input data cannot be empty")

        logger.debug("Input validation passed", agent=self.name)

    async def validate_output(self, output: AgentOutput) -> None:
        """
        Validate output data.

        Override in subclasses for custom validation.

        Args:
            output: Output to validate

        Raises:
            ValueError: If validation fails
        """
        if output.status == AgentStatus.FAILED and not output.error:
            raise ValueError("Failed output must have error message")

        logger.debug("Output validation passed", agent=self.name)

    async def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Emit an event for orchestrator tracking.

        Args:
            event_type: Type of event
            data: Event data
        """
        await self._emit_event(event_type, data)

    async def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Emit event to registered handlers.

        Args:
            event_type: Type of event
            data: Event data
        """
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

    def on(self, event_type: str, handler: Callable) -> None:
        """
        Register event handler.

        Args:
            event_type: Type of event to listen for
            handler: Callable to handle event
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
        logger.debug(
            "Event handler registered",
            agent=self.name,
            event_type=event_type,
        )

    def off(self, event_type: str, handler: Callable) -> None:
        """
        Unregister event handler.

        Args:
            event_type: Type of event
            handler: Handler to remove
        """
        if event_type in self._event_handlers:
            self._event_handlers[event_type].remove(handler)
            logger.debug(
                "Event handler unregistered",
                agent=self.name,
                event_type=event_type,
            )

    async def generate_prompt(self, template_name: str, **kwargs) -> str:
        """
        Generate prompt using template.

        Args:
            template_name: Name of prompt template
            **kwargs: Variables for template

        Returns:
            Rendered prompt
        """
        from src.llm.prompts import get_prompt_library

        library = get_prompt_library()
        return library.render(template_name, **kwargs)

    async def call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Call LLM with prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            LLM response text
        """
        logger.debug(
            "Calling LLM",
            agent=self.name,
            prompt_length=len(prompt),
        )

        response = await self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
        )

        logger.debug(
            "LLM response received",
            agent=self.name,
            response_length=len(response),
        )

        return response

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name={self.name})"
