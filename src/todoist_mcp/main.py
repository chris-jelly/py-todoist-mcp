"""Entry point for the Todoist MCP server."""

# Import tools to register them with the MCP server
from todoist_mcp.server import mcp
from todoist_mcp.tools import tasks  # noqa: F401
from todoist_mcp.utils import configure_logging, get_logger


def main() -> None:
    """Run the Todoist MCP server."""
    configure_logging()
    logger = get_logger(__name__)
    logger.info("Starting Todoist MCP server...")
    mcp.run()


if __name__ == "__main__":
    main()
