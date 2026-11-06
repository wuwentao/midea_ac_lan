# Testing the integration

The integration tests follow Home Assistant's integration testing approach: use
a real `hass` fixture and `MockConfigEntry`, load the entry through
`hass.config_entries.async_setup`, call services through
`hass.services.async_call`, and inspect `hass.states` and the entity/device
registries. Only device connections, LAN discovery, and Cloud requests are
mocked. Tests must never contact real appliances or accounts; pytest blocks
network sockets.

## Local commands

Keep the test environment separate from `.venv`, which contains linting and
development tools:

```sh
UV_PROJECT_ENVIRONMENT=.venv-test312 uv sync --locked --no-default-groups --group test --python 3.12
UV_PROJECT_ENVIRONMENT=.venv-test312 uv run --no-sync pytest
UV_PROJECT_ENVIRONMENT=.venv-test312 uv run --no-sync pytest --cov=custom_components.midea_ac_lan --cov-report=term-missing --cov-report=html --cov-report=xml
```

Open `htmlcov/index.html` to inspect missing lines and branches. Coverage includes
the entire integration, including compatibility branches; production code must
not be excluded just to increase the percentage. `.coveragerc` enforces 100%
line and branch coverage in every supported matrix environment.

## Compatibility matrix

| Python | Home Assistant        | Test group     | Harness                                           |
| ------ | --------------------- | -------------- | ------------------------------------------------- |
| 3.12   | 2024.4.1              | `test`         | `pytest-homeassistant-custom-component==0.13.112` |
| 3.13   | 2024.12.1             | `test`         | `pytest-homeassistant-custom-component==0.13.191` |
| 3.14   | 2026.3.1              | `test`         | `pytest-homeassistant-custom-component==0.13.317` |
| 3.14   | 2026.11.0b4 (preview) | `test-current` | `pytest-homeassistant==2026.11.0b4`               |

Change the environment path and `--python` in the commands above for another
baseline. For the preview, also select `--group test-current`. The official
central harness currently starts with Python 3.14 and HA 2026.11 prereleases;
historical HA releases need the matching extracted harness. Never install both
harness packages together. `tests/ha.py` exposes their shared helpers through a
single import. Update HA and its harness as a pair and run the full matrix.

The groups conflict with `dev` and `run` because historical harnesses also pin
pytest, pydantic, numpy, and lint tools. The unavailable `mypy-dev` prerelease
listed by the oldest harness is excluded; type checking uses `scripts/mypy.sh`
in the development environment.

## New tests

Use `custom_components.midea_ac_lan` in imports and patch targets, matching HA's
loader. Importing the integration under a second package name creates separate
module state and can hide registration and lifecycle failures. Keep small unit
tests for isolated conversions and boundary conditions, but exercise platform
services, config/options flows, updates, setup failures, unload and migrations
through HA's public managers. Use fictional device identifiers and credentials.

The Tests workflow runs every matrix entry, publishes a Markdown coverage
summary, and uploads XML, HTML, Markdown, and JUnit reports. The minimum-version
report is also uploaded to Codecov for the pull-request report and README badge.
The `Coverage gate` check requires every matrix entry to reach 100%. For
non-fork pull requests and pushes, the canonical report upload to Codecov must
also succeed. For pull requests from forks, the upload is best-effort because
upstream OIDC credentials are unavailable, so an upload failure does not fail
the gate; the local 100% gate still applies. Linting remains in the separate
Lint workflow.
