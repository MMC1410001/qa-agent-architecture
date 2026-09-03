"""QA-OS FastAPI application."""

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from src.agents.automation_engineer import AutomationEngineerAgent
from src.agents.bug_investigator import BugInvestigatorAgent
from src.agents.quality_insights import QualityInsightsAgent
from src.agents.regression_planner import RegressionPlannerAgent
from src.agents.requirement_analyst import RequirementAnalystAgent
from src.agents.test_designer import TestDesignerAgent
from src.agents.test_runner import TestRunnerAgent
from src.api.routes import agents, executions, projects, reports, test_cases
from src.orchestrator.engine import OrchestrationEngine
from src.orchestrator.pipeline import DEFAULT_PIPELINES
from src.utils.logger import get_logger, setup_logging

# Setup logging
setup_logging(
    log_level=settings.api_log_level,
    format_style="json" if settings.is_production else "text",
)

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="QA-OS - AI-Powered QA Operating System",
    description="Intelligent test automation orchestration powered by LLMs",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestration engine
orchestrator = OrchestrationEngine()

# Register agents
agents_instances = [
    RequirementAnalystAgent(),
    TestDesignerAgent(),
    AutomationEngineerAgent(),
    TestRunnerAgent(),
    BugInvestigatorAgent(),
    RegressionPlannerAgent(),
    QualityInsightsAgent(),
]

for agent in agents_instances:
    orchestrator.register_agent(agent)

# Register pipelines
for pipeline_name, pipeline in DEFAULT_PIPELINES.items():
    orchestrator.register_pipeline(pipeline_name, pipeline.agents)

logger.info(
    "QA-OS initialized",
    agents=len(agents_instances),
    pipelines=len(DEFAULT_PIPELINES),
)

# Include API routers
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(test_cases.router, prefix="/api/test-cases", tags=["test-cases"])
app.include_router(executions.router, prefix="/api/executions", tags=["executions"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(
    agents.router,
    prefix="/api/agents",
    tags=["agents"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "QA-OS",
        "version": "1.0.0",
        "status": "running",
        "agents": orchestrator.get_registered_agents(),
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.environment,
        "debug": settings.debug,
    }


@app.get("/info")
async def info():
    """Get system information."""
    return {
        "name": "QA-OS",
        "version": "1.0.0",
        "description": "AI-Powered QA Operating System",
        "agents": {
            name: {
                "description": agent.config.description,
                "enabled": agent.config.enabled,
            }
            for name, agent in orchestrator.agents.items()
        },
        "pipelines": {
            name: agents for name, agents in orchestrator.get_registered_pipelines().items()
        },
        "settings": {
            "environment": settings.environment,
            "debug": settings.debug,
            "llm_provider": settings.llm.provider,
            "llm_model": settings.llm.model,
        },
    }


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    logger.warning("Validation error", error=str(exc))
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error("Unhandled exception", error=str(exc), exc_type=type(exc).__name__)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.api_log_level.lower(),
    )
