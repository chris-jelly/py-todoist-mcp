## Why

The project has ~18 unit tests covering client, utils, and server modules, but zero tests that validate tool functions against the real Todoist API. Unit tests mock `create_client()`, which verifies internal logic but can't catch SDK contract changes, serialization issues, or API behavior mismatches. Integration tests against a real (personal) Todoist subscription would provide confidence that all 11 MCP tools actually work end-to-end.

## What Changes

- Add integration tests covering all 11 tool functions (6 task tools, 5 project tools), at least one test per tool
- Introduce a `pytest.mark.integration` marker to separate integration tests from unit tests
- Add test fixtures that create/teardown dedicated test projects in Todoist (named with a `[TEST]` prefix for visibility)
- Add a manually-triggered GitHub Actions workflow (`workflow_dispatch`) for running integration tests with the API token stored as a repository secret
- Ensure `pytest` default invocation (no marker) continues to run only fast, mocked unit tests
- Fix `TODOIST_API_TOKEN` being read at module import time in `client.py`, making it a lazy read inside `validate_token()` so the token is always resolved at call time rather than import time

## Capabilities

### New Capabilities
- `integration-testing`: Test infrastructure, fixtures, and integration tests that exercise all MCP tools against the live Todoist API
- `ci-integration-workflow`: GitHub Actions workflow with manual trigger for running integration tests against the real API

### Modified Capabilities
- `client`: Change token resolution from module-level constant to lazy read inside `validate_token()`, so the env var is evaluated at call time rather than import time

## Impact

- **New files**: `tests/integration/` directory with test modules, `conftest.py` with live API fixtures, `.github/workflows/integration-tests.yml`
- **Dependencies**: May need `pytest-timeout` or similar for guarding against hung API calls
- **External systems**: Todoist API (personal subscription) - tests will create and delete projects/tasks
- **Secrets**: `TODOIST_API_TOKEN` GitHub repository secret required for CI workflow
- **Risk**: Test failures mid-suite could leave orphaned test data; cleanup fixtures must be robust
