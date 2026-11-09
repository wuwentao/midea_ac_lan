# 微蒸烤一体机

带蒸汽和烘烤功能的微波炉 (设备类型 0x9A)。

## 特性

- 支持开关
- 支持童锁
- 支持炉灯
- 支持工作状态: 可写选择 (取消 / 工作 / 暂停) 以及上报所有状态的只读传感器 (取消 / 工作 / 暂停 / 结束 / 预约)
- 支持模式 (保温、烘烤、解冻、对流、发酵、披萨、微波等)
- 支持温度设置
- 支持烹饪定时 (小时 / 分钟 / 秒)
- 支持微波功率
- 支持食物重量
- 上报当前温度
- 上报错误代码

## 自定义

无自定义

## 实体

### 默认实体

| 实体ID                   | 类型   | 描述     |
| ------------------------ | ------ | -------- |
| switch.{DEVICEID}\_power | switch | 开关实体 |

### 扩展实体

| 实体ID                                 | 类型   | 描述                                              |
| -------------------------------------- | ------ | ------------------------------------------------- |
| switch.{DEVICEID}\_lock                | switch | 童锁                                              |
| switch.{DEVICEID}\_oven_light          | switch | 炉灯                                              |
| select.{DEVICEID}\_work_status_select  | select | 工作状态 (可写: 取消 / 工作 / 暂停)               |
| sensor.{DEVICEID}\_oven_work_status    | sensor | 工作状态 (上报: 取消 / 工作 / 暂停 / 结束 / 预约) |
| select.{DEVICEID}\_oven_mode           | select | 烹饪模式                                          |
| number.{DEVICEID}\_oven_temperature    | number | 目标温度 (°C)                                     |
| number.{DEVICEID}\_oven_hour           | number | 烹饪小时                                          |
| number.{DEVICEID}\_oven_minute         | number | 烹饪分钟                                          |
| number.{DEVICEID}\_oven_second         | number | 烹饪秒                                            |
| number.{DEVICEID}\_oven_watt           | number | 微波功率                                          |
| number.{DEVICEID}\_oven_weight         | number | 食物重量 (g)                                      |
| sensor.{DEVICEID}\_current_temperature | sensor | 当前温度                                          |
| sensor.{DEVICEID}\_error_code          | sensor | 错误代码                                          |

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性。服务数据:

| 名称      | 描述                                                                                                                                                          |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| device_id | 设备的 Appliance code (设备 ID)                                                                                                                               |
| attribute | "power"<br />"lock"<br />"furnace_light"<br />"work_status"<br />"mode"<br />"temperature"<br />"hour"<br />"minutes"<br />"second"<br />"watt"<br />"weight" |
| value     | 要设置的值                                                                                                                                                    |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: temperature
  value: 180
```
