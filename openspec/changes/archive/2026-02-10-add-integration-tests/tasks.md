## 1. Fix lazy token resolution in client.py

- [x] 1.1 Remove the module-level `TODOIST_API_TOKEN: Final[str | None] = os.environ.get("TODOIST_API_TOKEN")` constant from `src/todoist_mcp/client.py`
- [x] 1.2 Move `os.environ.get("TODOIST_API_TOKEN")` into `validate_token()` so it reads at call time
- [x] 1.3 Remove the unused `Final` import from typing
- [x] 1.4 Run existing unit tests (`pytest`) to confirm no regressions

## 2. Configure pytest marker and dependency

- [x] 2.1 Register the `integration` marker in `pyproject.toml` under `[tool.pytest.ini_options]` with `markers = ["integration: marks tests as integration tests (deselect with '-m \"not integration\"')"]`
- [x] 2.2 Add `addopts = "-m 'not integration'"` to `[tool.pytest.ini_options]` in `pyproject.toml`
- [x] 2.3 Add `pytest-timeout>=2.0` to the `dev` optional dependencies in `pyproject.toml`
- [x] 2.4 Run `uv sync --all-extras` to install the new dependency

## 3. Create integration test infrastructure

- [x] 3.1 Create `tests/integration/__init__.py` (empty)
- [x] 3.2 Create `tests/integration/conftest.py` with:
  - `api_client` fixture (session-scoped): creates a real `TodoistAPI` client from env var
  - `test_project` fixture (session-scoped): creates `[TEST] Integration - {timestamp}` project via API, yields project ID, deletes on teardown with `try/finally`
  - `test_task` fixture (function-scoped): creates a task in the test project, yields task data (id, content), deletes on teardown with `try/finally`
  - Skip-all guard: skip the entire module if `TODOIST_API_TOKEN` is not set or is the fake test token

## 4. Integration tests for task tools

- [x] 4.1 Create `tests/integration/test_task_tools.py` with `pytestmark = pytest.mark.integration`
- [x] 4.2 Implement `test_get_tasks` — call `todoist_get_tasks(project_id=...)`, assert result contains the test task content and ID
- [x] 4.3 Implement `test_get_task` — call `todoist_get_task(task_id=...)`, assert result contains task content, ID, and status
- [x] 4.4 Implement `test_add_task` — call `todoist_add_task(content=..., project_id=...)`, assert "Task created" in result, verify via `api_client.get_task()`, clean up created task
- [x] 4.5 Implement `test_update_task` — call `todoist_update_task(task_id=..., content="Updated")`, assert "updated successfully", verify via `api_client.get_task()`
- [x] 4.6 Implement `test_complete_task` — call `todoist_complete_task(task_id=...)`, assert "completed successfully"
- [x] 4.7 Implement `test_delete_task` — create a temp task, call `todoist_delete_task(task_id=...)`, assert "deleted successfully"

## 5. Integration tests for project tools

- [x] 5.1 Create `tests/integration/test_project_tools.py` with `pytestmark = pytest.mark.integration`
- [x] 5.2 Implement `test_get_projects` — call `todoist_get_projects()`, assert result contains the `[TEST]` project name and ID
- [x] 5.3 Implement `test_get_project` — call `todoist_get_project(project_id=...)`, assert result contains project name, ID, and favorite field
- [x] 5.4 Implement `test_add_project` — call `todoist_add_project(name="[TEST] Sub-project")`, assert "Project created", verify via `api_client.get_project()`, clean up created project
- [x] 5.5 Implement `test_update_project` — call `todoist_update_project(project_id=..., name="[TEST] Updated")`, assert "updated successfully", verify via `api_client.get_project()`, restore original name
- [x] 5.6 Implement `test_delete_project` — create a temp `[TEST]` project, call `todoist_delete_project(project_id=...)`, assert "deleted successfully"

## 6. GitHub Actions workflow

- [x] 6.1 Create `.github/workflows/integration-tests.yml` with `workflow_dispatch` trigger only
- [x] 6.2 Configure the workflow to use `uv` for Python setup and dependency installation
- [x] 6.3 Add the test step: `pytest -m integration --timeout=30` with `TODOIST_API_TOKEN` from `secrets.TODOIST_API_TOKEN`
- [x] 6.4 Verify workflow YAML is valid (e.g., `actionlint` or manual review)

## 7. Validation

- [x] 7.1 Run `pytest` (default) and confirm integration tests are NOT collected
- [ ] 7.2 Run `pytest -m integration` locally with a real `TODOIST_API_TOKEN` and confirm all 11 tests pass
- [x] 7.3 Run `ruff format` and `ruff check` on all changed files
- [x] 7.4 Run `mypy` and fix any type errors in changed files
