"""Shared fixtures for Todoist MCP tests."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_todoist_client() -> Generator[MagicMock, None, None]:
    """Mock the TodoistAPI client for testing.

    Patches create_client() to return a MagicMock instead of making real API calls.
    """
    with patch("todoist_mcp.client.create_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def fake_task() -> MagicMock:
    """Create a mock Task with realistic attributes.

    Returns a MagicMock configured with typical task properties:
    - content: Task title/content
    - id: Unique identifier
    - description: Task description
    - due: Due date object with string attribute
    - priority: Priority level (1-4)
    - project_id: Associated project ID
    - labels: List of label names
    - is_completed: Completion status
    """
    task = MagicMock()
    task.content = "Complete project documentation"
    task.id = "1234567890"
    task.description = "Write comprehensive README and API docs"
    task.due = MagicMock()
    task.due.string = "2024-03-15"
    task.priority = 4
    task.project_id = "9876543210"
    task.labels = ["work", "documentation"]
    task.is_completed = False
    return task


@pytest.fixture
def fake_minimal_task() -> MagicMock:
    """Create a mock Task with minimal attributes (no optional fields).

    Useful for testing tasks with only required fields populated.
    """
    task = MagicMock()
    task.content = "Simple task"
    task.id = "1111111111"
    task.description = None
    task.due = None
    task.priority = None
    task.project_id = None
    task.labels = []
    task.is_completed = False
    return task


@pytest.fixture
def fake_project() -> MagicMock:
    """Create a mock Project with realistic attributes.

    Returns a MagicMock configured with typical project properties:
    - name: Project name
    - id: Unique identifier
    - color: Color identifier
    - parent_id: Parent project ID for nested projects
    - is_favorite: Favorite status
    """
    project = MagicMock()
    project.name = "Work Projects"
    project.id = "9876543210"
    project.color = "red"
    project.parent_id = None
    project.is_favorite = True
    return project


@pytest.fixture
def fake_nested_project() -> MagicMock:
    """Create a mock Project with parent_id set (nested project).

    Useful for testing nested project functionality.
    """
    project = MagicMock()
    project.name = "Q1 Goals"
    project.id = "5555555555"
    project.color = "blue"
    project.parent_id = "9876543210"
    project.is_favorite = False
    return project


@pytest.fixture(autouse=True)
def env_with_token(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """Automatically set TODOIST_API_TOKEN for unit tests only.

    This fixture runs automatically (autouse=True) to ensure unit tests
    have a valid API token environment variable set, preventing
    RuntimeError when importing modules that check for the token.

    Skips for integration tests so the real token is preserved.
    """
    if "integration" in {mark.name for mark in request.node.iter_markers()}:
        return
    monkeypatch.setenv("TODOIST_API_TOKEN", "test-token-12345")
