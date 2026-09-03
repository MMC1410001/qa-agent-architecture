"""Projects API routes."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


class ProjectCreate(BaseModel):
    """Create project request."""

    name: str
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    """Project response."""

    id: str
    name: str
    description: Optional[str] = None


# In-memory storage for demo
projects_db = {}


@router.post("", response_model=ProjectResponse)
async def create_project(project: ProjectCreate) -> ProjectResponse:
    """
    Create a new project.

    Args:
        project: Project data

    Returns:
        Created project
    """
    import uuid

    project_id = str(uuid.uuid4())
    projects_db[project_id] = {
        "id": project_id,
        "name": project.name,
        "description": project.description,
    }
    return ProjectResponse(**projects_db[project_id])


@router.get("", response_model=List[ProjectResponse])
async def list_projects(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)) -> List[ProjectResponse]:
    """
    List all projects.

    Args:
        skip: Number of projects to skip
        limit: Maximum number of projects to return

    Returns:
        List of projects
    """
    items = list(projects_db.values())
    return items[skip : skip + limit]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str) -> ProjectResponse:
    """
    Get project by ID.

    Args:
        project_id: Project ID

    Returns:
        Project details

    Raises:
        HTTPException: If project not found
    """
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse(**projects_db[project_id])


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str, project: ProjectCreate
) -> ProjectResponse:
    """
    Update project.

    Args:
        project_id: Project ID
        project: Updated project data

    Returns:
        Updated project

    Raises:
        HTTPException: If project not found
    """
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    projects_db[project_id].update({
        "name": project.name,
        "description": project.description,
    })

    return ProjectResponse(**projects_db[project_id])


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """
    Delete project.

    Args:
        project_id: Project ID

    Raises:
        HTTPException: If project not found
    """
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    del projects_db[project_id]
    return {"deleted": True}
