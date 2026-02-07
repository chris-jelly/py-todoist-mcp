"""Entry point for the Todoist MCP server."""

import logging

from todoist_mcp.server import mcp


def main() -> None:
    """Run the Todoist MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting Todoist MCP server...")
    mcp.run()


if __name__ == "__main__":
    main()
