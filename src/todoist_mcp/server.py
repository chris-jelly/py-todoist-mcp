"""FastMCP server instance for Todoist integration."""

from fastmcp import FastMCP

from todoist_mcp.client import validate_token

# Validate token at module load time to fail fast
validate_token()

# Create the FastMCP server instance
mcp = FastMCP("todoist-mcp")
