# 面包机

自动面包机 (设备类型 0xE9)。

## 特性

- 支持工作状态、面包重量、烤色和投料控制
- 支持烘烤温度设置
- 支持烹饪和预约定时
- 上报工作阶段、底部温度和工作 / 保温时间
- 上报响应类型和错误代码

## 自定义

无自定义

## 实体

### 默认实体

无默认实体

### 扩展实体

| 实体ID                                 | 类型   | 描述     |
| -------------------------------------- | ------ | -------- |
| number.{DEVICEID}\_e9_work_status      | number | 工作状态 |
| number.{DEVICEID}\_e9_volume           | number | 面包重量 |
| number.{DEVICEID}\_e9_color            | number | 烤色     |
| number.{DEVICEID}\_e9_dosing           | number | 投料     |
| number.{DEVICEID}\_e9_bake_temperature | number | 烘烤温度 |
| number.{DEVICEID}\_e9_time_cuisine_hr  | number | 烹饪小时 |
| number.{DEVICEID}\_e9_time_cuisine_min | number | 烹饪分钟 |
| number.{DEVICEID}\_e9_time_reserve_hr  | number | 预约小时 |
| number.{DEVICEID}\_e9_time_reserve_min | number | 预约分钟 |
| number.{DEVICEID}\_e9_control_cmd_code | number | 命令码   |
| sensor.{DEVICEID}\_e9_response_type    | sensor | 响应类型 |
| sensor.{DEVICEID}\_e9_work_stage       | sensor | 工作阶段 |
| sensor.{DEVICEID}\_bottom_temperature  | sensor | 底部温度 |
| sensor.{DEVICEID}\_e9_time_work_hr     | sensor | 工作小时 |
| sensor.{DEVICEID}\_e9_time_work_min    | sensor | 工作分钟 |
| sensor.{DEVICEID}\_e9_time_warm_hr     | sensor | 保温小时 |
| sensor.{DEVICEID}\_e9_time_warm_min    | sensor | 保温分钟 |
| sensor.{DEVICEID}\_e9_product_volume   | sensor | 成品重量 |
| sensor.{DEVICEID}\_error_code          | sensor | 错误代码 |

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性。服务数据:

| 名称      | 描述                                                                                                                                                                                                 |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| device_id | 设备的 Appliance code (设备 ID)                                                                                                                                                                      |
| attribute | "work_status"<br />"volume"<br />"color"<br />"dosing"<br />"bake_temperature"<br />"time_cuisine_hr"<br />"time_cuisine_min"<br />"time_reserve_hr"<br />"time_reserve_min"<br />"control_cmd_code" |
| value     | 属性范围内的整数                                                                                                                                                                                     |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: bake_temperature
  value: 180
```
