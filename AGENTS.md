# AGENTS.md

Shared guidance for all AI coding agents (Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Gemini CLI, etc.) working in this repository. This is the single source of truth; tool-specific files (`CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`) point here.

## What this is

A Home Assistant custom integration (distributed via HACS) that controls Midea M-Smart appliances over the local network. This repo is a **thin Home Assistant glue layer**; all device protocol, discovery, encryption, and cloud-token logic lives in the external **`midea-lan`** library (imported as `midealan`, pinned in `custom_components/midea_ac_lan/manifest.json` → `requirements`). When device behavior or a new attribute is missing, the fix is often in `midea-lan`, not here.

Integration code lives entirely in `custom_components/midea_ac_lan/`. Minimum Home Assistant: **2024.4.1**; target Python **3.12+**.

## Architecture

### The device registry (`midea_devices.py`) is the center of everything

`MIDEA_DEVICES: dict[int, ...]` maps a device-type hex code (e.g. `0xAC`, `0xA1`) to `{"name": ..., "entities": {...}}`. Each entry in `entities` maps a **device attribute** (a `DeviceAttributes` enum member imported from `midealan.devices.<type>`) to a config dict describing which HA platform represents it and its metadata:

```python
ACAttributes.eco_mode: {
    "type": Platform.SWITCH,        # which HA platform renders this attribute
    "translation_key": "eco_mode",  # UI name via translations/<lang>.json
    "icon": "mdi:leaf",
    "default": True,                # optional: main entity, created without opt-in
}
```

This one table drives every platform. To **add support for a new attribute/entity**, add a row here — you usually do not touch the platform files.

### Platform files follow one identical pattern

`switch.py`, `sensor.py`, `binary_sensor.py`, `select.py`, `number.py`, `lock.py`, `fan.py`, `light.py`, `climate.py`, `water_heater.py`, `humidifier.py` each define `async_setup_entry` that: looks up the device, iterates `MIDEA_DEVICES[device.device_type]["entities"]`, and creates an entity for every row whose `config["type"]` matches that platform.

- **Extra entities** (sensors/switches/etc.): only created if the user opted in — `entity_key in config_entry.options.get(CONF_SENSORS/CONF_SWITCHES, [])`.
- **Main control entities** (climate, fan, light, water_heater, humidifier): created when `config.get("default")` is true, regardless of opt-in.
- Platform groupings live in `const.py`: `EXTRA_SENSOR`, `EXTRA_SWITCH`, `EXTRA_CONTROL`, `ALL_PLATFORM`.

`midea_entity.py` — `MideaEntity` base class shared by all platforms. It reads the entity's config dict from `MIDEA_DEVICES`, wires `device.register_update(self.update_state)` for local-push updates, and implements the entity-name/translation precedence (see the long comment block in that file: `translation_key` → explicit `name` → `device_class` → device name).

Note: simple platforms (switch, sensor, …) are generic and data-driven. Complex platforms (`climate.py`, `water_heater.py`, `fan.py`) contain **per-device-type subclasses** (e.g. `MideaACClimate`, `MideaCCClimate`, `MideaC3Climate`) selected by `device.device_type` in their `async_setup_entry`.

### Lifecycle & data flow (`__init__.py`)

`async_setup` registers two services (`set_attribute`, `send_command`; see `services.yaml`). `async_setup_entry` calls `midealan.devices.device_selector(...)` to build the `MideaDevice`, calls `device.open()` (starts the long-lived TCP connection), and stores it in `hass.data[DOMAIN][DEVICES][device_id]`. Entities read/write via `device.get_attribute()` / `device.set_attribute()`. `update_listener` re-applies options (customize JSON, IP, refresh interval) on config change. `async_migrate_entry` handles config-entry schema migrations (v1→v2 device identifiers).

### Config & options flow (`config_flow.py`)

`MideaLanConfigFlow` handles discovery/manual add and fetching Token+Key from the Midea cloud (`midealan.cloud`); `MideaLanOptionsFlowHandler` handles per-device options (IP, refresh interval, extra sensor/switch selection, customize). Successfully-added V3 devices are cached to `.storage/midea_ac_lan/<device_id>.json` and reloaded on re-add.

### Home Assistant multi-version compatibility

The integration supports a wide HA version range by branching on `(MAJOR_VERSION, MINOR_VERSION)` (imported from `homeassistant.const`). When using newer HA APIs, guard them this way — grep the codebase for `MAJOR_VERSION` for examples.

## Common commands

Dev environment is managed by **[uv](https://docs.astral.sh/uv/)**. Install uv first, then run `scripts/setup.sh`: it runs `uv sync` (creates `.venv`, installs the project + `dev` dependency group, and downloads the Python version pinned in `.python-version` if needed) and installs the pre-commit + commit-msg git hooks.

```bash
scripts/setup.sh        # uv sync + install pre-commit/commit-msg hooks
scripts/run.sh          # run Home Assistant locally with ./config, integration on PYTHONPATH (creates ./config on first run)
```

Linting / checks (all enforced in CI via pre-commit — there is no separate test suite in this repo):

```bash
uv run pre-commit run --all-files   # run everything: ruff, ruff-format, mypy, pylint, codespell, commitlint, prettier
uv run ruff check .                 # lint (config: ruff.toml, lint.select = ALL, target py312)
uv run ruff format .                # format
scripts/mypy.sh                     # mypy (config: mypy.ini) — note: NOT `mypy .` directly
uv run pylint custom_components     # pylint (config: pylintrc)
```

Dependencies (including the per-Python `homeassistant==` pins) live in `pyproject.toml` and are resolved by environment markers; `uv sync` installs the right set for your Python. There are no `requirements-dev-3.1x.txt` files anymore.

## Conventions

- **Commits must follow Conventional Commits** — enforced by commitlint + commitizen on the `commit-msg` hook. Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`. Releases are automated from these messages (see recent `chore(main): midea_ac_lan release vX.Y.Z` commits).
- **Do not commit directly to `main`** — blocked by a pre-commit hook; branch and open a PR.
- **Releasing** bumps `version` in `manifest.json`, which must be valid semver **without a `v` prefix** (HACS 2.0+ rejects `v`-prefixed); enforced by `.github/workflows/release.yml`.
- **Adding a new device type**: bump the `midea-lan` pin in `manifest.json`, add a `0xXX` entry to `MIDEA_DEVICES` in `midea_devices.py`, add a `doc/<TYPE>.md` (+ `_hans` Chinese variant) and a row in `README.md`'s supported-appliances table. Add UI strings to `custom_components/midea_ac_lan/translations/en.json` (and other locales) keyed by `translation_key`.
- CI validation: `.github/workflows/linter.yml` (pre-commit) and `validate.yml` (HACS + hassfest).
