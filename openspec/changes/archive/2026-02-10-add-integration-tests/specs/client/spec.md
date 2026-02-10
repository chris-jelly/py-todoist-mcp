## MODIFIED Requirements

### Requirement: Token resolution is lazy
The `validate_token()` function SHALL read `TODOIST_API_TOKEN` from `os.environ` at call time, not at module import time. The module SHALL NOT store the token in a module-level constant.

#### Scenario: Token set after module import is recognized
- **WHEN** `todoist_mcp.client` is imported before `TODOIST_API_TOKEN` is set in the environment
- **THEN** a subsequent call to `validate_token()` after setting the env var returns the token value

#### Scenario: Token missing at call time raises RuntimeError
- **WHEN** `validate_token()` is called and `TODOIST_API_TOKEN` is not set in the environment
- **THEN** a `RuntimeError` is raised with a message indicating the token is required

#### Scenario: Existing create_client behavior preserved
- **WHEN** `create_client()` is called with `TODOIST_API_TOKEN` set in the environment
- **THEN** a `TodoistAPI` instance is returned, identical to the previous behavior
