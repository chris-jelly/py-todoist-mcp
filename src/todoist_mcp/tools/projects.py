"""Todoist project management tools."""

from todoist_mcp.client import create_client
from todoist_mcp.server import mcp
from todoist_mcp.utils import get_logger, handle_todoist_errors

logger = get_logger("projects")


@mcp.tool()
@handle_todoist_errors
def todoist_get_projects() -> str:
    """Get a list of all projects from Todoist.

    Returns:
        A formatted string containing the list of projects.
    """
    client = create_client()

    projects_iter = client.get_projects()

    # Collect all projects from the paginator
    all_projects = []
    for project_batch in projects_iter:
        all_projects.extend(project_batch)

    if not all_projects:
        return "No projects found."

    result = []
    for project in all_projects:
        color_info = f" (Color: {project.color})" if project.color else ""
        parent_info = f" [Parent: {project.parent_id}]" if project.parent_id else ""
        result.append(f"- {project.name}{color_info}{parent_info} (ID: {project.id})")

    return "\n".join(result)


@mcp.tool()
@handle_todoist_errors
def todoist_get_project(project_id: str) -> str:
    """Get a single project by ID.

    Args:
        project_id: The ID of the project to retrieve.

    Returns:
        A formatted string containing the project details.
    """
    client = create_client()

    project = client.get_project(project_id=project_id)

    result = [f"Project: {project.name}", f"ID: {project.id}"]

    if project.color:
        result.append(f"Color: {project.color}")

    if project.parent_id:
        result.append(f"Parent ID: {project.parent_id}")

    if project.is_favorite:
        result.append("Favorite: Yes")
    else:
        result.append("Favorite: No")

    return "\n".join(result)


@mcp.tool()
@handle_todoist_errors
def todoist_add_project(
    name: str,
    color: str | None = None,
    parent_id: str | None = None,
) -> str:
    """Create a new project in Todoist.

    Args:
        name: The project name.
        color: Optional color for the project (e.g., "red", "blue", "#ff9900").
        parent_id: Optional parent project ID for nested projects.

    Returns:
        A confirmation message with the created project ID.
    """
    client = create_client()

    project = client.add_project(
        name=name,
        color=color,
        parent_id=parent_id,
    )

    return f"Project created: {project.name} (ID: {project.id})"


@mcp.tool()
@handle_todoist_errors
def todoist_update_project(
    project_id: str,
    name: str | None = None,
    color: str | None = None,
    is_favorite: bool | None = None,
) -> str:
    """Update an existing project in Todoist.

    Args:
        project_id: The ID of the project to update.
        name: Optional new project name.
        color: Optional new color for the project.
        is_favorite: Optional flag to mark project as favorite.

    Returns:
        A confirmation message.
    """
    client = create_client()

    # Build update kwargs dynamically, excluding None values
    update_kwargs: dict = {}
    if name is not None:
        update_kwargs["name"] = name
    if color is not None:
        update_kwargs["color"] = color
    if is_favorite is not None:
        update_kwargs["is_favorite"] = is_favorite

    if not update_kwargs:
        return "Error: No update parameters provided."

    is_success = client.update_project(project_id=project_id, **update_kwargs)

    if is_success:
        return f"Project {project_id} updated successfully."
    return f"Error: Failed to update project {project_id}."


@mcp.tool()
@handle_todoist_errors
def todoist_delete_project(project_id: str) -> str:
    """Delete a project by ID.

    Args:
        project_id: The ID of the project to delete.

    Returns:
        A confirmation message.
    """
    client = create_client()

    is_success = client.delete_project(project_id=project_id)

    if is_success:
        return f"Project {project_id} deleted successfully."
    return f"Error: Failed to delete project {project_id}."
