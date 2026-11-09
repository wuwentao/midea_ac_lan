# 保温烹饪器具

蒸汽 / 保温烹饪器具 (设备类型 0xEB)。

## 特性

- 支持功能选择
- 支持工作状态控制
- 支持火力档位控制
- 支持预约定时
- 支持倒计时定时
- 上报运行 / 剩余时间与工作阶段

## 自定义

无自定义

## 实体

### 默认实体

无默认实体

### 扩展实体

下表同时包含 number 控制实体(可写)与 sensor 传感器实体(只读)。

| 实体ID                                  | 类型   | 描述     |
| --------------------------------------- | ------ | -------- |
| number.{DEVICEID}\_eb_function_no       | number | 功能编号 |
| number.{DEVICEID}\_eb_work_status       | number | 工作状态 |
| number.{DEVICEID}\_eb_fire_level        | number | 火力档位 |
| number.{DEVICEID}\_eb_time_reserve_hr   | number | 预约小时 |
| number.{DEVICEID}\_eb_time_reserve_min  | number | 预约分钟 |
| number.{DEVICEID}\_eb_definite_time_hr  | number | 定时小时 |
| number.{DEVICEID}\_eb_definite_time_min | number | 定时分钟 |
| sensor.{DEVICEID}\_eb_time_running_hr   | sensor | 运行小时 |
| sensor.{DEVICEID}\_eb_time_running_min  | sensor | 运行分钟 |
| sensor.{DEVICEID}\_eb_time_surplus_hr   | sensor | 剩余小时 |
| sensor.{DEVICEID}\_eb_time_surplus_min  | sensor | 剩余分钟 |
| sensor.{DEVICEID}\_eb_work_stage        | sensor | 工作阶段 |
| sensor.{DEVICEID}\_error_code           | sensor | 错误代码 |

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性。服务数据:

| 名称      | 描述                                                                                                                                               |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| device_id | 设备的 Appliance code (设备 ID)                                                                                                                    |
| attribute | "function_no"<br />"work_status"<br />"fire_level"<br />"time_reserve_hr"<br />"time_reserve_min"<br />"definite_time_hr"<br />"definite_time_min" |
| value     | 属性范围内的整数                                                                                                                                   |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: fire_level
  value: 5
```
