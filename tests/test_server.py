"""Tests for the FastMCP server module."""

from fastmcp import FastMCP

from todoist_mcp import server


class TestMCPServer:
    """Tests for the FastMCP server instance."""

    def test_mcp_instance_exists(self) -> None:
        """Test that mcp is a FastMCP instance."""
        assert isinstance(server.mcp, FastMCP)

    def test_mcp_instance_name(self) -> None:
        """Test that the server name is 'todoist-mcp'."""
        assert server.mcp.name == "todoist-mcp"
