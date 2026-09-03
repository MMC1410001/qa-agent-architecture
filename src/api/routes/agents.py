"""Agents API routes."""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class AgentInfoResponse(BaseModel):
    """Agent information response."""

    name: str
    description: str
    enabled: bool


class ExecuteAgentRequest(BaseModel):
    """Execute agent request."""

    data: Dict[str, Any]


@router.get("", response_model=List[str])
async def list_agents() -> List[str]:
    """
    List available agents.

    Returns:
        List of agent names
    """
    return [
        "requirement_analyst",
        "test_designer",
        "automation_engineer",
        "test_runner",
        "bug_investigator",
        "regression_planner",
        "quality_insights",
    ]


@router.get("/{agent_name}", response_model=AgentInfoResponse)
async def get_agent(agent_name: str) -> AgentInfoResponse:
    """
    Get agent information.

    Args:
        agent_name: Name of agent

    Returns:
        Agent information

    Raises:
        HTTPException: If agent not found
    """
    agents_info = {
        "requirement_analyst": {
            "description": "Analyzes requirements and extracts testable test cases",
            "enabled": True,
        },
        "test_designer": {
            "description": "Designs comprehensive test cases with coverage analysis",
            "enabled": True,
        },
        "automation_engineer": {
            "description": "Creates automation scripts and page objects",
            "enabled": True,
        },
        "test_runner": {
            "description": "Executes tests and manages execution environments",
            "enabled": True,
        },
        "bug_investigator": {
            "description": "Analyzes test failures and generates bug reports",
            "enabled": True,
        },
        "regression_planner": {
            "description": "Plans and optimizes regression test suites",
            "enabled": True,
        },
        "quality_insights": {
            "description": "Generates quality metrics and insights",
            "enabled": True,
        },
    }

    if agent_name not in agents_info:
        raise HTTPException(status_code=404, detail="Agent not found")

    return AgentInfoResponse(
        name=agent_name,
        **agents_info[agent_name],
    )


@router.post("/{agent_name}/execute")
async def execute_agent(agent_name: str, request: ExecuteAgentRequest) -> Dict:
    """
    Execute a specific agent.

    Args:
        agent_name: Name of agent to execute
        request: Execution request with input data

    Returns:
        Execution result

    Raises:
        HTTPException: If agent not found
    """
    valid_agents = [
        "requirement_analyst",
        "test_designer",
        "automation_engineer",
        "test_runner",
        "bug_investigator",
        "regression_planner",
        "quality_insights",
    ]

    if agent_name not in valid_agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    # In a real implementation, would execute the agent
    return {
        "agent": agent_name,
        "status": "executed",
        "input_size": len(str(request.data)),
    }
