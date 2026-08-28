# 空气能热水器

## 自定义

扩展 CD 热水器可根据设备上报的能力提供即时/自动消毒、消毒温度、最高温度、
维护提醒、定时器/周计划、Demand Response、热回收及可选运行模式。未上报的属性
不会出现在集成的可选实体列表中，因此旧设备继续保持原有行为。

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

| EntityID                                    | 类型          | 名称                   | 描述       |
| ------------------------------------------- | ------------- | ---------------------- | ---------- |
| binary_sensor.{DEVICEID}\_compressor_status | binary_sensor | Compressor Status      | 压缩机状态 |
| sensor.{DEVICEID}\_compressor_temperature   | sensor        | Compressor Temperature | 压缩机温度 |
| sensor.{DEVICEID}\_condenser_temperature    | sensor        | Condenser Temperature  | 冷凝器温度 |
| sensor.{DEVICEID}\_outdoor_temperature      | sensor        | Outdoor Temperature    | 室外温度   |
| sensor.{DEVICEID}\_water_level              | sensor        | Water Level            | 水位       |
| switch.{DEVICEID}\_disinfect                | switch        | Disinfect              | 消毒       |
| sensor.{DEVICEID}\_elec_heat                | sensor        | Electric Heat          | 电加热     |
| binary_sensor.{DEVICEID}\_top_elec_heat     | binary_sensor | Top Electric Heat      | 上部电加热 |
| binary_sensor.{DEVICEID}\_bottom_elec_heat  | binary_sensor | Bottom Electric Heat   | 底部电加热 |
| sensor.{DEVICEID}\_water_pump               | sensor        | Water Pump             | 水泵       |
| sensor.{DEVICEID}\_four_way                 | sensor        | Four Way Valve         | 四通阀     |
| sensor.{DEVICEID}\_back_water               | sensor        | Back Water             | 回水       |
| sensor.{DEVICEID}\_sterilize                | sensor        | Sterilize              | 杀菌       |
| sensor.{DEVICEID}\_top_temperature          | sensor        | Top Temperature        | 顶部温度   |
| sensor.{DEVICEID}\_bottom_temperature       | sensor        | Bottom Temperature     | 底部温度   |
| sensor.{DEVICEID}\_wind                     | sensor        | Wind                   | 风         |
| binary_sensor.{DEVICEID}\_smart_grid        | binary_sensor | Smart Grid             | 智能电网   |
| binary_sensor.{DEVICEID}\_multi_terminal    | binary_sensor | Multi Terminal         | 多终端     |
| binary_sensor.{DEVICEID}\_mute_effect       | binary_sensor | Mute Effect            | 静音效果   |
| binary_sensor.{DEVICEID}\_mute_status       | binary_sensor | Mute Status            | 静音状态   |
| sensor.{DEVICEID}\_error_code               | sensor        | Error Code             | 错误代码   |
| sensor.{DEVICEID}\_typeinfo                 | sensor        | Type Info              | 类型信息   |
| switch.{DEVICEID}\_power                    | switch        | Power                  | 电源       |

### 扩展 CD 实体

仅当设备上报对应属性时，以下实体才会出现在可选实体中。`Schedule Mode` 的值
`0` 表示关闭，`1` 表示每日定时器，`2` 表示周计划。

| EntityID                                           | 类型          | 名称                           |
| -------------------------------------------------- | ------------- | ------------------------------ |
| switch.{DEVICEID}\_disinfect                       | switch        | Immediate Disinfection         |
| number.{DEVICEID}\_schedule_mode                   | number        | Schedule Mode                  |
| number.{DEVICEID}\_max_temperature                 | number        | Maximum Target Temperature     |
| number.{DEVICEID}\_disinfection_temperature        | number        | Disinfection Temperature       |
| switch.{DEVICEID}\_maintenance_reminder            | switch        | Maintenance Reminder           |
| binary_sensor.{DEVICEID}\_dr_enable                | binary_sensor | Demand Response                |
| binary_sensor.{DEVICEID}\_electric_rod_exception   | binary_sensor | Electric Heater Fault          |
| sensor.{DEVICEID}\_remaining_hot_water_max         | sensor        | Maximum Remaining Hot Water    |
| sensor.{DEVICEID}\_force_e_heating_status          | sensor        | Forced Electric Heating Status |
| binary_sensor.{DEVICEID}\_heat_recovery_status     | binary_sensor | Heat Recovery                  |
| binary_sensor.{DEVICEID}\_new_version_water_heater | binary_sensor | Extended Protocol              |

温度上下限、假期范围、定时步长及所有 capability 标志也作为可选诊断实体提供。
每日和每周计划是结构化映射。目前无法通过 `midea_ac_lan.set_attribute`
服务写入，因为该服务架构只接受标量值。

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
