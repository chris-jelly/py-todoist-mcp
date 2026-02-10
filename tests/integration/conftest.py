"""Fixtures for integration tests against the live Todoist API."""

import os
from collections.abc import Generator
from datetime import datetime, timezone

import pytest
from todoist_api_python.api import TodoistAPI

# Skip all integration tests if no real token is available
_token = os.environ.get("TODOIST_API_TOKEN")
if not _token or _token == "test-token-12345":
    pytest.skip(
        "TODOIST_API_TOKEN not set or is the fake test token; skipping integration tests",
        allow_module_level=True,
    )

# Store the real token at import time so teardown always has access,
# even if env vars are modified by other fixtures during the session.
_REAL_TOKEN: str = _token


@pytest.fixture(scope="session")
def api_client() -> TodoistAPI:
    """Create a real TodoistAPI client for verification calls."""
    return TodoistAPI(_REAL_TOKEN)


@pytest.fixture(scope="session")
def test_project(api_client: TodoistAPI) -> Generator[str, None, None]:
    """Create a dedicated test project and tear it down after the session.

    Yields:
        The project ID of the created test project.
    """
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%S")
    project_name = f"[TEST] Integration - {timestamp}"

    project = api_client.add_project(name=project_name)
    project_id = project.id

    try:
        yield project_id
    finally:
        # Use a fresh client for teardown to ensure clean state
        try:
            teardown_client = TodoistAPI(_REAL_TOKEN)
            teardown_client.delete_project(project_id=project_id)
        except Exception as exc:
            import warnings

            warnings.warn(
                f"Failed to clean up test project {project_id}: {exc}",
                stacklevel=1,
            )


@pytest.fixture
def test_task(api_client: TodoistAPI, test_project: str) -> Generator[dict[str, str], None, None]:
    """Create a task in the test project for each test that needs one.

    Yields:
        A dict with 'id' and 'content' keys for the created task.
    """
    task = api_client.add_task(
        content="[TEST] Integration test task",
        project_id=test_project,
    )
    task_data = {"id": task.id, "content": task.content}

    try:
        yield task_data
    finally:
        try:
            api_client.delete_task(task_id=task.id)
        except Exception:
            # Best-effort cleanup; task may already be deleted/completed by a test
            pass
