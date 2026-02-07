"""Error handling utilities and structured logging for Todoist MCP server."""

import functools
import logging
from typing import Any, Callable, TypeVar

import requests.exceptions

F = TypeVar("F", bound=Callable[..., Any])

logger = logging.getLogger("todoist_mcp")


def configure_logging(level: int = logging.INFO) -> None:
    """Configure structured logging for the Todoist MCP server.

    Args:
        level: The logging level to use (default: INFO).
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Optional logger name suffix (e.g., 'tasks' -> 'todoist_mcp.tasks').

    Returns:
        A configured logger instance.
    """
    if name:
        return logging.getLogger(f"todoist_mcp.{name}")
    return logger


def handle_todoist_errors(func: F) -> F:
    """Decorator that catches Todoist API exceptions and returns user-friendly error strings.

    This decorator catches common exceptions from the todoist_api_python library
    and returns formatted error messages suitable for MCP tool responses.

    Args:
        func: The function to wrap.

    Returns:
        A wrapped function that handles exceptions.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            response = e.response
            status_code = response.status_code if response else "Unknown"

            # Map common HTTP status codes to user-friendly messages
            error_messages: dict[int, str] = {
                401: "Authentication failed. Please check your TODOIST_API_TOKEN.",
                403: "Access forbidden. Your API token may not have permission for this operation.",
                404: "Resource not found. The requested task or project does not exist.",
                429: "Rate limit exceeded. Please wait a moment before trying again.",
                500: "Todoist server error. Please try again later.",
                502: "Todoist server is temporarily unavailable. Please try again later.",
                503: "Todoist service is unavailable. Please try again later.",
            }

            message = error_messages.get(
                status_code,
                f"Todoist API error (HTTP {status_code}): {e!s}",
            )

            logger.error(f"HTTPError in {func.__name__}: {status_code} - {e}")  # noqa: TRY400
            return f"Error: {message}"

        except (TypeError, ValueError) as e:
            # These are typically validation or parsing errors
            logger.error(f"Validation error in {func.__name__}: {e}")  # noqa: TRY400
            return f"Error: Invalid input or response format - {e!s}"

        except Exception as e:
            # Catch-all for unexpected errors
            logger.exception(f"Unexpected error in {func.__name__}")
            return f"Error: An unexpected error occurred - {type(e).__name__}: {e!s}"

    return wrapper  # type: ignore[return-value]
