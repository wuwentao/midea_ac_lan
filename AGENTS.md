# AGENTS.md

Shared guidance for all AI coding agents (Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Gemini CLI, etc.) working in this repository. This is the single source of truth; tool-specific files (`CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`) point here.

## What this is

A Home Assistant custom integration (distributed via HACS) that controls Midea M-Smart appliances over the local network. This repo is a **thin Home Assistant glue layer**; all device protocol, discovery, encryption, and cloud-token logic lives in the external **`midea-lan`** library (imported as `midealan`, pinned in `custom_components/midea_ac_lan/manifest.json` → `requirements`). When device behavior or a new attribute is missing, the fix is often in `midea-lan`, not here.

Integration code lives entirely in `custom_components/midea_ac_lan/`. Minimum Home Assistant: **2024.4.1**; target Python **3.12+**.

## Project family and change routing

Device support commonly spans three repositories. Keep their responsibilities separate and cross-link related issues and PRs:

- [`midea-lua`](https://github.com/wuwentao/midea-lua) archives vendor Lua protocol files used as research sources. It is **not** a runtime dependency. If the required protocol file is absent, obtain it as documented there and submit it before implementing the protocol.
- [`midea-lan`](https://github.com/wuwentao/midea-lan) implements discovery, Cloud access, authentication, encryption, message parsing/encoding, appliance attributes, and LAN commands. Protocol and device-behavior fixes belong there and require tests.
- [`midea_ac_lan`](https://github.com/wuwentao/midea_ac_lan) maps `midealan` attributes to Home Assistant entities, configuration flows, services, translations, and user documentation.

For protocol-backed device work, link the exact `midea-lua` file, the related `midea-lan` issue/PR, and the matching `midea_ac_lan` issue/PR. Use `N/A` with a short explanation only when a layer genuinely does not apply. Do not bump the `midea-lan` requirement in a feature PR; the maintainer updates it after publishing the library release.

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

In Home Assistant OS, the full cache path is `/config/.storage/midea_ac_lan/<device_id>.json`. A backed-up JSON file can be restored by copying it into that directory; adding the appliance then automatically loads the cached configuration and skips the Cloud Token/Key request.

### Cloud and appliance Wi-Fi behavior

`midea_ac_lan` controls appliances over the LAN after setup, but the appliance Wi-Fi hardware is designed to reach a Midea Cloud server after joining Wi-Fi. Blocking Internet access for the appliance may cause its Wi-Fi module to repeatedly reboot and probe until the Cloud is reachable; do not misdiagnose that hardware behavior as a LAN integration requirement.

Keep official App / Cloud names unchanged in every language. Do not translate or normalize these names: `美的美居`, `SmartHome`, `Midea Air`, `NetHome Plus`, `Ariston Clima`, `TSmartLife`, and `Toshiba Iolife`. Current Midea Cloud endpoints accept personal accounts associated with a valid appliance. Preset-account login errors can be ignored because preset accounts contain no appliance and cannot provide its Token/Key; troubleshoot Cloud login with redacted debug logs from the user's own account.

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

The pinned Node version under `default_language_version` in `.pre-commit-config.yaml` keeps Prettier reproducible across platforms. Do not remove or change it without validating the full pre-commit suite on Windows as well as the primary development platform.

## Conventions

- **Commits must follow Conventional Commits** — enforced by commitlint + commitizen on the `commit-msg` hook. Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`. Releases are automated from these messages (see recent `chore(main): midea_ac_lan release vX.Y.Z` commits).
- **Do not commit directly to `main`** — blocked by a pre-commit hook; branch and open a PR.
- **Releasing** bumps `version` in `manifest.json`, which must be valid semver **without a `v` prefix** (HACS 2.0+ rejects `v`-prefixed); enforced by `.github/workflows/release.yml`.
- **Adding a new device type**: add a `0xXX` entry to `MIDEA_DEVICES` in `midea_devices.py`, add a `doc/<TYPE>.md` (+ `_hans` Chinese variant) and a row in `README.md`'s supported-appliances table. Add UI strings to `custom_components/midea_ac_lan/translations/en.json` (and other locales) keyed by `translation_key`. Do **not** bump the `midea-lan` pin in `manifest.json` in the feature PR — the maintainer sets that in a follow-up PR after cutting the library release. The full step-by-step walkthrough is in [`doc/adding-a-new-device.md`](doc/adding-a-new-device.md) (and its `.zh-Hans.md` translation), which uses `0xD9` ([PR #1086](https://github.com/wuwentao/midea_ac_lan/pull/1086)) as its running example and `0x9B` ([PR #1096](https://github.com/wuwentao/midea_ac_lan/pull/1096)) as a second, larger example (61 entities) covering the duplicate-translation-key hazard (`check-json` fails on a duplicate key within a platform section — reuse a shared key or namespace yours, e.g. `x9b_fire_power`), distinct `translation_key`s for a coexisting read sensor + write control, and the bool-not-string requirement for switch/binary_sensor/lock states.
- CI validation: `.github/workflows/linter.yml` (pre-commit) and `validate.yml` (HACS + hassfest).

## Documentation, templates, and security

- Keep English and Simplified Chinese documents aligned when both variants exist. Preserve commands, paths, App / Cloud names, warnings, and behavior across translations.
- Issue forms must collect Home Assistant and integration versions, appliance type/model and redacted SN, exact App / Cloud, reproduction details, expected behavior, and complete redacted debug logs or feature evidence. Keep paired English/Chinese forms structurally equivalent.
- The pull request template must retain cross-repository protocol-source links, testing/hardware evidence, documentation impact, and the security checklist. Use a UTF-8/LF Markdown body file with the applicable `gh` command's `--body-file` option for multiline GitHub text.
- Never commit or publish account credentials, passwords, Tokens, Keys, full device IDs, MAC addresses, private keys, or unredacted logs. Examples must use clearly fictional or masked values.
- Treat `.storage` device JSON as sensitive because it may contain identifiers and authentication material. Documentation may explain backup/restore paths, but repository fixtures and PR attachments must be sanitized.

## Submitting issues and pull requests (AI agents)

Most issues and PRs here are now drafted with an AI agent. The agent MUST drive the submission through the repository templates — not around them. Free-form, AI-generated issue/PR text that skips the template is the single most common reason reports are incomplete and get closed or stalled. Follow these rules:

- **Use the repository template as the outline, verbatim.** For issues, open one of the forms in `.github/ISSUE_TEMPLATE/` (bug or enhancement, in the submitter's language) and fill every required field. For PRs, start from `.github/pull_request_template.md` and keep every heading and checklist item. Do not delete, rename, reorder, or replace sections with your own structure. Extra detail is welcome _after_ the template fields, not instead of them.
- **Fill every field; gather what is missing before asking.** For each field, first obtain the value yourself where possible — Home Assistant and integration versions, `midea_devices.py`, translations, `doc/`, the debug log the submitter attached. Only when a value genuinely cannot be obtained by the agent — device SN, a redacted debug log, an official-app screenshot — explicitly ask the submitter for it. Never silently drop a field or invent a value.
- **`N/A` must carry a reason.** Use `N/A` only when a section truly does not apply, and add a short phrase explaining why (e.g. "N/A — HA-only entity rename, no protocol change"). An unexplained `N/A` or a blank field is treated as incomplete.
- **Lua protocol source (checklist).** When the change relies on a device protocol:
  1. Check [`wuwentao/midea-lua`](https://github.com/wuwentao/midea-lua) for the exact protocol file. If it already exists, link that file directly.
  2. If it is missing, guide the submitter to download it as documented in the `midea-lua` README, format it with StyLua (or the formatter that repo's README specifies), and open a `midea-lua` PR _first_. Link that PR rather than pasting raw Lua here.
  3. If no Lua protocol applies, use `N/A` with a one-line reason.
- **Route the change to the right layer and cross-link.** Protocol and device-behavior fixes usually belong in [`midea-lan`](https://github.com/wuwentao/midea-lan), not here (see "Project family and change routing" above). Link the related `midea-lan` issue/PR, the `midea-lua` source, and the matching `midea_ac_lan` issue/PR so the three-repo change set stays traceable.
- **Do not bump the `midea-lan` pin in `manifest.json` in a feature PR.** If you need to test against unreleased library work, mark the PR as a **draft** and temporarily point the `manifest.json` `requirements` entry at the `midea-lan` test branch/commit (e.g. `"midea-lan @ git+https://github.com/<owner>/midea-lan.git@<ref>"`). Before marking the PR ready for review, remove that change and restore the released pin — the maintainer syncs the real pin to `midea_ac_lan` in a follow-up PR after the library release.
- **Redact secrets.** Never paste account credentials, tokens, keys, full device IDs, MAC addresses, or unredacted logs / `.storage` JSON. Mask them.

### Keep code consistent with what exists

When implementing a fix or feature, match the approach already in the codebase; do not invent parallel styles:

- **Prefer the registry-driven path.** Adding an attribute/entity is usually a row in `MIDEA_DEVICES` (`midea_devices.py`) plus translations — you normally do not touch platform files. Follow the identical `async_setup_entry` pattern the platform files already share, and the walkthrough in `doc/adding-a-new-device.md`.
- **Avoid adding new files or new naming conventions** unless necessary. If a new file, platform, or pattern is genuinely required, say so in the PR and explain the reason and the benefit, so reviewers can weigh it against consistency.
- **Comment the key and divergent parts.** Where logic is non-obvious, differs from sibling device entries, or encodes a protocol detail, add a short English comment and cite the referenced Lua field name / attribute. This is what later edits rely on to avoid regressions or mis-edits. Keep English and Simplified Chinese docs/translations aligned.

Reviewed and updated by OpenAI Codex (GPT-5).
