# 饮品机

饮品 / 冲饮机 (设备类型 0xEF)。

## 特性

- 支持预约和保温开关
- 支持饮品类型选择 (热饮 / 温饮)
- 支持设置温度以及预约 / 保温定时
- 上报工作状态、进程状态、当前温度和错误代码

## 自定义

无自定义

## 实体

### 默认实体

无默认实体

### 扩展传感器

| 实体ID                                    | 类型   | 描述     |
| ----------------------------------------- | ------ | -------- |
| switch.{DEVICEID}\_ef_reserve             | switch | 预约     |
| switch.{DEVICEID}\_ef_warm                | switch | 保温     |
| select.{DEVICEID}\_ef_drink_style         | select | 饮品类型 |
| number.{DEVICEID}\_ef_temperature_setting | number | 设置温度 |
| number.{DEVICEID}\_ef_time_reserve_hr     | number | 预约小时 |
| number.{DEVICEID}\_ef_time_reserve_min    | number | 预约分钟 |
| number.{DEVICEID}\_ef_time_warm_hr        | number | 保温小时 |
| number.{DEVICEID}\_ef_time_warm_min       | number | 保温分钟 |
| number.{DEVICEID}\_ef_cmd_code            | number | 命令码   |
| number.{DEVICEID}\_ef_cmd_id              | number | 命令 ID  |
| sensor.{DEVICEID}\_ef_response_type       | sensor | 响应     |
| sensor.{DEVICEID}\_ef_work_status         | sensor | 工作状态 |
| sensor.{DEVICEID}\_ef_work_step           | sensor | 工作步骤 |
| sensor.{DEVICEID}\_ef_process_status      | sensor | 进程状态 |
| sensor.{DEVICEID}\_ef_time_work_hr        | sensor | 工作小时 |
| sensor.{DEVICEID}\_ef_time_work_min       | sensor | 工作分钟 |
| sensor.{DEVICEID}\_ef_time_max            | sensor | 最大时间 |
| sensor.{DEVICEID}\_ef_temperature_current | sensor | 当前温度 |
| sensor.{DEVICEID}\_error_code             | sensor | 错误代码 |

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性。服务数据:

| 名称      | 描述                                                                                                                                                                                      |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| device_id | 设备的 Appliance code (设备 ID)                                                                                                                                                           |
| attribute | "reserve"<br />"warm"<br />"drink_style"<br />"temperature_setting"<br />"time_reserve_hr"<br />"time_reserve_min"<br />"time_warm_hr"<br />"time_warm_min"<br />"cmd_code"<br />"cmd_id" |
| value     | reserve/warm 为 true/false; drink_style 为 "hot_drink"/"warm_drink"; 数值属性为范围内的整数                                                                                               |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: drink_style
  value: hot_drink
```
