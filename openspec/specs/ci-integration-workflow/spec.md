## ADDED Requirements

### Requirement: Manually-triggered GitHub Actions workflow
The system SHALL provide a GitHub Actions workflow file at `.github/workflows/integration-tests.yml` that runs integration tests only via `workflow_dispatch` trigger. The workflow SHALL NOT have automated triggers (no `push`, `pull_request`, or `schedule`).

#### Scenario: Manual trigger runs integration tests
- **WHEN** a maintainer triggers the workflow via GitHub Actions UI or `gh workflow run`
- **THEN** the workflow executes `pytest -m integration --timeout=30` with the real Todoist API token

#### Scenario: No automated triggers exist
- **WHEN** code is pushed or a pull request is opened
- **THEN** the integration test workflow does NOT run

### Requirement: Workflow uses repository secret for API token
The workflow SHALL read `TODOIST_API_TOKEN` from GitHub repository secrets and set it as an environment variable for the test step. The token SHALL NOT appear in workflow logs.

#### Scenario: Token is available to tests
- **WHEN** the workflow runs with the `TODOIST_API_TOKEN` secret configured
- **THEN** the `pytest` step has `TODOIST_API_TOKEN` set in its environment

#### Scenario: Workflow fails gracefully without secret
- **WHEN** the workflow runs without the `TODOIST_API_TOKEN` secret configured
- **THEN** the test step fails with a clear error about the missing token (not a cryptic import error)

### Requirement: Workflow uses uv for dependency management
The workflow SHALL use `uv` to install Python and project dependencies, consistent with the project's tooling. It SHALL set up the Python version specified in the project configuration.

#### Scenario: Dependencies installed via uv
- **WHEN** the workflow runs
- **THEN** it uses `uv sync --all-extras` (or equivalent) to install dependencies including dev extras

### Requirement: Workflow reports test results
The workflow SHALL report test results in the GitHub Actions summary. Failed tests SHALL be clearly visible in the workflow output.

#### Scenario: Test results visible in Actions UI
- **WHEN** integration tests complete (pass or fail)
- **THEN** individual test results are visible in the GitHub Actions log output
