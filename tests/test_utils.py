"""Unit tests for error handling utilities and logging functions."""

import logging
from unittest.mock import MagicMock, patch

import requests.exceptions

from todoist_mcp.utils import configure_logging, get_logger, handle_todoist_errors


class TestConfigureLogging:
    """Tests for configure_logging function."""

    def test_configure_logging_sets_level(self) -> None:
        """Verify logging configuration applies the correct level."""
        with patch("logging.basicConfig") as mock_basic_config:
            configure_logging(level=logging.DEBUG)
            mock_basic_config.assert_called_once()
            call_kwargs = mock_basic_config.call_args.kwargs
            assert call_kwargs["level"] == logging.DEBUG


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_with_name(self) -> None:
        """Returns logger with todoist_mcp.{name} namespace."""
        logger = get_logger("tasks")
        assert logger.name == "todoist_mcp.tasks"

    def test_get_logger_without_name(self) -> None:
        """Returns base todoist_mcp logger."""
        logger = get_logger()
        assert logger.name == "todoist_mcp"


class TestHandleTodoistErrors:
    """Tests for handle_todoist_errors decorator."""

    @staticmethod
    def create_http_error(status_code: int) -> requests.exceptions.HTTPError:
        """Helper to create an HTTPError with a mocked response."""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        error = requests.exceptions.HTTPError("HTTP Error")
        error.response = mock_response
        return error

    def test_handle_todoist_errors_http_401(self) -> None:
        """Returns auth error message for HTTP 401."""

        @handle_todoist_errors
        def func_that_raises() -> str:
            raise self.create_http_error(401)

        result = func_that_raises()
        assert "Authentication failed" in result
        assert "Error:" in result

    def test_handle_todoist_errors_http_404(self) -> None:
        """Returns not found message for HTTP 404."""

        @handle_todoist_errors
        def func_that_raises() -> str:
            raise self.create_http_error(404)

        result = func_that_raises()
        assert "not found" in result.lower()
        assert "Error:" in result

    def test_handle_todoist_errors_http_429(self) -> None:
        """Returns rate limit message for HTTP 429."""

        @handle_todoist_errors
        def func_that_raises() -> str:
            raise self.create_http_error(429)

        result = func_that_raises()
        assert "Rate limit" in result
        assert "Error:" in result

    def test_handle_todoist_errors_http_500(self) -> None:
        """Returns server error message for HTTP 500."""

        @handle_todoist_errors
        def func_that_raises() -> str:
            raise self.create_http_error(500)

        result = func_that_raises()
        assert "server error" in result.lower()
        assert "Error:" in result

    def test_handle_todoist_errors_http_unknown(self) -> None:
        """Returns generic HTTP error for unknown status codes."""

        @handle_todoist_errors
        def func_that_raises() -> str:
            raise self.create_http_error(418)  # I'm a teapot

        result = func_that_raises()
        assert "HTTP 418" in result
        assert "Error:" in result

    def test_handle_todoist_errors_type_error(self) -> None:
        """Returns validation error for TypeError."""

        @handle_todoist_errors
        def func_that_raises() -> str:
            raise TypeError("Invalid type provided")

        result = func_that_raises()
        assert "Invalid input" in result
        assert "Error:" in result

    def test_handle_todoist_errors_value_error(self) -> None:
        """Returns validation error for ValueError."""

        @handle_todoist_errors
        def func_that_raises() -> str:
            raise ValueError("Invalid value provided")

        result = func_that_raises()
        assert "Invalid input" in result
        assert "Error:" in result

    def test_handle_todoist_errors_unexpected(self) -> None:
        """Returns unexpected error with type name for unknown exceptions."""

        @handle_todoist_errors
        def func_that_raises() -> str:
            raise RuntimeError("Something went wrong")

        result = func_that_raises()
        assert "unexpected error" in result.lower()
        assert "RuntimeError" in result
        assert "Error:" in result

    def test_handle_todoist_errors_success(self) -> None:
        """Passes through normal return value when no exception."""

        @handle_todoist_errors
        def func_that_succeeds() -> str:
            return "Success!"

        result = func_that_succeeds()
        assert result == "Success!"

    def test_handle_todoist_errors_preserves_function_metadata(self) -> None:
        """Decorator preserves original function name and docstring."""

        @handle_todoist_errors
        def my_function() -> str:
            """My docstring."""
            return "result"

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."
