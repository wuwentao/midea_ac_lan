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

| 实体ID                                  | 类型          | 名称                    | 描述         |
| --------------------------------------- | ------------- | ----------------------- | ------------ |
| binary_sensor.{DEVICEID}\_burning_state | binary_sensor | Burning State           | 燃烧状态     |
| binary_sensor.{DEVICEID}\_protection    | binary_sensor | Protection              | 安全防护     |
| sensor.{DEVICEID}\_current_temperature  | sensor        | Current Temperature     | 温度         |
| switch.{DEVICEID}\_power                | switch        | Power                   | 电源开关     |
| switch.{DEVICEID}\_smart_volume         | switch        | Smart Volume            | 智能变容     |
| switch.{DEVICEID}\_zero_cold_water      | switch        | Zero Cold Water         | 零冷水       |
| switch.{DEVICEID}\_zero_cold_pulse      | switch        | Zero Cold Water (Pulse) | 零冷水(点动) |

## 云端用量统计

本地协议不上报用水量和用气量，且并非所有 E3 机型都有云端用量报表。如需使用，请打开
`设置 -> 设备与服务 -> Midea AC LAN -> 设备 -> 配置`，启用**云端用量统计**，并填写
该设备所绑定的美居账号（手机号/邮箱）和密码。集成随后会调用官方 App 使用的同一个
`dayReportV2` 用量报表接口，并生成以下实体：

| 实体ID                                          | 类型   | 单位 | 描述                 |
| ----------------------------------------------- | ------ | ---- | -------------------- |
| sensor.{DEVICEID}\_cloud_water_usage_daily      | sensor | L    | 最近一个完整日的用水量 |
| sensor.{DEVICEID}\_cloud_gas_usage_daily        | sensor | m³   | 最近一个完整日的用气量 |
| sensor.{DEVICEID}\_cloud_duration_daily         | sensor | min  | 最近一个完整日的用热时长 |
| sensor.{DEVICEID}\_cloud_water_usage_monthly    | sensor | L    | 本月累计用水量        |
| sensor.{DEVICEID}\_cloud_gas_usage_monthly      | sensor | m³   | 本月累计用气量        |

说明

- 该功能默认关闭，仅在启用后才会创建上述实体；本地实体不需要美居账号。
- 凭据来自`配置`对话框或本地设备 JSON（`.storage/midea_ac_lan/<设备ID>.json`）：
  既可以是美居云端 `cloud_access_token`（直接使用），也可以是
  `cloud_account` + `cloud_password`（可选 `cloud_server`）用于自动登录刷新 token。
  该 JSON 中的设备 `token`/`key` 是局域网凭据，云端报表接口不接受。
- 报表由云端每天生成一次，因此日统计为“最近一个完整日”的数据，具体日期见
  `report_date` 属性；云端发布后一小时内更新。
- 月统计为 `total` 计量，每月初重置；上月数值见 `last_month` 属性。
- 云端 token 有效期很短，集成会自动重新登录，因此必须保存账号。

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
