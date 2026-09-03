"""Agent configuration and I/O models."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Agent execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class AgentInput(BaseModel):
    """Input data for an agent."""

    data: Dict[str, Any] = Field(..., description="Input data dictionary")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Optional input metadata"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, description="Execution context"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "data": {
                    "document": "product requirements...",
                    "scope": "functional testing",
                },
                "metadata": {"source": "PRD", "version": "1.0"},
            }
        }


class AgentOutput(BaseModel):
    """Output data from an agent."""

    agent_name: str = Field(..., description="Name of agent that produced output")
    status: AgentStatus = Field(
        ..., description="Execution status"
    )
    data: Dict[str, Any] = Field(..., description="Output data")
    error: Optional[str] = Field(
        None, description="Error message if execution failed"
    )
    error_type: Optional[str] = Field(
        None, description="Type of error"
    )
    execution_time_seconds: float = Field(
        ..., description="Time taken to execute"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Execution timestamp"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Output metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "agent_name": "requirement_analyst",
                "status": "completed",
                "data": {
                    "requirements": [
                        {
                            "id": "REQ-001",
                            "title": "User login",
                            "test_scenarios": ["valid login", "invalid password"],
                        }
                    ]
                },
                "execution_time_seconds": 45.2,
                "timestamp": "2024-01-01T10:00:00Z",
            }
        }


class AgentConfig(BaseModel):
    """Configuration for an agent."""

    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    enabled: bool = Field(True, description="Whether agent is enabled")

    # Execution settings
    timeout: int = Field(300, description="Timeout in seconds")
    retry_attempts: int = Field(3, description="Number of retry attempts")
    retry_delay: int = Field(5, description="Delay between retries in seconds")

    # LLM settings
    max_tokens: int = Field(4096, description="Max tokens for LLM response")
    temperature: float = Field(
        0.7, ge=0, le=1, description="LLM temperature"
    )
    prompt_template: Optional[str] = Field(
        None, description="Prompt template name"
    )

    # Input/Output configuration
    inputs: List[Dict[str, str]] = Field(
        default_factory=list, description="Input field definitions"
    )
    outputs: List[Dict[str, str]] = Field(
        default_factory=list, description="Output field definitions"
    )

    # Validation
    validation_rules: Optional[Dict[str, Any]] = Field(
        None, description="Validation rules for inputs/outputs"
    )

    # Custom settings
    settings: Dict[str, Any] = Field(
        default_factory=dict, description="Custom agent settings"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "requirement_analyst",
                "description": "Analyzes requirements and extracts test cases",
                "enabled": True,
                "timeout": 300,
                "retry_attempts": 3,
                "max_tokens": 4096,
                "temperature": 0.7,
                "inputs": [
                    {
                        "type": "document",
                        "description": "Product requirements document",
                    },
                    {
                        "type": "test_scope",
                        "description": "Scope of testing",
                    },
                ],
                "outputs": [
                    {
                        "type": "requirements",
                        "description": "Extracted requirements",
                    }
                ],
                "validation_rules": {
                    "min_requirements": 1,
                    "max_requirements": 1000,
                },
            }
        }
