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

### 温度调整步长

默认值：`0.5`

```json
{ "temperature_step": 1 }
```

### 温度范围

温控实体显示的最低/最高目标温度。默认情况下，若设备上报了温度能力（B5 报文）
则按其取值，否则回退为 16~30 °C。当设备未上报温度范围，或上报的范围不正确时，
可用以下选项手动覆盖（请通过美的 App 或遥控器确认正确的取值）。两个值均为可选。

```json
{ "min_temperature": 16, "max_temperature": 30 }
```

### 能力配置

设备支持的能力默认会从 B5 能力报文中自动识别。自定义配置可以从两个层面覆盖
自动识别的结果：第一类是强制开启或关闭某个能力的总开关，第二类是定义某些
能力对应的取值或范围，决定 Home Assistant 中显示哪些控制项。

#### 能力总开关

使用 `capabilities` 自定义键可以强制开启 B5 能力报文中没有上报的功能，或强制
关闭设备错误上报的功能。这些值会合并到 `midea-lan` 的能力表中，并且会强制
覆盖设备回复的结果：优先级为 自定义 > B5 能力 > 默认值。

```json
{ "capabilities": { "self_clean": true, "rate_select": 2 } }
```

普通开关类能力使用 `true` 或 `false` 开启/关闭。像 `rate_select` 这样表示档位
或级别数量的能力使用整数；使用 `false` 或 `0` 可关闭该能力。

示例：

```json
{ "capabilities": { "self_clean": true } }
```

```json
{ "capabilities": { "self_clean": false } }
```

```json
{ "capabilities": { "rate_select": 2 } }
```

```json
{ "capabilities": { "rate_select": false } }
```

```json
{ "capabilities": { "error_code": true, "out_silent": true, "sound": true } }
```

```json
{ "capabilities": { "error_code": false, "out_silent": false, "sound": false } }
```

建议只在已经通过美的 App 或遥控器确认设备确实支持该功能时开启能力。若物理
设备并不支持，被强制开启的相关实体可能保持不可用、未知，或无法更新。

#### 能力取值和范围

运行模式、风速、摆风和预设会根据设备的 B5 能力上报自动识别（例如仅制冷的移动空调
只显示 `cool`/`dry`/`fan_only`、`low`/`high`/`auto` 风速，无摆风，并保留
`comfort`/`sleep` 预设以及 B5 上报的其它预设）。如果尚未解析到能力映射，默认会显示
全部预设。

部分能力无法推断（旧版库，或协议本身不声明的功能，如 `comfort`/`sleep` 预设），
可通过自定义覆盖（请通过美的 App 或遥控器确认真实取值）：

```json
{
  "swing": false,
  "hvac_modes": ["off", "cool", "dry", "fan_only"],
  "preset_modes": ["none"],
  "fan_modes": ["silent", "low", "medium", "high", "auto"]
}
```

- `swing`（布尔）：强制开启/关闭摆风控制。
- `hvac_modes`（列表）：限制显示的模式，`off` 始终保留。可选值：`off`、`auto`、`cool`、`dry`、`heat`、`fan_only`。
- `preset_modes`（列表）：限制预设，`none` 始终保留；用 `["none"]` 可完全移除预设控制。可选值：`none`、`comfort`、`eco`、`boost`、`sleep`、`away`。
- `fan_modes`（列表）：限制显示的风速。可选值：`silent`、`low`、`medium`、`high`、`full`、`auto`。

优先级为 自定义 > B5 能力 > 默认值。所有键均为可选；省略则使用自动识别的集合。

### 空调功耗分析方法

空调功耗数据有 5 种不同的解析方式，但无法预先判断哪一种适合你的设备。如果
功率或能耗数据看起来不正确，可以尝试切换其它方法。

默认值：`1`

支持的值：`1`（二进制）、`2`（BCD）、`3`（100 进制）、`12`（类似 `2`，但能耗
值额外除以 `10`）、`101`（能耗值使用 BCD，实时功率使用二进制）。

```json
{ "power_analysis_method": 2 }
```

已知设置：

| 设备                       | 模式 |
| :------------------------- | ---: |
| Midea PortaSplit           |   12 |
| Midea 00000Q1D subtype 524 |  101 |

## 生成实体

### 默认生成实体

| 实体ID                      | 类型    | 描述       |
| --------------------------- | ------- | ---------- |
| climate.{DEVICEID}\_climate | climate | 恒温器实体 |

### 额外生成实体

