# 燃气热水器

## 特性

- 支持温度设定

## 自定义

- 设置热水器温度基数为整度还是半度 (false 为整度 true 为半度, 默认为 false)

  如果你的热水器显示的温度为实际温度的两倍，请将该值设为true。

```json
{ "precision_halves": true }
```

- 设置温度调整步长(默认为1).

```json
{ "temperature_step": 0.5 }
```

## 生成实体

### 默认生成实体

| 实体ID                                | 类型         | 描述       |
| ------------------------------------- | ------------ | ---------- |
| water_heater.{DEVICEID}\_water_heater | water_heater | 热水器实体 |

### 额外生成实体

| 实体ID                                    | 类型          | 名称                    | 描述         |
| ----------------------------------------- | ------------- | ----------------------- | ------------ |
| binary_sensor.{DEVICEID}\_burning_state   | binary_sensor | Burning State           | 燃烧状态     |
| binary_sensor.{DEVICEID}\_protection      | binary_sensor | Protection              | 安全防护     |
| sensor.{DEVICEID}\_current_temperature    | sensor        | Current Temperature     | 温度         |
| switch.{DEVICEID}\_power                  | switch        | Power                   | 电源开关     |
| switch.{DEVICEID}\_smart_volume           | switch        | Smart Volume            | 智能变容     |
| switch.{DEVICEID}\_zero_cold_water        | switch        | Zero Cold Water         | 零冷水       |
| switch.{DEVICEID}\_zero_cold_pulse        | switch        | Zero Cold Water (Pulse) | 零冷水(点动) |
| sensor.{DEVICEID}\_water_usage_daily      | sensor        | Daily Water Usage       | 日用水量     |
| sensor.{DEVICEID}\_gas_usage_daily        | sensor        | Daily Gas Usage         | 日用气量     |
| sensor.{DEVICEID}\_water_usage_monthly    | sensor        | Monthly Water Usage     | 本月用水量   |
| sensor.{DEVICEID}\_gas_usage_monthly      | sensor        | Monthly Gas Usage       | 本月用气量   |
| sensor.{DEVICEID}\_water_usage_last_month | sensor        | Last Month Water Usage  | 上月用水量   |
| sensor.{DEVICEID}\_gas_usage_last_month   | sensor        | Last Month Gas Usage    | 上月用气量   |

### 用水量/用气量统计（可选）

水量和气量传感器并非来自设备本身：E3 燃气热水器只把用量上报到美的云
（即官方 App 中展示的日报表）。使用方法：

1. 在设备的集成选项中的 **额外传感器** 里勾选这些传感器。
2. 在同一选项对话框中填写 **美的云账号**、**密码** 和 **云服务器**，
   必须是设备在美的 App 中注册的个人账号；预置账号无法使用，它看不到
   你的设备。云服务器仅提供支持报表的 `美的美居` 和 `SmartHome`，其他
   云不提供用量报表。

云端每天写入一次报表，集成每 6 小时检查一次。`日` 为最近一个完整天数
（见传感器的 `report_date` 属性），`本月` 为当月至今，`上月` 为上一个
自然月。水量单位为升，气量单位为立方米。

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                                                                                        |
| --------- | ------------------------------------------------------------------------------------------- |
| device_id | 设备的编号(Device ID)                                                                       |
| attribute | "energy_saving"<br/>"power"<br />"smart_volume"<br/>"zero_cold_water"<br/>"zero_cold_pulse" |
| value     | true or false                                                                               |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: smart_volume
  value: true
```
