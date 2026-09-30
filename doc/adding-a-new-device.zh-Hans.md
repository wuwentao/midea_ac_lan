# 为 Home Assistant 集成新增一款设备

> [English version / 英文版](./adding-a-new-device.md)

本指南是在 `midea_ac_lan` Home Assistant 集成中暴露一款新美的设备类型的完整流程。
它是协议库指南（位于 `midea-lan` 仓库
[新增设备类型支持指南](https://github.com/wuwentao/midea-lan/blob/main/docs/adding-a-new-device.zh-Hans.md)）的
**HA 集成配套篇**：那篇指南讲的是解析 LAN 协议、为 `midealan` 库新增
`devices/<type>/` 包；本篇讲的是把这些设备属性变成 Home Assistant 实体。

本文同时面向人工贡献者与 AI 编码助手，以 `0xD9` 洗烘一体机
（[PR #1086](https://github.com/wuwentao/midea_ac_lan/pull/1086)，与 `midea-lan`
[PR #175](https://github.com/wuwentao/midea-lan/pull/175) 配套）作为贯穿示例。

## 前置条件：库侧必须先支持该设备

`midea_ac_lan` 是一层**很薄的 Home Assistant 胶水层**。所有协议、发现、加密、
云 token 逻辑都在外部的 `midea-lan` 库（导入名为 `midealan`）里。要在这里暴露一款
设备，库侧必须已经：

- 拥有带 `DeviceAttributes(StrEnum)` 的 `midealan/devices/<type>/` 包；且
- 已发布到 PyPI（或已固定到一个兼容版本）。

如果你需要的某个属性还不存在，那么应当去 `midea-lan` 修，而不是这里。参见上方链接
的库侧指南。库侧就绪后，再回到这里按下述步骤操作。

## 目录

1. [集成是如何串起来的](#1-集成是如何串起来的)
2. [步骤 1 —— 升级 `midea-lan` 依赖](#2-步骤-1--升级-midea-lan-依赖)
3. [步骤 2 —— 在 `midea_devices.py` 中注册设备](#3-步骤-2--在-midea_devicespy-中注册设备)
4. [步骤 3 —— 为每个属性选择 platform、`device_class`、`unit`](#4-步骤-3--为每个属性选择-platformdevice_classunit)
5. [步骤 4 —— 添加 `translation_key` 与翻译文件](#5-步骤-4--添加-translation_key-与翻译文件)
6. [步骤 5 —— 编写设备文档（en + zh-Hans）](#6-步骤-5--编写设备文档en--zh-hans)
7. [步骤 6 —— 更新 README 设备表](#7-步骤-6--更新-readme-设备表)
8. [步骤 7 —— Lint 与校验](#8-步骤-7--lint-与校验)
9. [步骤 8 —— 提交 PR](#9-步骤-8--提交-pr)
10. [检查清单](#10-检查清单)

---

## 1. 集成是如何串起来的

整个集成是**由一张表驱动**的。为新设备你几乎不用写 platform 代码 —— 你只往一个
注册表里加行，通用的 platform 文件就会据此构建实体。

- **`custom_components/midea_ac_lan/midea_devices.py`** —— 注册表
  `MIDEA_DEVICES: dict[int, ...]` 把设备类型十六进制码（`0xD9`、`0xAC`……）映射到
  `{"name": ..., "entities": {...}}`。`entities` 中的每一行把一个
  `DeviceAttributes` 成员（从 `midealan.devices.<type>` 导入）映射到一个配置字典，
  描述由哪个 HA platform 渲染以及其元数据。**这是一切的核心 —— 新增设备主要就是
  编辑这个文件。**
- **Platform 文件** —— `sensor.py`、`binary_sensor.py`、`switch.py`、`select.py`、
  `number.py`、`lock.py`、`button.py`、`time.py`，以及复杂控制类
  `climate.py`、`fan.py`、`light.py`、`water_heater.py`、`humidifier.py`。每个
  `async_setup_entry` 都会遍历 `MIDEA_DEVICES[device.device_type]["entities"]`，
  为每一行 `config["type"]` 匹配该 platform 的项创建实体。
  - **额外实体**（sensor/switch/…）：仅当用户在选项流中勾选时才创建
    （`entity_key in options.get(CONF_SENSORS/CONF_SWITCHES, [])`）。
  - **主控实体**（climate/fan/light/water_heater/humidifier）：当
    `config.get("default")` 为真时创建，无需用户勾选。
- **`custom_components/midea_ac_lan/midea_entity.py`** —— `MideaEntity` 基类。它
  读取该行配置、接线 `device.register_update(self.update_state)` 以进行本地推送
  更新，并实现实体名优先级：`translation_key` → 显式 `name` → `device_class` →
  设备名。
- **`custom_components/midea_ac_lan/translations/<lang>.json`** —— 以
  `translation_key` 为键的 UI 文案。

简单 platform（switch、sensor、select、number……）完全通用、数据驱动 —— 新增一个
sensor/switch **无需**改任何 platform 文件。复杂 platform（`climate.py`、
`water_heater.py`、`fan.py`）含有按设备类型区分的子类（如 `MideaACClimate`、
`MideaC3Climate`），由 `device.device_type` 选择；若新设备需要这些类型的主控
实体，则还需在那里加一个子类。

参考：Home Assistant 开发者文档中的
[实体](https://developers.home-assistant.io/docs/core/entity)、
[集成文件结构](https://developers.home-assistant.io/docs/creating_integration_file_structure)、
[实体翻译](https://developers.home-assistant.io/docs/internationalization/core)。

---

## 2. 步骤 1 —— 升级 `midea-lan` 依赖

集成在 `custom_components/midea_ac_lan/manifest.json` 中固定库版本：

```json
"requirements": ["midea-lan==2026.9.2"]
```

将其升级到第一个包含你新增 `devices/<type>/` 包的 `midea-lan` 发布版本，使得
`from midealan.devices.<type> import DeviceAttributes` 在用户运行时可以解析。
（在本地针对尚未发布的库开发时，你可能会遇到固定版本导入错误 —— 在库发布落地前
这是预期现象；不要通过在提交的 manifest 里取消固定来绕过。）

---

## 3. 步骤 2 —— 在 `midea_devices.py` 中注册设备

### 3.1 导入属性枚举

在其他 `from midealan.devices.<type> import ...` 行附近按字母序添加导入：

```python
from midealan.devices.d9 import DeviceAttributes as D9Attributes
```

若设备还暴露了集成需要的枚举/映射（例如 select 用到的工作模式映射），也一并导入
—— 参考 `bf` 如何导入 `WORK_MODE_MAP as BF_WORK_MODE_MAP` 与 `FirePower as
BFFirePower`。

### 3.2 添加 `0xXX` 条目

在 `MIDEA_DEVICES` 中按十六进制顺序插入新键。条目包含 `name`（设备注册表中显示的
可读设备名）与一个 `entities` 映射：

```python
0xD9: {
    "name": "Washer Dryer Combo",
    "entities": {
        # 主控实体（无需勾选即创建）—— 纯 sensor/switch 设备可省略
        # "climate": {"type": Platform.CLIMATE, "default": True},

        # 一个开关（额外实体 —— 用户勾选）
        D9Attributes.db_power: {
            "type": Platform.SWITCH,
            "translation_key": "db_power",
            "name": "Washer Power",
            "icon": "mdi:power",
        },
        # 一个枚举/文本状态的传感器
        D9Attributes.db_running_status: {
            "type": Platform.SENSOR,
            "translation_key": "db_running_status",
            "name": "Washer Running Status",
            "icon": "mdi:washing-machine",
        },
        # 一个带 unit + device_class + state_class 的数值传感器
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

集成能识别的配置字典键：

| 键                                | 适用于               | 含义                                                       |
| --------------------------------- | -------------------- | ---------------------------------------------------------- |
| `type`                            | 全部                 | 渲染该属性的 HA `Platform.*`（必填）。                     |
| `translation_key`                 | 全部                 | 指向 `translations/<lang>.json` 的本地化名称键（见 §5）。  |
| `name`                            | 全部                 | 未找到翻译时的英文回退名。                                 |
| `icon`                            | 全部                 | `mdi:*` 图标。                                             |
| `default`                         | 主控实体             | `True` = 无需用户勾选即创建（climate/fan/light/…）。       |
| `device_class`                    | sensor/binary/number | HA 设备类别（决定图标、单位校验、UI 格式）。               |
| `unit`                            | sensor/number        | 计量单位（使用 `UnitOf*` 常量）。                          |
| `state_class`                     | sensor               | `MEASUREMENT` / `TOTAL` / `TOTAL_INCREASING`，用于统计。   |
| `min` / `max` / `step`            | number               | `Platform.NUMBER` 实体的数值范围。                         |
| `options`                         | select               | 列出可选项的设备属性名。                                   |
| `entity_category`                 | 任意                 | `EntityCategory.CONFIG` / `DIAGNOSTIC`，从主控中分组出去。 |
| `entity_registry_enabled_default` | 任意                 | `False` 默认隐藏噪声/原始实体（用户可启用）。              |

> 提示：对于有相互独立子单元的设备（D9 的洗衣机/干衣机），库侧用了带前缀的属性名
> （`db_*`、`dc_*`）。在这里直接复用这些名字作为 `translation_key`，就无需任何
> 重命名 —— 这正是库侧指南坚持使用干净的小写 `snake_case` 属性名的原因。

---

## 4. 步骤 3 —— 为每个属性选择 platform、`device_class`、`unit`

针对每个 `DeviceAttributes` 成员，决定它在 HA 中如何呈现。把属性的数据类型匹配到
platform：

| 属性性质                     | Platform                                          | 说明                                             |
| ---------------------------- | ------------------------------------------------- | ------------------------------------------------ |
| 只读布尔（运行、报警）       | `Platform.BINARY_SENSOR`                          | 选一个 `BinarySensorDeviceClass`（RUNNING 等）。 |
| 只读数值（温度、时间、电量） | `Platform.SENSOR`                                 | 加 `device_class` + `unit` + `state_class`。     |
| 只读文本/枚举（状态、程序）  | `Platform.SENSOR`                                 | 无单位；用图标。                                 |
| 可写布尔                     | `Platform.SWITCH`                                 | 开/关控制。                                      |
| 从固定集合中可写选择         | `Platform.SELECT`                                 | `options` 指向设备的选项列表。                   |
| 范围内可写数值               | `Platform.NUMBER`                                 | 加 `min` / `max` / `step`（+ `unit`）。          |
| 瞬时动作                     | `Platform.BUTTON`                                 | 如启动/停止一个循环。                            |
| 一个时刻设置                 | `Platform.TIME`                                   | 如预约时间。                                     |
| 设备的主控                   | climate / fan / light / water_heater / humidifier | 设 `"default": True`；可能需要子类。             |

从 Home Assistant 常量中选取 `device_class` 与 `unit` —— 不要自造字符串：

- **Sensor** 设备类别及其所需单位：
  [SensorDeviceClass](https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes)。
  本仓库用到的例子：`SensorDeviceClass.TEMPERATURE` + `UnitOfTemperature.CELSIUS`、
  `SensorDeviceClass.POWER` + `UnitOfPower.WATT`、`SensorDeviceClass.ENERGY` +
  `UnitOfEnergy.KILO_WATT_HOUR`。
- **`state_class`**：瞬时读数用 `SensorStateClass.MEASUREMENT`，累计计数器（水耗/
  电耗）用 `SensorStateClass.TOTAL_INCREASING`，以便 HA 统计与能源面板正常工作。
- **Binary sensor** 设备类别：
  [BinarySensorDeviceClass](https://developers.home-assistant.io/docs/core/entity/binary-sensor/#available-device-classes)
  （如 `RUNNING`、`DOOR`、`PROBLEM`）。
- **单位**：始终使用 `homeassistant.const` 中的 `UnitOf*` 枚举（`UnitOfTime`、
  `UnitOfTemperature`、`UnitOfPower`、`UnitOfEnergy`、`UnitOfVolume`、
  `PERCENTAGE`……）。对于跨 HA 版本被重命名的单位，本仓库已按 HA 版本分支处理
  （见 `midea_devices.py` 顶部的 `UnitOfDensity`/`UnitOfRatio` 代码块）—— 若需要
  很新的单位，请照此模式处理。

当某个 `device_class` 已完全隐含名称（如 `temperature` → “Temperature”）时，你可
省略 `translation_key` 与 `name`，让 HA 自动生成标签；但为清晰与完整本地化，建议
仍给出 `translation_key`。

---

## 5. 步骤 4 —— 添加 `translation_key` 与翻译文件

Home Assistant 通过 `translation_key` 本地化实体名。`MideaEntity` 会设置
`self._attr_translation_key = config.get("translation_key")` 与
`has_entity_name = True`；随后 HA 在 `translations/<lang>.json` 中查找该字符串，
未找到则回退到 `name` / `device_class`（见 `midea_entity.py` 中的优先级注释块）。

### 5.1 键放在哪里

每个翻译文件在 `entity` 下**按 platform** 分组：

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

platform 下的键，正是 `midea_devices.py` 中的 `translation_key`。对于 `select`
（或任何带可翻译**状态**的实体），还要加一个 `state` 映射：

```json
"select": {
  "db_program": {
    "name": "Washer Program",
    "state": { "cotton": "Cotton", "quick": "Quick Wash", "wool": "Wool" }
  }
}
```

状态键必须是小写 `snake_case`，且与设备上报的确切字符串一致（近期的修复 #1089 把
风向状态键规范为下划线 —— 大小写/空格不匹配会导致查找失败）。

### 5.2 更新哪些文件

至少要把键加入 **`en.json`**（英文，回退用）与 **`zh-Hans.json`**（简体中文）。
仓库还带有 `de`、`es`、`fr`、`hu`、`it`、`ru`、`sk`。你能翻译的语言都加上相同的键；
不能翻译的语言会自动回退到英文，但保留该键（哪怕填英文）可避免出现缺口。请保留
各文件既有格式 —— pre-commit 会跑 `prettier` 并重新格式化，请对齐周围的 2 空格
缩进，且不要重排无关条目。

### 5.3 图标（可选）

静态的按实体图标放在 `midea_devices.py` 的 `icon` 配置键里。依赖状态的图标（不同
状态用不同图标）放在 `icons.json` 的 `entity.<platform>.<translation_key>` 下；
参见既有的 `climate_key` 示例。

---

## 6. 步骤 5 —— 编写设备文档（en + zh-Hans）

每款受支持设备都有一个 `doc/<TYPE>.md` 与一个 `doc/<TYPE>_hans.md`。参照现成的
一对，如 `doc/E2.md` / `doc/E2_hans.md`。结构为：

```markdown
# <设备名>

## 特性

- 简短列出集成对该设备支持了哪些功能。

## 自定义

- 该设备的任何 `customize` JSON 选项（协议版本、精度……）。
  若设备没有则省略本节。

## 实体

### 默认实体

| EntityID                    | Class   | Description |
| --------------------------- | ------- | ----------- |
| climate.{DEVICEID}\_climate | climate | 主控        |

### 额外实体

| EntityID                          | Class  | Description    |
| --------------------------------- | ------ | -------------- |
| sensor.{DEVICEID}\_db_remain_time | sensor | 洗衣机剩余时间 |
| switch.{DEVICEID}\_db_power       | switch | 洗衣机电源     |

## 服务

### midea_ac_lan.set_attribute

| Name      | Description                        |
| --------- | ---------------------------------- |
| device_id | 设备的 Appliance code（Device ID） |
| attribute | "db_power"<br />"dc_power"         |
| value     | true 或 false                      |

（示例 YAML 块）
```

`EntityID` 一律采用 `<platform>.{DEVICEID}\_<attribute>` 的形式（`\_` 是为
Markdown 转义下划线）。把你在 `midea_devices.py` 中注册的每个实体都列出来，并把
每个可写属性记录在 `set_attribute` 服务下。`_hans.md` 文件是同样的表格，只是把
`特性`/`自定义`/`Description` 中的散文译为简体中文。

D9 示例（PR #1086）随附了 `doc/D9.md` / `doc/D9_hans.md`，描述了 `db_*` 洗衣机与
`dc_*` 干衣机实体。

---

## 7. 步骤 6 —— 更新 README 设备表

在 `README.md` 与 `README_hans.md` 的**已支持设备**表（第 4 节）中，按表内十六进制
顺序添加一行：

```markdown
| D9 | Washer Dryer Combo | [D9.md](doc/D9.md) |
```

`README_hans.md` 链接 `_hans` 文档：

```markdown
| D9 | 洗烘一体机 | [D9_hans.md](doc/D9_hans.md) |
```

---

## 8. 步骤 7 —— Lint 与校验

本仓库没有单元测试套件；CI 强制执行 lint 与 HACS/hassfest 校验器。开发环境由
[uv](https://docs.astral.sh/uv/) 管理：

```bash
scripts/setup.sh                      # uv sync + 安装 git 钩子

uv run pre-commit run --all-files     # ruff、ruff-format、mypy、pylint、codespell、
                                      # commitlint、prettier —— CI 跑的全部
uv run ruff check .
uv run ruff format .
scripts/mypy.sh                       # mypy（不要直接 `mypy .`）
uv run pylint custom_components
```

你也可以带上你的设备在本地运行 Home Assistant 来冒烟测试实体：

```bash
scripts/run.sh                        # 用 ./config 启动 HA，集成在 PYTHONPATH 上
```

提交前修复 `pre-commit` 报告的所有问题 —— CI（`linter.yml` + `validate.yml`）会在
失败时阻止合并。

---

## 9. 步骤 8 —— 提交 PR

- **分支**：绝不直接提交到 `main`（有 pre-commit 钩子拦截）。使用特性分支，如
  `feat/d9-washer-dryer-combo`。
- **Conventional Commits**：`feat(d9): add washer/dryer combo support`。
  commitlint/commitizen 强制格式；发布由这些提交消息自动完成。
- **`manifest.json` 版本**：版本升级交给自动发布流程 —— 不要在特性 PR 中手改
  `version`。
- **PR 描述**：概述该设备、列出实体，并链接配套的 `midea-lan` 库 PR/发布。如实
  陈述你验证了什么（lint 通过、在 HA 中冒烟测试等）。
- **CodeRabbit**：该 AI 评审会跳过草稿 PR。要让草稿获得评审，评论
  `@coderabbitai review`，随后在对应线程中逐条处理所有意见。

可参照的范例：D9 一体机 —— `midea_ac_lan`
[PR #1086](https://github.com/wuwentao/midea_ac_lan/pull/1086)，与 `midea-lan`
[PR #175](https://github.com/wuwentao/midea-lan/pull/175) 配套。它新增了 `0xD9`
注册条目（跨 sensor/switch 的 30 个实体）、所有语言文件中的翻译键、
`doc/D9.md` + `doc/D9_hans.md`，以及 README 行。

---

## 10. 检查清单

- [ ] 库先行：`midealan/devices/<type>/` 已存在且已发布；若未，先完成
      [`midea-lan` 指南](https://github.com/wuwentao/midea-lan/blob/main/docs/adding-a-new-device.zh-Hans.md)。
- [ ] 已把 `manifest.json` 中的 `midea-lan` 固定版本升级到含该设备的发布版本。
- [ ] 已在 `midea_devices.py` 中导入 `DeviceAttributes as <X>Attributes`。
- [ ] 已添加含 `name` 与逐属性 `entities` 行的 `0xXX` 条目。
- [ ] 每行都有正确的 `type`（platform），sensor/number 带来自 HA 常量的
      `device_class` / `unit` / `state_class`。
- [ ] 每个实体都设了 `translation_key`，与属性名一致。
- [ ] 已把键加入 `translations/en.json`、`zh-Hans.json` 及其他语言（select 含
      states）。
- [ ] 已编写 `doc/<TYPE>.md` 与 `doc/<TYPE>_hans.md`。
- [ ] 已把设备行加入 `README.md` 与 `README_hans.md`（十六进制顺序）。
- [ ] `uv run pre-commit run --all-files` 通过；可选地用 `scripts/run.sh` 冒烟
      测试。
- [ ] 在特性分支上提 PR，Conventional Commit 标题，链接库 PR/发布，处理完
    CodeRabbit 意见。
</content>
