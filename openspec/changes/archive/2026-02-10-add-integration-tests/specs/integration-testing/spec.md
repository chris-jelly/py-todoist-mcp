## ADDED Requirements

### Requirement: Integration test marker isolation
The system SHALL register a `pytest.mark.integration` marker and exclude it from default test runs via `addopts = "-m 'not integration'"` in `pyproject.toml`. Integration tests SHALL only run when explicitly requested with `pytest -m integration`.

#### Scenario: Default pytest invocation skips integration tests
- **WHEN** a developer runs `pytest` with no marker arguments
- **THEN** only unit tests execute; no integration tests are collected or run

#### Scenario: Explicit marker invocation runs integration tests
- **WHEN** a developer runs `pytest -m integration`
- **THEN** only tests marked with `@pytest.mark.integration` are collected and run

### Requirement: Integration test directory structure
The system SHALL place all integration tests in `tests/integration/` with a dedicated `conftest.py` that provides live API fixtures. The directory SHALL contain `test_task_tools.py` and `test_project_tools.py` test modules.

#### Scenario: Integration conftest provides real API fixtures
- **WHEN** integration tests are collected
- **THEN** the `tests/integration/conftest.py` provides `test_project`, `test_task`, and `api_client` fixtures backed by the real Todoist API

### Requirement: Session-scoped test project lifecycle
The system SHALL create a dedicated Todoist project named `[TEST] Integration - {timestamp}` at the start of the integration test session and delete it at session teardown. The fixture SHALL use `try/finally` to ensure cleanup runs even on test failures.

#### Scenario: Test project created at session start
- **WHEN** the integration test session begins
- **THEN** a new Todoist project with name matching `[TEST] Integration - *` is created via the Todoist API

#### Scenario: Test project deleted at session end
- **WHEN** the integration test session ends (regardless of pass/fail)
- **THEN** the test project is deleted from Todoist via the API

#### Scenario: Test project cleanup on mid-suite failure
- **WHEN** a test fails mid-suite and the session terminates
- **THEN** the `try/finally` teardown still deletes the test project

### Requirement: Function-scoped test task lifecycle
The system SHALL provide a function-scoped `test_task` fixture that creates a task in the test project before each test that requests it, and deletes the task after the test completes. The fixture SHALL use `try/finally` for cleanup.

#### Scenario: Fresh task per test
- **WHEN** a test function requests the `test_task` fixture
- **THEN** a new task is created in the session's test project before the test body runs

#### Scenario: Task cleanup after test
- **WHEN** a test function using `test_task` completes (pass or fail)
- **THEN** the task is deleted from Todoist

### Requirement: Integration test for todoist_get_tasks
The system SHALL include a test that calls `todoist_get_tasks` with the test project ID and verifies tasks are returned in formatted string output.

#### Scenario: Get tasks from test project
- **WHEN** `todoist_get_tasks(project_id=test_project_id)` is called with a project containing at least one task
- **THEN** the result is a non-empty string containing the task content and ID

### Requirement: Integration test for todoist_get_task
The system SHALL include a test that calls `todoist_get_task` with a known task ID and verifies the formatted detail output.

#### Scenario: Get single task by ID
- **WHEN** `todoist_get_task(task_id=known_task_id)` is called
- **THEN** the result contains the task content, ID, and status fields

### Requirement: Integration test for todoist_add_task
The system SHALL include a test that calls `todoist_add_task` to create a task in the test project, verifies the confirmation message, and confirms the task exists via a separate API client call. The test SHALL clean up the created task.

#### Scenario: Add task and verify via API
- **WHEN** `todoist_add_task(content="...", project_id=test_project_id)` is called
- **THEN** the result contains "Task created" and a task ID
- **THEN** the task is retrievable via `api_client.get_task()` with matching content

### Requirement: Integration test for todoist_update_task
The system SHALL include a test that calls `todoist_update_task` to modify a task's content, verifies the success message, and confirms the change via a separate API client call.

#### Scenario: Update task content and verify
- **WHEN** `todoist_update_task(task_id=..., content="Updated content")` is called
- **THEN** the result contains "updated successfully"
- **THEN** `api_client.get_task()` returns the task with the updated content

### Requirement: Integration test for todoist_complete_task
The system SHALL include a test that calls `todoist_complete_task` on a known task and verifies the success message.

#### Scenario: Complete a task
- **WHEN** `todoist_complete_task(task_id=known_task_id)` is called
- **THEN** the result contains "completed successfully"

### Requirement: Integration test for todoist_delete_task
The system SHALL include a test that creates a task, then calls `todoist_delete_task` to remove it, and verifies the success message.

#### Scenario: Delete a task
- **WHEN** `todoist_delete_task(task_id=...)` is called on an existing task
- **THEN** the result contains "deleted successfully"

### Requirement: Integration test for todoist_get_projects
The system SHALL include a test that calls `todoist_get_projects` and verifies the test project appears in the formatted output.

#### Scenario: Get projects includes test project
- **WHEN** `todoist_get_projects()` is called
- **THEN** the result contains the `[TEST]` project name and its ID

### Requirement: Integration test for todoist_get_project
The system SHALL include a test that calls `todoist_get_project` with the test project ID and verifies the formatted detail output.

#### Scenario: Get single project by ID
- **WHEN** `todoist_get_project(project_id=test_project_id)` is called
- **THEN** the result contains the project name, ID, and color/favorite fields

### Requirement: Integration test for todoist_add_project
The system SHALL include a test that calls `todoist_add_project` to create a sub-project, verifies the confirmation message, confirms it exists via API, and cleans it up.

#### Scenario: Add project and verify via API
- **WHEN** `todoist_add_project(name="[TEST] Sub-project", parent_id=test_project_id)` is called
- **THEN** the result contains "Project created" and a project ID
- **THEN** the project is retrievable via `api_client.get_project()` with matching name

### Requirement: Integration test for todoist_update_project
The system SHALL include a test that calls `todoist_update_project` to rename the test project (then restores it), verifies the success message, and confirms the change via API.

#### Scenario: Update project name and verify
- **WHEN** `todoist_update_project(project_id=..., name="[TEST] Updated")` is called
- **THEN** the result contains "updated successfully"
- **THEN** `api_client.get_project()` returns the project with the updated name

### Requirement: Integration test for todoist_delete_project
The system SHALL include a test that creates a temporary project, then calls `todoist_delete_project` to remove it, and verifies the success message.

#### Scenario: Delete a project
- **WHEN** `todoist_delete_project(project_id=...)` is called on a `[TEST]`-prefixed project
- **THEN** the result contains "deleted successfully"

### Requirement: pytest-timeout dependency
The system SHALL add `pytest-timeout` to dev dependencies in `pyproject.toml`. Integration tests SHALL use a 30-second per-test timeout to guard against hung API calls.

#### Scenario: Hung API call is terminated
- **WHEN** an integration test exceeds 30 seconds
- **THEN** pytest-timeout terminates the test and reports a timeout failure
