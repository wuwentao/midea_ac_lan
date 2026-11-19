# 加湿器

## 特性

- 支持运行模式
- 支持风扇模式设定
- 支持湿度设定
- 支持按设备协议自动匹配运行模式、风速和屏幕布局
- 支持 Lua `2024110101` 设备的湿帘风干功能

## 生成实体

### 默认生成实体

| 实体ID                            | 类型       | 描述       |
| --------------------------------- | ---------- | ---------- |
| humidifier.{DEVICEID}\_humidifier | humidifier | 加湿器实体 |

### 额外生成实体

| EntityID                               | 类型   | 名称                | 描述     |
| -------------------------------------- | ------ | ------------------- | -------- |
| sensor.{DEVICEID}\_current_humidity    | sensor | Current Humidity    | 当前湿度 |
| sensor.{DEVICEID}\_current_temperature | sensor | Current Temperature | 当前温度 |
| switch.{DEVICEID}\_disinfect           | switch | Disinfect           | 消毒开关 |
| switch.{DEVICEID}\_prompt_tone         | switch | Prompt Tone         | 提示音   |
| switch.{DEVICEID}\_power               | switch | Power               | 电源开关 |
| switch.{DEVICEID}\_wet_pad_dry         | switch | Wet Pad Drying      | 湿帘风干 |
| select.{DEVICEID}\_fan_speed           | select | Fan Speed           | 风速设定 |
| select.{DEVICEID}\_screen_display      | select | Screen Display      | 屏幕设定 |

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                                                        |
| --------- | ----------------------------------------------------------- |
| device_id | 设备的编号(Device ID)                                       |
| attribute | "disinfect"<br/>"prompt_tone"<br/>"power"<br/>"wet_pad_dry" |
| value     | true 或 false                                               |

| 名称      | 描述                                                            |
| --------- | --------------------------------------------------------------- |
| device_id | 设备的编号(Device ID)                                           |
| attribute | "fan_speed"                                                     |
| value     | "Lowest"<br/>"Low"<br/>"Medium"<br/>"High"<br/>"Auto"<br/>"Off" |

| 名称      | 描述                         |
| --------- | ---------------------------- |
| device_id | 设备的编号(Device ID)        |
| attribute | "screen_display"             |
| value     | "Bright"<br/>"Dim"<br/>"Off" |

可用运行模式、风速和屏幕选项取决于自动检测到的设备协议。Lua 25 设备提供实机验证过的
风速选项，但不提供 `Off` 风速；其屏幕选项为 `Bright`/`Off`，不提供 `Dim`。
Lua `2024110101` 设备提供
`Manual`/`Sleep`/`Moist skin`、`Low`/`Medium`/`High` 和
`Bright`/`Dim`/`Off`。

湿帘风干是可选的额外开关。只有 Lua `2024110101` 状态报文确认设备支持该功能后，
集成配置选项才会提供此开关。

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: prompt_tone
  value: true
```

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: fan_speed
  value: Medium
```
