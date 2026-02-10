## Context

The project has 11 MCP tool functions (6 task, 5 project) that are thin wrappers around `todoist-api-python`. Existing unit tests mock `create_client()` to test internal formatting logic, but nothing validates that the tools work against the real Todoist API. The sole maintainer has a personal Todoist subscription available for testing.

Additionally, `TODOIST_API_TOKEN` is currently read at module import time in `client.py` (line 8) as a module-level constant. This is problematic: if anything imports `todoist_mcp.client` before the env var is set, the token is permanently `None` for that process. This needs to be fixed as a prerequisite for reliable integration testing.

## Goals / Non-Goals

**Goals:**
- Validate all 11 tool functions work end-to-end against the live Todoist API
- Isolate integration tests so they never run accidentally during normal development
- Provide a clean test lifecycle: create test data, exercise tools, tear down completely
- Enable manual CI execution via GitHub Actions `workflow_dispatch`
- Fix token resolution to be lazy (read at call time, not import time)

**Non-Goals:**
- Achieving high coverage of edge cases (that's what unit tests are for)
- Testing rate limiting or error recovery scenarios against the live API
- Automated CI runs on push/PR (explicitly avoided to protect personal subscription)
- Testing the MCP protocol layer itself (only testing tool functions directly)

## Decisions

### 1. Test isolation: `pytest.mark.integration` marker with `addopts` exclusion

Integration tests are marked with `@pytest.mark.integration` and excluded from default runs via `addopts = "-m 'not integration'"` in `pyproject.toml`. To run them explicitly:

```bash
pytest -m integration
```

**Why over separate pytest config file**: Simpler, single config source. The marker approach is standard pytest convention and well-understood. No risk of config drift between two files.

**Alternative considered**: A separate `pytest-integration.ini` — rejected because it duplicates config and requires remembering a different invocation (`pytest -c pytest-integration.ini`).

### 2. Test directory: `tests/integration/` with its own `conftest.py`

Integration tests live in `tests/integration/` with a dedicated `conftest.py` that:
- Validates `TODOIST_API_TOKEN` is a real token (not the fake `test-token-12345`)
- Provides session-scoped fixtures for test project creation/teardown
- Does NOT use the autouse `env_with_token` fixture from the root conftest (the root conftest's autouse fixture won't affect integration tests because we'll use a `conftest.py` in `tests/integration/` that takes precedence for that directory)

**Why session-scoped project fixtures**: Creating/deleting a Todoist project per test is slow and wasteful. A single test project created at session start and torn down at session end minimizes API calls. Tasks within the project are created/cleaned per test.

**Alternative considered**: Module-scoped fixtures — rejected because session scope is sufficient and simpler. All integration tests can share one `[TEST]` project.

### 3. Test project naming: `[TEST] Integration - {timestamp}`

Test projects use the pattern `[TEST] Integration - {timestamp}` (e.g., `[TEST] Integration - 20260209T153000`). This provides:
- Visual identification in the Todoist UI (`[TEST]` prefix)
- Uniqueness across parallel runs (timestamp)
- Easy manual cleanup if teardown fails (search for `[TEST]`)

### 4. Fixture strategy: session project, function-scoped tasks

```
Session scope:  test_project  →  creates [TEST] project, yields project_id, deletes on teardown
Function scope: test_task     →  creates a task in test_project, yields task data, deletes on teardown
Function scope: api_client    →  yields a real TodoistAPI client for direct verification
```

The `test_task` fixture provides a fresh task for each test that needs one (get_task, update_task, complete_task, delete_task). Tests for `add_task` create their own and clean up.

Each fixture uses `try/finally` for teardown to ensure cleanup runs even on assertion failures.

### 5. Call tool functions directly, not through MCP protocol

Tests import and call the tool functions directly (e.g., `todoist_add_task(content="test")`), not through the MCP server. This tests the actual API integration without introducing MCP protocol complexity.

**Why**: The goal is validating Todoist API interaction, not MCP routing. MCP routing is a concern for a separate test layer. Direct calls are simpler, faster, and easier to debug.

### 6. Assertion strategy: verify via separate API client

After calling a tool function, assertions verify the result by making a separate API call using the `api_client` fixture. This confirms the tool actually affected Todoist state, not just returned a plausible string.

Example: After `todoist_add_task(content="Test")`, use `api_client.get_task(task_id)` to verify the task exists and has the correct content.

### 7. CI workflow: `workflow_dispatch` only

The GitHub Actions workflow uses only `workflow_dispatch` trigger with the token stored as a repository secret (`TODOIST_API_TOKEN`). No automated triggers.

The workflow:
1. Checks out code
2. Sets up Python + uv
3. Installs dependencies
4. Runs `pytest -m integration --timeout=30`
5. Reports results

### 9. Lazy token resolution in `client.py`

Remove the module-level `TODOIST_API_TOKEN` constant. Instead, read `os.environ.get("TODOIST_API_TOKEN")` inside `validate_token()` at call time.

Before:
```python
TODOIST_API_TOKEN: Final[str | None] = os.environ.get("TODOIST_API_TOKEN")

def validate_token() -> str:
    if not TODOIST_API_TOKEN:
        raise RuntimeError(...)
    return TODOIST_API_TOKEN
```

After:
```python
def validate_token() -> str:
    token = os.environ.get("TODOIST_API_TOKEN")
    if not token:
        raise RuntimeError(...)
    return token
```

**Why**: The module-level read means the token value is frozen at import time. This causes subtle bugs: test fixtures that set the env var after import have no effect, and integration tests would need the token in the environment before any `todoist_mcp` module is imported. Lazy resolution eliminates this entire class of problems.

**Impact on existing tests**: The root conftest's `env_with_token` fixture will now work correctly — it sets the env var, and `validate_token()` reads it at call time. No test changes needed.

**Alternative considered**: Keep the constant but make it non-Final and add a `reset_token()` function — rejected as unnecessarily complex. There's no performance reason to cache an env var read.

### 10. Dependencies: add `pytest-timeout`

Add `pytest-timeout` to dev dependencies. Each integration test gets a 30-second timeout to guard against hung API calls. This prevents a single broken test from blocking the entire suite indefinitely.

## Risks / Trade-offs

**[Orphaned test data]** → Mitigation: `try/finally` teardown in fixtures. `[TEST]` prefix makes manual cleanup easy. Could add a standalone cleanup script that deletes all `[TEST]`-prefixed projects.

**[Rate limiting]** → Mitigation: Session-scoped project reduces API calls. Tests run sequentially (not parallel). 11 tests with ~3 calls each = ~33 API calls total, well within Todoist's limits.

**[Token resolution change affects all callers]** → Mitigation: The behavioral change is minimal — `validate_token()` still returns the same value, just reads it lazily. Existing unit tests pass without modification because the root conftest sets the env var before any tool function calls `validate_token()`.

**[Flaky tests from network/API issues]** → Mitigation: `pytest-timeout` prevents hangs. Tests are simple (one operation + verify). Retry logic is explicitly a non-goal — flaky failures are acceptable for a manual-trigger workflow.

**[Personal subscription data exposure]** → Mitigation: Tests operate exclusively within `[TEST]`-prefixed projects. No tests read or modify existing user data. Delete operations only target resources created during the test session.
