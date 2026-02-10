"""Integration tests for Todoist project tool functions."""

import re

import pytest
from todoist_api_python.api import TodoistAPI

from todoist_mcp.tools.projects import (
    todoist_add_project,
    todoist_delete_project,
    todoist_get_project,
    todoist_get_projects,
    todoist_update_project,
)

pytestmark = pytest.mark.integration

# The @mcp.tool() decorator wraps functions in FunctionTool objects.
# Access the underlying function via .fn for direct invocation.
_get_projects = todoist_get_projects.fn
_get_project = todoist_get_project.fn
_add_project = todoist_add_project.fn
_update_project = todoist_update_project.fn
_delete_project = todoist_delete_project.fn


@pytest.mark.timeout(30)
class TestGetProjects:
    """Tests for todoist_get_projects against the live API."""

    def test_get_projects(self, test_project: str, api_client: TodoistAPI) -> None:
        """Verify todoist_get_projects includes the test project."""
        # Get the project name for assertion
        project = api_client.get_project(project_id=test_project)

        result = _get_projects()

        assert project.name in result
        assert test_project in result


@pytest.mark.timeout(30)
class TestGetProject:
    """Tests for todoist_get_project against the live API."""

    def test_get_project(self, test_project: str, api_client: TodoistAPI) -> None:
        """Verify todoist_get_project returns details for the test project."""
        project = api_client.get_project(project_id=test_project)

        result = _get_project(project_id=test_project)

        assert project.name in result
        assert test_project in result
        assert "Favorite:" in result


@pytest.mark.timeout(30)
class TestAddProject:
    """Tests for todoist_add_project against the live API."""

    def test_add_project(self, api_client: TodoistAPI) -> None:
        """Verify todoist_add_project creates a project and returns confirmation."""
        result = _add_project(name="[TEST] Sub-project")

        assert "Project created" in result

        # Extract project ID from result (Todoist IDs are alphanumeric)
        match = re.search(r"ID: (\S+)\)?", result)
        assert match is not None
        project_id = match.group(1).rstrip(")")

        try:
            # Verify via separate API call
            project = api_client.get_project(project_id=project_id)
            assert project.name == "[TEST] Sub-project"
        finally:
            api_client.delete_project(project_id=project_id)


@pytest.mark.timeout(30)
class TestUpdateProject:
    """Tests for todoist_update_project against the live API."""

    def test_update_project(self, api_client: TodoistAPI, test_project: str) -> None:
        """Verify todoist_update_project modifies a project and returns success."""
        # Get original name to restore later
        original = api_client.get_project(project_id=test_project)
        original_name = original.name

        try:
            result = _update_project(
                project_id=test_project,
                name="[TEST] Updated",
            )

            assert "updated successfully" in result

            # Verify via separate API call
            project = api_client.get_project(project_id=test_project)
            assert project.name == "[TEST] Updated"
        finally:
            # Restore original name
            api_client.update_project(project_id=test_project, name=original_name)


@pytest.mark.timeout(30)
class TestDeleteProject:
    """Tests for todoist_delete_project against the live API."""

    def test_delete_project(self, api_client: TodoistAPI) -> None:
        """Verify todoist_delete_project removes a project."""
        # Create a temporary project specifically for deletion
        project = api_client.add_project(name="[TEST] Project to be deleted")

        result = _delete_project(project_id=project.id)

        assert "deleted successfully" in result
