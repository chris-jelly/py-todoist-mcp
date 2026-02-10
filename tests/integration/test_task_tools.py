"""Integration tests for Todoist task tool functions."""

import re

import pytest
from todoist_api_python.api import TodoistAPI

from todoist_mcp.tools.tasks import (
    todoist_add_task,
    todoist_complete_task,
    todoist_delete_task,
    todoist_get_task,
    todoist_get_tasks,
    todoist_update_task,
)

pytestmark = pytest.mark.integration

# The @mcp.tool() decorator wraps functions in FunctionTool objects.
# Access the underlying function via .fn for direct invocation.
_get_tasks = todoist_get_tasks.fn
_get_task = todoist_get_task.fn
_add_task = todoist_add_task.fn
_update_task = todoist_update_task.fn
_complete_task = todoist_complete_task.fn
_delete_task = todoist_delete_task.fn


@pytest.mark.timeout(30)
class TestGetTasks:
    """Tests for todoist_get_tasks against the live API."""

    def test_get_tasks(self, test_project: str, test_task: dict[str, str]) -> None:
        """Verify todoist_get_tasks returns tasks from the test project."""
        result = _get_tasks(project_id=test_project)

        assert test_task["content"] in result
        assert test_task["id"] in result


@pytest.mark.timeout(30)
class TestGetTask:
    """Tests for todoist_get_task against the live API."""

    def test_get_task(self, test_task: dict[str, str]) -> None:
        """Verify todoist_get_task returns task details for a known task."""
        result = _get_task(task_id=test_task["id"])

        assert test_task["content"] in result
        assert test_task["id"] in result
        assert "Status:" in result


@pytest.mark.timeout(30)
class TestAddTask:
    """Tests for todoist_add_task against the live API."""

    def test_add_task(self, api_client: TodoistAPI, test_project: str) -> None:
        """Verify todoist_add_task creates a task and returns confirmation."""
        result = _add_task(
            content="[TEST] Added by integration test",
            project_id=test_project,
        )

        assert "Task created" in result

        # Extract task ID from result (Todoist IDs are alphanumeric)
        match = re.search(r"ID: (\S+)\)?", result)
        assert match is not None
        task_id = match.group(1).rstrip(")")

        try:
            # Verify via separate API call
            task = api_client.get_task(task_id=task_id)
            assert task.content == "[TEST] Added by integration test"
        finally:
            api_client.delete_task(task_id=task_id)


@pytest.mark.timeout(30)
class TestUpdateTask:
    """Tests for todoist_update_task against the live API."""

    def test_update_task(self, api_client: TodoistAPI, test_task: dict[str, str]) -> None:
        """Verify todoist_update_task modifies a task and returns success."""
        result = _update_task(
            task_id=test_task["id"],
            content="[TEST] Updated by integration test",
        )

        assert "updated successfully" in result

        # Verify via separate API call
        task = api_client.get_task(task_id=test_task["id"])
        assert task.content == "[TEST] Updated by integration test"


@pytest.mark.timeout(30)
class TestCompleteTask:
    """Tests for todoist_complete_task against the live API."""

    def test_complete_task(self, test_task: dict[str, str]) -> None:
        """Verify todoist_complete_task marks a task as complete."""
        result = _complete_task(task_id=test_task["id"])

        assert "completed successfully" in result


@pytest.mark.timeout(30)
class TestDeleteTask:
    """Tests for todoist_delete_task against the live API."""

    def test_delete_task(self, api_client: TodoistAPI, test_project: str) -> None:
        """Verify todoist_delete_task removes a task."""
        # Create a temporary task specifically for deletion
        task = api_client.add_task(
            content="[TEST] Task to be deleted",
            project_id=test_project,
        )

        result = _delete_task(task_id=task.id)

        assert "deleted successfully" in result
