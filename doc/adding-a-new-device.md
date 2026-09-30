# Adding a New Device to the Home Assistant Integration

> [中文版 / Chinese version](./adding-a-new-device.zh-Hans.md)

This guide is the end-to-end recipe for exposing a new Midea appliance type in the
`midea_ac_lan` Home Assistant integration. It is the **HA-integration companion**
to the protocol-library guide in the `midea-lan` repo
([Adding a New Device Type](https://github.com/wuwentao/midea-lan/blob/main/docs/adding-a-new-device.md)):
that guide covers decoding the LAN protocol and adding a `devices/<type>/` package
to the `midealan` library; this guide covers turning those device attributes into
Home Assistant entities.

It is written for both human contributors and AI coding agents, using the `0xD9`
washer/dryer combo ([PR #1086](https://github.com/wuwentao/midea_ac_lan/pull/1086),
paired with `midea-lan` [PR #175](https://github.com/wuwentao/midea-lan/pull/175))
as the worked example.

## Prerequisite: the library must support the device first

`midea_ac_lan` is a **thin Home Assistant glue layer**. All protocol, discovery,
encryption, and cloud-token logic lives in the external `midea-lan` library
(imported as `midealan`). Before you can expose a device here, the library must
already:

- have a `midealan/devices/<type>/` package with a `DeviceAttributes(StrEnum)`, and
- be published to PyPI (or pinned to a compatible version).

If an attribute you need does not exist, the fix is in `midea-lan`, not here. See
the library guide linked above. Once the library is ready, come back and follow the
steps below.

## Contents

1. [How the integration is wired](#1-how-the-integration-is-wired)
2. [Step 1 — Bump the `midea-lan` dependency](#2-step-1--bump-the-midea-lan-dependency)
3. [Step 2 — Register the device in `midea_devices.py`](#3-step-2--register-the-device-in-midea_devicespy)
4. [Step 3 — Choose the platform, `device_class`, and `unit` per attribute](#4-step-3--choose-the-platform-device_class-and-unit-per-attribute)
5. [Step 4 — Add `translation_key`s and translation files](#5-step-4--add-translation_keys-and-translation-files)
6. [Step 5 — Write the device docs (en + zh-Hans)](#6-step-5--write-the-device-docs-en--zh-hans)
7. [Step 6 — Update the README appliance table](#7-step-6--update-the-readme-appliance-table)
8. [Step 7 — Lint and validate](#8-step-7--lint-and-validate)
9. [Step 8 — Submit the PR](#9-step-8--submit-the-pr)
10. [Checklist](#10-checklist)

---

## 1. How the integration is wired

The whole integration is **data-driven from one table**. You almost never write
platform code for a new device — you add rows to a registry and the generic
platform files build the entities.

- **`custom_components/midea_ac_lan/midea_devices.py`** — the registry
  `MIDEA_DEVICES: dict[int, ...]` maps a device-type hex code (`0xD9`, `0xAC`, …)
  to `{"name": ..., "entities": {...}}`. Each row in `entities` maps one
  `DeviceAttributes` member (imported from `midealan.devices.<type>`) to a config
  dict describing which HA platform renders it and its metadata. **This is the
  center of everything — adding a device is mostly editing this file.**
- **Platform files** — `sensor.py`, `binary_sensor.py`, `switch.py`, `select.py`,
  `number.py`, `lock.py`, `button.py`, `time.py`, and the complex control
  platforms `climate.py`, `fan.py`, `light.py`, `water_heater.py`,
  `humidifier.py`. Each `async_setup_entry` iterates
  `MIDEA_DEVICES[device.device_type]["entities"]` and creates an entity for every
  row whose `config["type"]` matches that platform.
  - **Extra entities** (sensor/switch/…): only created if the user opted in via
    the options flow (`entity_key in options.get(CONF_SENSORS/CONF_SWITCHES, [])`).
  - **Main control entities** (climate/fan/light/water_heater/humidifier): created
    when `config.get("default")` is true, regardless of opt-in.
- **`custom_components/midea_ac_lan/midea_entity.py`** — `MideaEntity` base class.
  It reads the row's config, wires `device.register_update(self.update_state)` for
  local-push updates, and implements the entity-name precedence:
  `translation_key` → explicit `name` → `device_class` → device name.
- **`custom_components/midea_ac_lan/translations/<lang>.json`** — UI strings keyed
  by `translation_key`.

Simple platforms (switch, sensor, select, number, …) are fully generic and
data-driven — a new sensor/switch needs **no** platform-file change. Complex
platforms (`climate.py`, `water_heater.py`, `fan.py`) contain per-device-type
subclasses (e.g. `MideaACClimate`, `MideaC3Climate`) selected by
`device.device_type`; a new device that needs a main control entity of those types
also needs a subclass there.

Reference: the Home Assistant developer docs on
[entities](https://developers.home-assistant.io/docs/core/entity),
[integration file structure](https://developers.home-assistant.io/docs/creating_integration_file_structure),
and
[entity translations](https://developers.home-assistant.io/docs/internationalization/core).

---

## 2. Step 1 — Bump the `midea-lan` dependency

The integration pins the library version in
`custom_components/midea_ac_lan/manifest.json`:

```json
"requirements": ["midea-lan==2026.9.2"]
```

Bump this to the first `midea-lan` release that contains your new
`devices/<type>/` package, so `from midealan.devices.<type> import DeviceAttributes`
resolves at runtime for users. (During local development against an unreleased
library you may hit a pinned-version import error — that is expected until the
library release lands; do not work around it by unpinning in the committed
manifest.)

---

## 3. Step 2 — Register the device in `midea_devices.py`

### 3.1 Import the attributes enum

Add an import near the other `from midealan.devices.<type> import ...` lines,
alphabetically:

```python
from midealan.devices.d9 import DeviceAttributes as D9Attributes
```

If the device also exposes enums/maps the integration needs (e.g. work-mode maps
used by a select), import those too — see how `bf` imports
`WORK_MODE_MAP as BF_WORK_MODE_MAP` and `FirePower as BFFirePower`.

### 3.2 Add the `0xXX` entry

Insert a new key in `MIDEA_DEVICES`, kept in hex order. The entry has a `name`
(the human-readable appliance name shown in the device registry) and an `entities`
map:

```python
0xD9: {
    "name": "Washer Dryer Combo",
    "entities": {
        # main control entity (created without opt-in) — omit for a
        # sensor/switch-only device
        # "climate": {"type": Platform.CLIMATE, "default": True},

        # a switch (extra entity — user opts in)
        D9Attributes.db_power: {
            "type": Platform.SWITCH,
            "translation_key": "db_power",
            "name": "Washer Power",
            "icon": "mdi:power",
        },
        # a sensor with an enumerated/text state
        D9Attributes.db_running_status: {
            "type": Platform.SENSOR,
            "translation_key": "db_running_status",
            "name": "Washer Running Status",
            "icon": "mdi:washing-machine",
        },
        # a numeric sensor with a unit + device_class + state_class
        D9Attributes.db_remain_time: {
            "type": Platform.SENSOR,
            "translation_key": "db_remain_time",
            "name": "Washer Remaining Time",
            "icon": "mdi:progress-clock",
            "unit": UnitOfTime.MINUTES,
            "state_class": SensorStateClass.MEASUREMENT,
        },
    },
},
```

The config-dict keys the integration understands:

| Key                               | Applies to           | Meaning                                                                  |
| --------------------------------- | -------------------- | ------------------------------------------------------------------------ |
| `type`                            | all                  | The HA `Platform.*` that renders this attribute (required).              |
| `translation_key`                 | all                  | Key into `translations/<lang>.json` for the localized name (see §5).     |
| `name`                            | all                  | English fallback name if no translation is found.                        |
| `icon`                            | all                  | `mdi:*` icon.                                                            |
| `default`                         | main controls        | `True` = created without user opt-in (climate/fan/light/…).              |
| `device_class`                    | sensor/binary/number | HA device class (drives icon, unit validation, UI formatting).           |
| `unit`                            | sensor/number        | Unit of measurement (use the `UnitOf*` constants).                       |
| `state_class`                     | sensor               | `MEASUREMENT` / `TOTAL` / `TOTAL_INCREASING` for statistics.             |
| `min` / `max` / `step`            | number               | Numeric bounds for a `Platform.NUMBER` entity.                           |
| `options`                         | select               | Name of the device property that lists the selectable options.           |
| `entity_category`                 | any                  | `EntityCategory.CONFIG` / `DIAGNOSTIC` to group away from main controls. |
| `entity_registry_enabled_default` | any                  | `False` to hide a noisy/raw entity by default (user can enable).         |

> Tip: for a device with independent sub-units (D9's washer/dryer), the library
> uses prefixed attribute names (`db_*`, `dc_*`). Reuse those same names as the
> `translation_key` so nothing has to be renamed here — this is why the library
> guide insists on clean lowercase `snake_case` attribute names.

---

## 4. Step 3 — Choose the platform, `device_class`, and `unit` per attribute

For each `DeviceAttributes` member, decide how it should surface in HA. Match the
attribute's data type to a platform:

| Attribute nature                      | Platform                                          | Notes                                             |
| ------------------------------------- | ------------------------------------------------- | ------------------------------------------------- |
| Read-only boolean (running, alarm)    | `Platform.BINARY_SENSOR`                          | Pick a `BinarySensorDeviceClass` (RUNNING, etc.). |
| Read-only number (temp, time, energy) | `Platform.SENSOR`                                 | Add `device_class` + `unit` + `state_class`.      |
| Read-only text/enum (status, program) | `Platform.SENSOR`                                 | No unit; use an icon.                             |
| Writable boolean                      | `Platform.SWITCH`                                 | on/off control.                                   |
| Writable choice from a fixed set      | `Platform.SELECT`                                 | `options` points at the device's option list.     |
| Writable number in a range            | `Platform.NUMBER`                                 | Add `min` / `max` / `step` (+ `unit`).            |
| Momentary action                      | `Platform.BUTTON`                                 | e.g. start/stop a cycle.                          |
| A time-of-day setting                 | `Platform.TIME`                                   | e.g. appointment time.                            |
| The device's primary control          | climate / fan / light / water_heater / humidifier | Set `"default": True`; may need a subclass.       |

Pick `device_class` and `unit` from the Home Assistant constants — do not invent
strings:

- **Sensor** device classes and their required units:
  [SensorDeviceClass](https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes).
  Examples used in this repo: `SensorDeviceClass.TEMPERATURE` + `UnitOfTemperature.CELSIUS`,
  `SensorDeviceClass.POWER` + `UnitOfPower.WATT`, `SensorDeviceClass.ENERGY` +
  `UnitOfEnergy.KILO_WATT_HOUR`.
- **`state_class`**: use `SensorStateClass.MEASUREMENT` for instantaneous readings,
  `SensorStateClass.TOTAL_INCREASING` for cumulative counters (water/energy
  consumption) so HA's statistics and the Energy dashboard work.
- **Binary sensor** device classes:
  [BinarySensorDeviceClass](https://developers.home-assistant.io/docs/core/entity/binary-sensor/#available-device-classes)
  (e.g. `RUNNING`, `DOOR`, `PROBLEM`).
- **Units**: always use the `UnitOf*` enums from `homeassistant.const`
  (`UnitOfTime`, `UnitOfTemperature`, `UnitOfPower`, `UnitOfEnergy`, `UnitOfVolume`,
  `PERCENTAGE`, …). This repo already branches on the HA version for units that
  were renamed across HA releases (see the `UnitOfDensity`/`UnitOfRatio` block at
  the top of `midea_devices.py`) — follow that pattern if you need a very new unit.

When a `device_class` fully implies the name (e.g. `temperature` → "Temperature"),
you can omit both `translation_key` and `name` and let HA generate the label; but
for clarity and full localization, prefer giving a `translation_key`.

---

## 5. Step 4 — Add `translation_key`s and translation files

Home Assistant localizes entity names via `translation_key`. `MideaEntity` sets
`self._attr_translation_key = config.get("translation_key")` and
`has_entity_name = True`; HA then looks up the string in
`translations/<lang>.json` and falls back to `name` / `device_class` if missing
(see the precedence comment block in `midea_entity.py`).

### 5.1 Where the keys live

Each translation file groups keys **by platform** under `entity`:

```json
{
  "entity": {
    "sensor": {
      "db_running_status": { "name": "Washer Running Status" },
      "db_remain_time": { "name": "Washer Remaining Time" }
    },
    "switch": {
      "db_power": { "name": "Washer Power" }
    }
  }
}
```

The key under the platform is exactly the `translation_key` from
`midea_devices.py`. For a `select` (or any entity with translatable **states**),
add a `state` map too:

```json
"select": {
  "db_program": {
    "name": "Washer Program",
    "state": { "cotton": "Cotton", "quick": "Quick Wash", "wool": "Wool" }
  }
}
```

State keys must be lowercase `snake_case` and match the exact string the device
reports (a recent fix, #1089, normalized wind-angle state keys to underscores —
mismatched casing/spacing breaks the lookup).

### 5.2 Which files to update

At minimum add the keys to **`en.json`** (English, the fallback) and
**`zh-Hans.json`** (Simplified Chinese). The repo also ships `de`, `es`, `fr`,
`hu`, `it`, `ru`, `sk`. Add the same keys to every file you can translate; for
locales you can't, English will fall back automatically, but keeping the key
present (even if English text) avoids gaps. Preserve each file's existing
formatting — `prettier` runs in pre-commit and will reformat, so match the
surrounding 2-space indentation and don't reflow unrelated entries.

### 5.3 Icons (optional)

Static per-entity icons go in the `icon` config key in `midea_devices.py`.
State-dependent icons (different icon per state value) go in `icons.json` under
`entity.<platform>.<translation_key>`; see the existing `climate_key` example.

---

## 6. Step 5 — Write the device docs (en + zh-Hans)

Every supported device has a `doc/<TYPE>.md` and a `doc/<TYPE>_hans.md`. Model
them on an existing pair such as `doc/E2.md` / `doc/E2_hans.md`. The structure is:

```markdown
# <Device Name>

## Features

- Short bullet list of what the integration supports for this device.

## Customize

- Any per-device `customize` JSON options (protocol version, precision, …).
  Omit this section if the device has none.

## Entities

### Default entity

| EntityID                    | Class   | Description  |
| --------------------------- | ------- | ------------ |
| climate.{DEVICEID}\_climate | climate | Main control |

### Extra entities

| EntityID                          | Class  | Description           |
| --------------------------------- | ------ | --------------------- |
| sensor.{DEVICEID}\_db_remain_time | sensor | Washer Remaining Time |
| switch.{DEVICEID}\_db_power       | switch | Washer Power          |

## Services

### midea_ac_lan.set_attribute

| Name      | Description                    |
| --------- | ------------------------------ |
| device_id | The Appliance code (Device ID) |
| attribute | "db_power"<br />"dc_power"     |
| value     | true or false                  |

(example YAML block)
```

Use the `EntityID` form `<platform>.{DEVICEID}\_<attribute>` exactly (the `\_`
escapes the underscore for Markdown). List every entity you registered in
`midea_devices.py`, and document each writable attribute under the
`set_attribute` service. The `_hans.md` file is the same tables with the
`Features`/`Customize`/`Description` prose translated to Simplified Chinese.

The D9 example (PR #1086) shipped `doc/D9.md` / `doc/D9_hans.md` describing the
`db_*` washer and `dc_*` dryer entities.

---

## 7. Step 6 — Update the README appliance table

Add a row to the **Supported appliances** table (section 4) in both `README.md`
and `README_hans.md`, kept in the table's hex order:

```markdown
| D9 | Washer Dryer Combo | [D9.md](doc/D9.md) |
```

`README_hans.md` links the `_hans` doc:

```markdown
| D9 | 洗烘一体机 | [D9_hans.md](doc/D9_hans.md) |
```

---

## 8. Step 7 — Lint and validate

There is no unit-test suite in this repo; CI enforces linting and the HACS/hassfest
validators. The dev environment is managed by [uv](https://docs.astral.sh/uv/):

```bash
scripts/setup.sh                      # uv sync + install git hooks

uv run pre-commit run --all-files     # ruff, ruff-format, mypy, pylint, codespell,
                                      # commitlint, prettier — everything CI runs
uv run ruff check .
uv run ruff format .
scripts/mypy.sh                       # mypy (NOT `mypy .` directly)
uv run pylint custom_components
```

You can also run Home Assistant locally with your device to smoke-test the
entities:

```bash
scripts/run.sh                        # starts HA with ./config, integration on PYTHONPATH
```

Fix everything `pre-commit` reports before committing — CI (`linter.yml` +
`validate.yml`) blocks merge on failure.

---

## 9. Step 8 — Submit the PR

- **Branch**: never commit to `main` (a pre-commit hook blocks it). Use a feature
  branch, e.g. `feat/d9-washer-dryer-combo`.
- **Conventional Commits**: `feat(d9): add washer/dryer combo support`.
  commitlint/commitizen enforce the format; releases are automated from these
  messages.
- **`manifest.json` version**: leave the release bump to the automated release
  flow — do not hand-edit `version` in a feature PR.
- **PR description**: summarize the device, list the entities, and link the paired
  `midea-lan` library PR/release. State plainly what you verified (lint clean,
  smoke-tested in HA, etc.).
- **CodeRabbit**: the AI reviewer skips draft PRs. To get a review on a draft,
  comment `@coderabbitai review`, then address every finding in-thread.

Reference worked example: the D9 combo — `midea_ac_lan`
[PR #1086](https://github.com/wuwentao/midea_ac_lan/pull/1086), paired with
`midea-lan` [PR #175](https://github.com/wuwentao/midea-lan/pull/175). It added the
`0xD9` registry entry (30 entities across sensor/switch), translation keys in all
locale files, `doc/D9.md` + `doc/D9_hans.md`, and the README rows.

---

## 10. Checklist

- [ ] Library first: `midealan/devices/<type>/` exists and is published; if not,
      finish the [`midea-lan` guide](https://github.com/wuwentao/midea-lan/blob/main/docs/adding-a-new-device.md).
- [ ] Bumped the `midea-lan` pin in `manifest.json` to the release with the device.
- [ ] Imported `DeviceAttributes as <X>Attributes` in `midea_devices.py`.
- [ ] Added the `0xXX` entry with `name` and an `entities` row per attribute.
- [ ] Each row has the right `type` (platform), and sensors/numbers have
      `device_class` / `unit` / `state_class` from HA constants.
- [ ] `translation_key` set on each entity, matching the attribute name.
- [ ] Added the keys to `translations/en.json`, `zh-Hans.json`, and other locales
      (states included for selects).
- [ ] Wrote `doc/<TYPE>.md` and `doc/<TYPE>_hans.md`.
- [ ] Added the appliance row to `README.md` and `README_hans.md` (hex order).
- [ ] `uv run pre-commit run --all-files` passes; optionally smoke-tested with
      `scripts/run.sh`.
- [ ] PR on a feature branch, Conventional Commit title, library PR/release linked,
    CodeRabbit findings resolved.
</content>