| EntityID                                       | 类型          | 名称                             | 描述              |
| ---------------------------------------------- | ------------- | -------------------------------- | ----------------- |
| sensor.{DEVICEID}\_full_dust                   | binary_sensor | Full of Dust                     | 尘满              |
| sensor.{DEVICEID}\_indoor_humidity             | sensor        | Indoor humidity                  | 湿度              |
| sensor.{DEVICEID}\_indoor_temperature          | sensor        | Indoor Temperature               | 室内温度          |
| sensor.{DEVICEID}\_outdoor_temperature         | sensor        | Outdoor Temperature              | 室外机温度        |
| sensor.{DEVICEID}\_total_energy_consumption    | sensor        | Total Energy Consumption         | 总能耗            |
| sensor.{DEVICEID}\_current_energy_consumption  | sensor        | Current Energy Consumption       | 当前能耗          |
| sensor.{DEVICEID}\_realtime_power              | sensor        | Realtime Power                   | 实时功率          |
| sensor.{DEVICEID}\_compressor_frequency        | sensor        | Compressor Frequency             | 压缩机频率        |
| sensor.{DEVICEID}\_target_compressor_frequency | sensor        | Target Compressor Frequency      | 压缩机目标频率    |
| sensor.{DEVICEID}\_compressor_current          | sensor        | Compressor Current               | 压缩机电流        |
| sensor.{DEVICEID}\_compressor_voltage          | sensor        | Compressor Voltage               | 压缩机电压        |
| sensor.{DEVICEID}\_compressor_power            | sensor        | Compressor Power                 | 压缩机实时功率    |
| sensor.{DEVICEID}\_indoor_ambient_temperature  | sensor        | Indoor Ambient Temperature (T1)  | 室内环境温度 (T1) |
| sensor.{DEVICEID}\_indoor_coil_temperature     | sensor        | Indoor Coil Temperature (T2)     | 室内盘管温度 (T2) |
| sensor.{DEVICEID}\_outdoor_coil_temperature    | sensor        | Outdoor Coil Temperature (T3)    | 室外盘管温度 (T3) |
| sensor.{DEVICEID}\_outdoor_ambient_temperature | sensor        | Outdoor Ambient Temperature (T4) | 室外环境温度 (T4) |
| sensor.{DEVICEID}\_discharge_pipe_temperature  | sensor        | Discharge Pipe Temperature (TP)  | 排气管温度 (TP)   |
| sensor.{DEVICEID}\_indoor_fan_speed            | sensor        | Indoor Fan Speed                 | 内风机转速        |
| sensor.{DEVICEID}\_target_indoor_fan_speed     | sensor        | Target Indoor Fan Speed          | 内风机目标转速    |
| sensor.{DEVICEID}\_water_pump_running          | binary_sensor | Water Pump Running               | 水泵运行          |
| fan.{DEVICEID}\_fresh_air                      | fan           | Fresh Air                        | 新风              |
| fan.{DEVICEID}\_fresh_air_exhaust              | fan           | Fresh Air Exhaust                | 排风              |
| select.{DEVICEID}\_fresh_air_mode              | select        | Fresh Air Speed                  | 新风风速          |
| select.{DEVICEID}\_fresh_air_exhaust_mode      | select        | Fresh Air Exhaust Speed          | 排风风速          |
| switch.{DEVICEID}\_aux_heating                 | switch        | Aux Heating                      | 电辅热            |
| switch.{DEVICEID}\_boost_mode                  | switch        | Boost Mode                       | 强劲模式          |
| switch.{DEVICEID}\_breezeless                  | switch        | Breezeless                       | 无风感            |
| switch.{DEVICEID}\_comfort_mode                | switch        | Comfort Mode                     | 舒省模式          |
| switch.{DEVICEID}\_dry                         | switch        | Dry                              | 干燥              |
| switch.{DEVICEID}\_eco_mode                    | switch        | ECO Mode                         | ECO模式           |
| switch.{DEVICEID}\_ieco                        | switch        | iECO                             | iECO 节能         |
| switch.{DEVICEID}\_indirect_wind               | switch        | Indirect Wind                    | 防直吹            |
| switch.{DEVICEID}\_natural_wind                | switch        | Natural Wind                     | 自然风            |
| switch.{DEVICEID}\_prompt_tone                 | switch        | Prompt Tone                      | 提示音            |
| switch.{DEVICEID}\_power                       | switch        | Power                            | 电源开关          |
| switch.{DEVICEID}\_screen_display              | switch        | Screen Display                   | 屏幕显示          |
| switch.{DEVICEID}\_screen_display_alternate    | switch        | Screen Display Alternate         | 屏幕显示备用开关  |
| switch.{DEVICEID}\_smart_eye                   | switch        | Smart Eye                        | 智慧眼            |
| switch.{DEVICEID}\_swing_horizontal            | switch        | Swing Horizontal                 | 水平摆风          |
| switch.{DEVICEID}\_swing_vertical              | switch        | Swing Vertical                   | 垂直摆风          |
| switch.{DEVICEID}\_wind_lr_angle               | select        | Airflow Horizontal               | 水平出风          |
| switch.{DEVICEID}\_wind_ud_angle               | select        | Airflow Vertical                 | 垂直出风          |
| switch.{DEVICEID}\_rate_select                 | select        | Power Rate Limit                 | 功率限制          |
| switch.{DEVICEID}\_fan_speed                   | number        | Fan Speed Percent                | 风速百分比        |

服务诊断实体为可选实体。如果设备不返回相应的美的分组数据，这些实体可能保持未知状态。

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
