# py-todoist-mcp

A Python MCP (Model Context Protocol) server for Todoist integration, enabling AI assistants to manage tasks and projects via the Model Context Protocol.

## Features

- **Task Management**: Create, read, update, complete, and delete tasks
- **Project Management**: Manage Todoist projects with support for nested projects
- **Filter Support**: Query tasks using Todoist's powerful filter syntax
- **Error Handling**: Robust error handling with user-friendly messages
- **Structured Logging**: Comprehensive logging for debugging and monitoring

## Prerequisites

- Python 3.14 or higher
- [uv](https://github.com/astral-sh/uv) for Python package management
- A Todoist API token

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd py-todoist-mcp
```

### 2. Install dependencies with uv

```bash
uv sync
```

Or install in development mode:

```bash
uv pip install -e ".[dev]"
```

### 3. Set up your API token

The server reads `TODOIST_API_TOKEN` from the environment. Set it in your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) so it's always available:

```bash
# Add to your shell profile
export TODOIST_API_TOKEN="your-api-token-here"
```

To obtain your Todoist API token:
1. Log in to [Todoist](https://todoist.com)
2. Go to Settings → Integrations → Developer
3. Copy your API token

> **Note:** Avoid placing your API token directly in MCP configuration files (e.g., `opencode.json`). These files are easy to accidentally commit or share. The server will pick up the token from your environment automatically.

## Configuration

### Opencode

Add the following configuration to your Opencode `~/.config/opencode/opencode.json`:

```json
{
  "mcpServers": {
    "todoist": {
      "command": "uv",
      "args": [
        "run",
        "--python",
        "3.14",
        "todoist-mcp"
      ],
      "env": {
        "TODOIST_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

### Codex

Add the following to your Codex configuration file (location varies by installation):

```json
{
  "mcpServers": {
    "todoist": {
      "command": "uv",
      "args": [
        "run",
        "--python",
        "3.14",
        "todoist-mcp"
      ],
      "env": {
        "TODOIST_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

## Usage

Once configured, you can use natural language to interact with Todoist:

### Task Examples

```
"Show me all my tasks"
"List my tasks for today"
"Create a task 'Buy groceries' due tomorrow with priority 1"
"Get details for task ID 123456"
"Update task 123456 to be due next Monday"
"Mark task 123456 as complete"
"Delete task 123456"
```

### Project Examples

```
"List all my projects"
"Create a new project called 'Work'"
"Get details for project ID 987654"
"Update project 987654 color to blue"
"Delete project 987654"
```

### Filter Examples

```
"Show me overdue tasks"
"List tasks in project work"
"Get tasks labeled urgent"
```

## Available Tools

### Task Tools

| Tool | Description |
|------|-------------|
| `todoist_get_tasks` | List tasks with optional filters (project_id, filter_string) |
| `todoist_get_task` | Get a single task by ID with full details |
| `todoist_add_task` | Create a new task with content, description, due_date, priority, project_id, labels |
| `todoist_update_task` | Update task attributes by ID |
| `todoist_complete_task` | Mark a task as complete by ID |
| `todoist_delete_task` | Delete a task by ID |

### Project Tools

| Tool | Description |
|------|-------------|
| `todoist_get_projects` | List all projects |
| `todoist_get_project` | Get a single project by ID with full details |
| `todoist_add_project` | Create a new project with name, color, parent_id |
| `todoist_update_project` | Update project attributes by ID |
| `todoist_delete_project` | Delete a project by ID |

## Development

### Running the server locally

```bash
# Set your API token
export TODOIST_API_TOKEN="your-api-token-here"

# Run the server
uv run todoist-mcp
```

### Code Quality

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Format code
ruff format .

# Check for linting errors
ruff check .

# Fix auto-fixable issues
ruff check . --fix
```

### Project Structure

```
py-todoist-mcp/
├── src/todoist_mcp/
│   ├── __init__.py
│   ├── main.py          # Entry point
│   ├── server.py        # FastMCP server setup
│   ├── client.py        # Todoist API client
│   ├── utils.py         # Logging and error handling
│   └── tools/
│       ├── __init__.py
│       ├── tasks.py     # Task management tools
│       └── projects.py  # Project management tools
├── pyproject.toml
└── README.md
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please ensure:

1. All code passes `ruff lint` and `ruff format` checks
2. Follow the existing code patterns and conventions
3. Add tests for new functionality
4. Update documentation as needed

## Troubleshooting

### Server won't start

- Verify `TODOIST_API_TOKEN` is set correctly
- Check that Python 3.14+ is installed: `python --version`
- Ensure uv is installed: `uv --version`

### Authentication errors

- Verify your API token is correct and hasn't expired
- Check that your Todoist account is active
- Ensure the token has appropriate permissions

### AI Assistant not connecting

**For Opencode:**
- Verify the configuration JSON syntax
- Check the Opencode logs: `~/.config/opencode/logs/`
- Run `opencode --version` to ensure it's installed correctly
- Restart Opencode after configuration changes

**For Codex:**
- Verify the configuration JSON syntax
- Check Codex output for error messages
- Restart Codex after configuration changes
