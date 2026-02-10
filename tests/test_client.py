"""Tests for the Todoist API client module."""

import pytest
from todoist_api_python.api import TodoistAPI

from todoist_mcp import client


class TestValidateToken:
    """Tests for validate_token function."""

    def test_validate_token_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that validate_token returns the token when set."""
        monkeypatch.setattr(client, "TODOIST_API_TOKEN", "valid-token-123")

        result = client.validate_token()

        assert result == "valid-token-123"

    def test_validate_token_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that validate_token raises RuntimeError when token is missing."""
        monkeypatch.setattr(client, "TODOIST_API_TOKEN", None)

        with pytest.raises(RuntimeError) as exc_info:
            client.validate_token()

        assert "TODOIST_API_TOKEN environment variable is required" in str(exc_info.value)


class TestCreateClient:
    """Tests for create_client function."""

    def test_create_client_returns_todoist_api(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that create_client returns a TodoistAPI instance."""
        monkeypatch.setattr(client, "TODOIST_API_TOKEN", "test-token")

        result = client.create_client()

        assert isinstance(result, TodoistAPI)
        assert result._token == "test-token"

    def test_create_client_calls_validate_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that create_client validates the token during creation."""
        monkeypatch.setattr(client, "TODOIST_API_TOKEN", None)

        with pytest.raises(RuntimeError, match="TODOIST_API_TOKEN"):
            client.create_client()
