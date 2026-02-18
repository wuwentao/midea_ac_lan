# 空气能热水器

## 自定义

- 支持温度设定

设置温度调整步长 (默认为1).

```json
{ "temperature_step": 0.5 }
```

- 设置温度单位处理的协议版本

某些空气能热水器型号可能会显示错误的温度单位（应该显示摄氏度却显示华氏度，或反之）。这是由不同型号使用的不同协议版本造成的。如果遇到此问题，可以手动设置协议版本：

```json
{ "lua_protocol": "new" }
```

`lua_protocol` 设置可以设为：
- `auto`（默认）- 自动检测协议版本
- `new` - 使用新版协议（如果温度单位错误，请先尝试此选项）
- `old` - 使用旧版协议

**注意：** 此设置专门影响温度单位的解释方式。如果您的设备显示错误的温度单位（例如，应该是60°C却显示为140°F），请尝试将此项设置为 `"new"` 或 `"old"` 来修复问题。

## 生成实体

### 默认生成实体

| 实体ID                                | 类型         | 描述       |
| ------------------------------------- | ------------ | ---------- |
| water_heater.{DEVICEID}\_water_heater | water_heater | 热水器实体 |

### Extra entities

| EntityID                                    | 类型          | 名称                     | 描述           |
| ------------------------------------------- | ------------- | ------------------------ | -------------- |
| binary_sensor.{DEVICEID}\_compressor_status | binary_sensor | Compressor Status        | 压缩机状态     |
| sensor.{DEVICEID}\_compressor_temperature   | sensor        | Compressor Temperature   | 压缩机温度     |
| sensor.{DEVICEID}\_condenser_temperature    | sensor        | Condenser Temperature    | 冷凝器温度     |
| sensor.{DEVICEID}\_outdoor_temperature      | sensor        | Outdoor Temperature      | 室外温度       |
| sensor.{DEVICEID}\_water_level              | sensor        | Water Level              | 水位           |
| switch.{DEVICEID}\_disinfect                | switch        | Disinfect                | 消毒           |
| sensor.{DEVICEID}\_elec_heat                | sensor        | Electric Heat            | 电加热         |
| binary_sensor.{DEVICEID}\_top_elec_heat     | binary_sensor | Top Electric Heat        | 上部电加热     |
| binary_sensor.{DEVICEID}\_bottom_elec_heat  | binary_sensor | Bottom Electric Heat     | 底部电加热     |
| sensor.{DEVICEID}\_water_pump               | sensor        | Water Pump               | 水泵           |
| sensor.{DEVICEID}\_four_way                 | sensor        | Four Way Valve           | 四通阀         |
| sensor.{DEVICEID}\_back_water               | sensor        | Back Water               | 回水           |
| sensor.{DEVICEID}\_sterilize                | sensor        | Sterilize                | 杀菌           |
| sensor.{DEVICEID}\_top_temperature          | sensor        | Top Temperature          | 顶部温度       |
| sensor.{DEVICEID}\_bottom_temperature       | sensor        | Bottom Temperature       | 底部温度       |
| sensor.{DEVICEID}\_wind                     | sensor        | Wind                     | 风             |
| binary_sensor.{DEVICEID}\_smart_grid        | binary_sensor | Smart Grid               | 智能电网       |
| binary_sensor.{DEVICEID}\_multi_terminal    | binary_sensor | Multi Terminal           | 多终端         |
| binary_sensor.{DEVICEID}\_mute_effect       | binary_sensor | Mute Effect              | 静音效果       |
| binary_sensor.{DEVICEID}\_mute_status       | binary_sensor | Mute Status              | 静音状态       |
| sensor.{DEVICEID}\_error_code               | sensor        | Error Code               | 错误代码       |
| sensor.{DEVICEID}\_typeinfo                 | sensor        | Type Info                | 类型信息       |
| switch.{DEVICEID}\_power                    | switch        | Power                    | 电源           |

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                  |
| --------- | --------------------- |
| device_id | 设备的编号(Device ID) |
| attribute | "power"               |
| value     | true 或 false         |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: false
```
