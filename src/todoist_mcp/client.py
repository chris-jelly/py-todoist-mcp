"""Todoist API client wrapper."""

import os
from typing import Final

from todoist_api_python.api import TodoistAPI

TODOIST_API_TOKEN: Final[str | None] = os.environ.get("TODOIST_API_TOKEN")


def validate_token() -> str:
    """Validate that the TODOIST_API_TOKEN environment variable is set.

    Returns:
        The API token value.

    Raises:
        RuntimeError: If TODOIST_API_TOKEN is not set.
    """
    if not TODOIST_API_TOKEN:
        msg = (
            "TODOIST_API_TOKEN environment variable is required. "
            "Please set it to your Todoist API token."
        )
        raise RuntimeError(msg)
    return TODOIST_API_TOKEN


def create_client() -> TodoistAPI:
    """Create a Todoist API client instance.

    Returns:
        A configured TodoistAPI instance.

    Raises:
        RuntimeError: If TODOIST_API_TOKEN is not set.
    """
    token = validate_token()
    return TodoistAPI(token)
