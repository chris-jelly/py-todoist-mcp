"""Todoist API client wrapper."""

import os

from todoist_api_python.api import TodoistAPI


def validate_token() -> str:
    """Validate that the TODOIST_API_TOKEN environment variable is set.

    Reads the token from the environment at call time (not import time)
    to support test fixtures that set the env var after module import.

    Returns:
        The API token value.

    Raises:
        RuntimeError: If TODOIST_API_TOKEN is not set.
    """
    token = os.environ.get("TODOIST_API_TOKEN")
    if not token:
        msg = (
            "TODOIST_API_TOKEN environment variable is required. "
            "Please set it to your Todoist API token."
        )
        raise RuntimeError(msg)
    return token


def create_client() -> TodoistAPI:
    """Create a Todoist API client instance.

    Returns:
        A configured TodoistAPI instance.

    Raises:
        RuntimeError: If TODOIST_API_TOKEN is not set.
    """
    token = validate_token()
    return TodoistAPI(token)
