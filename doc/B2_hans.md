# 蒸箱

嵌入式蒸箱 / 蒸汽炉 (设备类型 0xB2)。

## 特性

- 支持工作状态 (待机 / 工作 / 暂停 / 已完成 / 预约 / 节能)
- 支持烹饪模式 (16 种)
- 支持定时小时 / 分钟
- 支持温度
- 支持童锁
- 上报门、水箱、蒸箱 (内腔) 状态

## 自定义

无自定义

## 实体

### 默认实体

无默认实体

### 扩展传感器

| 实体ID                         | 类型   | 描述                   |
| ------------------------------ | ------ | ---------------------- |
| select.{DEVICEID}\_work_status | select | 工作状态               |
| select.{DEVICEID}\_work_mode   | select | 烹饪模式               |
| number.{DEVICEID}\_work_hour   | number | 定时小时 (0-9)         |
| number.{DEVICEID}\_work_minute | number | 定时分钟 (0-59)        |
| number.{DEVICEID}\_temperature | number | 目标温度 (50-100°C)    |
| switch.{DEVICEID}\_lock        | switch | 童锁                   |
| sensor.{DEVICEID}\_door_state  | sensor | 门状态 (关闭 / 打开)   |
| sensor.{DEVICEID}\_water_state | sensor | 水箱状态 (已满 / 缺水) |
| sensor.{DEVICEID}\_box_state   | sensor | 蒸箱状态 (放入 / 取出) |

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性。服务数据:

| 名称      | 描述                                                                                              |
| --------- | ------------------------------------------------------------------------------------------------- |
| device_id | 设备的 Appliance code (设备 ID)                                                                   |
| attribute | "work_status"<br />"work_mode"<br />"work_hour"<br />"work_minute"<br />"temperature"<br />"lock" |
| value     | 参考上方实体的选项 / 取值范围                                                                     |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: temperature
  value: 100
```
