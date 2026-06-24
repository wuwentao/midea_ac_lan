# 家用空调

## 特性

- 支持目标温度设定
- 支持运行模式设定
- 支持风扇模式设定
- 支持摆风模式设定
- 支持预设模式设定
- 支持出风角度设定
- 支持内置新风系统

### 支持的模式

- 舒适模式
- 节能模式
- 强力模式

## 自定义

- 设置温度调整步长(默认为0.5).

```json
{ "temperature_step": 1 }
```

- 能力（模式 / 摆风 / 预设）

  运行模式、摆风和预设会根据设备的 B5 能力上报自动识别（例如仅制冷的移动空调
  只显示 `cool`/`dry`/`fan_only`，无摆风、无预设）。

  部分能力无法推断（旧版库，或协议本身不声明的功能，如 `comfort`/`sleep` 预设），
  可通过自定义覆盖（请通过美的 App 或遥控器确认真实取值）：

```json
{
  "swing": false,
  "hvac_modes": ["off", "cool", "dry", "fan_only"],
  "preset_modes": ["none"]
}
```

  - `swing`（布尔）：强制开启/关闭摆风控制。
  - `hvac_modes`（列表）：限制显示的模式，`off` 始终保留。可选值：`off`、`auto`、`cool`、`dry`、`heat`、`fan_only`。
  - `preset_modes`（列表）：限制预设，`none` 始终保留；用 `["none"]` 可完全移除预设控制。可选值：`none`、`comfort`、`eco`、`boost`、`sleep`、`away`。

  优先级为 自定义 > B5 能力 > 默认值。所有键均为可选；省略则使用自动识别的集合。

- 空调功耗分析方法(默认为1)

  我找到了三种不同的办法去分析空调功耗数据, 但我无从得知哪种适合你的空调设备
  如果空调的功耗数据看起来不正确, 换用其它方法试试看
  可选值有(1/2/3)

```json
{ "power_analysis_method": 2 }
```

## 生成实体

### 默认生成实体

| 实体ID                      | 类型    | 描述       |
| --------------------------- | ------- | ---------- |
| climate.{DEVICEID}\_climate | climate | 恒温器实体 |

### 额外生成实体

| EntityID                                      | 类型          | 名称                       | 描述             |
| --------------------------------------------- | ------------- | -------------------------- | ---------------- |
| sensor.{DEVICEID}\_full_dust                  | binary_sensor | Full of Dust               | 尘满             |
| sensor.{DEVICEID}\_indoor_humidity            | sensor        | Indoor humidity            | 湿度             |
| sensor.{DEVICEID}\_indoor_temperature         | sensor        | Indoor Temperature         | 室内温度         |
| sensor.{DEVICEID}\_outdoor_temperature        | sensor        | Outdoor Temperature        | 室外机温度       |
| sensor.{DEVICEID}\_total_energy_consumption   | sensor        | Total Energy Consumption   | 总能耗           |
| sensor.{DEVICEID}\_current_energy_consumption | sensor        | Current Energy Consumption | 当前能耗         |
| sensor.{DEVICEID}\_realtime_power             | sensor        | Realtime Power             | 实时功率         |
| fan.{DEVICEID}\_fresh_air                     | fan           | Fresh Air                  | 新风             |
| switch.{DEVICEID}\_aux_heating                | switch        | Aux Heating                | 电辅热           |
| switch.{DEVICEID}\_boost_mode                 | switch        | Boost Mode                 | 强劲模式         |
| switch.{DEVICEID}\_breezeless                 | switch        | Breezeless                 | 无风感           |
| switch.{DEVICEID}\_comfort_mode               | switch        | Comfort Mode               | 舒省模式         |
| switch.{DEVICEID}\_dry                        | switch        | Dry                        | 干燥             |
| switch.{DEVICEID}\_eco_mode                   | switch        | ECO Mode                   | ECO模式          |
| switch.{DEVICEID}\_indirect_wind              | switch        | Indirect Wind              | 防直吹           |
| switch.{DEVICEID}\_natural_wind               | switch        | Natural Wind               | 自然风           |
| switch.{DEVICEID}\_prompt_tone                | switch        | Prompt Tone                | 提示音           |
| switch.{DEVICEID}\_power                      | switch        | Power                      | 电源开关         |
| switch.{DEVICEID}\_screen_display             | switch        | Screen Display             | 屏幕显示         |
| switch.{DEVICEID}\_screen_display_alternate   | switch        | Screen Display Alternate   | 屏幕显示备用开关 |
| switch.{DEVICEID}\_smart_eye                  | switch        | Smart Eye                  | 智慧眼           |
| switch.{DEVICEID}\_swing_horizontal           | switch        | Swing Horizontal           | 水平摆风         |
| switch.{DEVICEID}\_swing_vertical             | switch        | Swing Vertical             | 垂直摆风         |
| switch.{DEVICEID}\_wind_lr_angle              | select        | Airflow Horizontal         | 水平出风         |
| switch.{DEVICEID}\_wind_ud_angle              | select        | Airflow Vertical           | 垂直出风         |
| switch.{DEVICEID}\_fan_speed                  | number        | Fan Speed Percent          | 风速百分比       |

## 内置新风系统

部分美的的"中央新风机"产品，其实使用了空调的协议。如果你的新风机被识别为空调，则只用在选项中勾选"Fresh Air"的fan实体，然后使用该fan实体控制新风机即可。

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                                                                                                                                                                                                                                                                     |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| device_id | 设备的编号(Device ID)                                                                                                                                                                                                                                                    |
| attribute | "aux_heating"<br/>"breezeless"<br/>"comfort_mode"<br/>"dry"<br/>"eco_mode"<br/>"indirect_wind"<br/>"natural_wind"<br/>"prompt_tone"<br/>"power"<br/>"screen_display"<br/>"screen_display_2"<br/>"smart_eye"<br/>"swing_horizontal"<br/>"swing_vertical"<br/>"turbo_mode" |
| value     | true 或 false                                                                                                                                                                                                                                                            |

| 名称      | 描述                  |
| --------- | --------------------- |
| device_id | 设备的编号(Device ID) |
| attribute | fan_speed             |
| value     | 范围为1-100, 或者auto |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: eco_mode
  value: true
```

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: fan_speed
  value: 65
```
