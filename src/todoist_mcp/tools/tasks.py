"""Todoist task management tools."""

from todoist_mcp.client import create_client
from todoist_mcp.server import mcp
from todoist_mcp.utils import get_logger, handle_todoist_errors

logger = get_logger("tasks")


@mcp.tool()
@handle_todoist_errors
def todoist_get_tasks(
    project_id: str | None = None,
    filter_string: str | None = None,
) -> str:
    """Get a list of tasks from Todoist with optional filters.

    Args:
        project_id: Optional project ID to filter tasks by project.
        filter_string: Optional filter/query string (e.g., "today", "overdue", "#work").

    Returns:
        A formatted string containing the list of tasks.
    """
    client = create_client()

    # Use filter_tasks if filter_string provided, otherwise use get_tasks
    if filter_string:
        tasks_iter = client.filter_tasks(query=filter_string)
    else:
        tasks_iter = client.get_tasks(project_id=project_id)

    # Collect all tasks from the iterator
    all_tasks = []
    for task_batch in tasks_iter:
        all_tasks.extend(task_batch)

    if not all_tasks:
        return "No tasks found."

    result = []
    for task in all_tasks:
        due_info = f" (Due: {task.due.string})" if task.due else ""
        priority_info = f" [P{task.priority}]" if task.priority else ""
        result.append(f"- {task.content}{due_info}{priority_info} (ID: {task.id})")

    return "\n".join(result)


@mcp.tool()
@handle_todoist_errors
def todoist_get_task(task_id: str) -> str:
    """Get a single task by ID.

    Args:
        task_id: The ID of the task to retrieve.

    Returns:
        A formatted string containing the task details.
    """
    client = create_client()

    task = client.get_task(task_id=task_id)

    result = [f"Task: {task.content}", f"ID: {task.id}"]

    if task.description:
        result.append(f"Description: {task.description}")

    if task.due:
        result.append(f"Due: {task.due.string}")

    if task.priority:
        result.append(f"Priority: P{task.priority}")

    if task.project_id:
        result.append(f"Project ID: {task.project_id}")

    if task.labels:
        result.append(f"Labels: {', '.join(task.labels)}")

    if task.is_completed:
        result.append("Status: Completed")
    else:
        result.append("Status: Not completed")

    return "\n".join(result)


@mcp.tool()
@handle_todoist_errors
def todoist_add_task(
    content: str,
    description: str | None = None,
    due_date: str | None = None,
    priority: int | None = None,
    project_id: str | None = None,
    labels: list[str] | None = None,
) -> str:
    """Create a new task in Todoist.

    Args:
        content: The task content/name.
        description: Optional task description.
        due_date: Optional due date string (e.g., "tomorrow", "2024-01-15", "next Monday").
        priority: Optional priority (1-4, where 4 is highest).
        project_id: Optional project ID to assign the task to.
        labels: Optional list of label names to apply.

    Returns:
        A confirmation message with the created task ID.
    """
    client = create_client()

    task = client.add_task(
        content=content,
        description=description,
        due_string=due_date,
        priority=priority,
        project_id=project_id,
        labels=labels,
    )

    return f"Task created: {task.content} (ID: {task.id})"


@mcp.tool()
@handle_todoist_errors
def todoist_update_task(
    task_id: str,
    content: str | None = None,
    description: str | None = None,
    due_date: str | None = None,
    priority: int | None = None,
    labels: list[str] | None = None,
) -> str:
    """Update an existing task in Todoist.

    Args:
        task_id: The ID of the task to update.
        content: Optional new task content.
        description: Optional new description.
        due_date: Optional new due date string.
        priority: Optional new priority (1-4).
        labels: Optional new list of label names.

    Returns:
        A confirmation message.
    """
    client = create_client()

    # Build update kwargs dynamically, excluding None values
    update_kwargs: dict = {}
    if content is not None:
        update_kwargs["content"] = content
    if description is not None:
        update_kwargs["description"] = description
    if due_date is not None:
        update_kwargs["due_string"] = due_date
    if priority is not None:
        update_kwargs["priority"] = priority
    if labels is not None:
        update_kwargs["labels"] = labels

    if not update_kwargs:
        return "Error: No update parameters provided."

    is_success = client.update_task(task_id=task_id, **update_kwargs)

    if is_success:
        return f"Task {task_id} updated successfully."
    return f"Error: Failed to update task {task_id}."


@mcp.tool()
@handle_todoist_errors
def todoist_complete_task(task_id: str) -> str:
    """Mark a task as complete.

    Args:
        task_id: The ID of the task to complete.

    Returns:
        A confirmation message.
    """
    client = create_client()

    is_success = client.complete_task(task_id=task_id)

    if is_success:
        return f"Task {task_id} completed successfully."
    return f"Error: Failed to complete task {task_id}."


@mcp.tool()
@handle_todoist_errors
def todoist_delete_task(task_id: str) -> str:
    """Delete a task by ID.

    Args:
        task_id: The ID of the task to delete.

    Returns:
        A confirmation message.
    """
    client = create_client()

    is_success = client.delete_task(task_id=task_id)

    if is_success:
        return f"Task {task_id} deleted successfully."
    return f"Error: Failed to delete task {task_id}."
