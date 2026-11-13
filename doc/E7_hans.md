# 蒸制烹饪电器

蒸制烹饪电器 (设备类型 0xE7)，与 0xEB 系列为同类设备。

## 特性

- 支持工作状态 / 功能 / 火力档位控制
- 支持预约与定时设置
- 上报运行时间、剩余时间与工作阶段

## 自定义

无自定义

## 实体

### 默认实体

无默认实体

### 扩展传感器

| 实体ID                               | 类型   | 描述     |
| ------------------------------------ | ------ | -------- |
| number.{DEVICEID}\_work_status       | number | 工作状态 |
| number.{DEVICEID}\_function_no       | number | 功能编号 |
| number.{DEVICEID}\_fire_level        | number | 火力档位 |
| number.{DEVICEID}\_time_reserve_hr   | number | 预约小时 |
| number.{DEVICEID}\_time_reserve_min  | number | 预约分钟 |
| number.{DEVICEID}\_definite_time_hr  | number | 定时小时 |
| number.{DEVICEID}\_definite_time_min | number | 定时分钟 |
| sensor.{DEVICEID}\_time_running_hr   | sensor | 运行小时 |
| sensor.{DEVICEID}\_time_running_min  | sensor | 运行分钟 |
| sensor.{DEVICEID}\_time_surplus_hr   | sensor | 剩余小时 |
| sensor.{DEVICEID}\_time_surplus_min  | sensor | 剩余分钟 |
| sensor.{DEVICEID}\_work_stage        | sensor | 工作阶段 |
| sensor.{DEVICEID}\_error_code        | sensor | 错误代码 |

`work_status` 取值为 0–5 的原始设备状态码。协议仅命名了 `5`（`5` = 关机 /
`BYTE_STATUS_POWER_OFF`）；`0`–`4` 为协议未逐一命名的原始运行阶段码。

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性。服务数据:

| 名称      | 描述                                                                                                                                               |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| device_id | 设备的 Appliance code (设备 ID)                                                                                                                    |
| attribute | "work_status"<br />"function_no"<br />"fire_level"<br />"time_reserve_hr"<br />"time_reserve_min"<br />"definite_time_hr"<br />"definite_time_min" |
| value     | 位于实体范围内的整数                                                                                                                               |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: fire_level
  value: 10
```
